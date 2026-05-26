import math
import itertools as it
import functools as ft
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon


def polygon(pts):
    return tuple(map(tuple, pts))


def vector(u, v):
    return v[0] - u[0], v[1] - u[1]


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def compose(*fns):
    return lambda x: ft.reduce(lambda val, fn: fn(val), fns, x)


def apply_to_vertices(fn):
    return lambda poly: tuple(map(fn, poly))


def regular_polygon(n, r=1, center=(0, 0)):
    ox, oy = center
    return polygon(
        (ox + r * math.cos(2 * math.pi * k / n),
         oy + r * math.sin(2 * math.pi * k / n))
        for k in range(n)
    )


def gen_rectangle(width=1, height=0.8, gap=0.35, x0=0, y0=0):
    stride = width + gap
    return map(
        lambda k: (
            (x0 + k * stride,         y0),
            (x0 + k * stride + width, y0),
            (x0 + k * stride + width, y0 + height),
            (x0 + k * stride,         y0 + height),
        ),
        it.count()
    )


def gen_triangle(side=1, gap=0.35, x0=0, y0=0):
    h = side * math.sqrt(3) / 2
    stride = side + gap
    return map(
        lambda k: (
            (x0 + k * stride,            y0),
            (x0 + k * stride + side / 2, y0 + h),
            (x0 + k * stride + side,     y0),
        ),
        it.count()
    )


def gen_reversed_triangle(side=1, gap=0.35, x0=0, y0=0):
    h = side * math.sqrt(3) / 2
    stride = side + gap
    return map(
        lambda k: (
            (x0 + k * stride + side,     y0),
            (x0 + k * stride + side / 2, y0 - h),
            (x0 + k * stride,            y0),
        ),
        it.count()
    )


def gen_hexagon(side=0.55, gap=0.35, x0=0, y0=0):
    h = math.sqrt(3) * side
    stride = 2 * side + gap
    return map(
        lambda k: (
            (x0 + k * stride + side / 2,     y0),
            (x0 + k * stride + 3 * side / 2, y0),
            (x0 + k * stride + 2 * side,     y0 + h / 2),
            (x0 + k * stride + 3 * side / 2, y0 + h),
            (x0 + k * stride + side / 2,     y0 + h),
            (x0 + k * stride,                y0 + h / 2),
        ),
        it.count()
    )


def tr_translate(dx, dy):
    return apply_to_vertices(lambda pt: (pt[0] + dx, pt[1] + dy))


def tr_rotate(angle, center=(0, 0)):
    ox, oy = center
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    def _rot(pt):
        rx, ry = pt[0] - ox, pt[1] - oy
        return rx * cos_a - ry * sin_a + ox, rx * sin_a + ry * cos_a + oy

    return apply_to_vertices(_rot)


def tr_symmetry(axis="x"):
    mirrors = {
        "x":      lambda pt: (pt[0], -pt[1]),
        "y":      lambda pt: (-pt[0], pt[1]),
        "origin": lambda pt: (-pt[0], -pt[1]),
    }
    return apply_to_vertices(mirrors[axis])


def tr_homothety(scale, center=(0, 0)):
    ox, oy = center
    return apply_to_vertices(lambda pt: (ox + scale * (pt[0] - ox), oy + scale * (pt[1] - oy)))


def transform_sequence(shapes, *transforms):
    return map(compose(*transforms), shapes)


def visualize(shapes, title="", limit=None, figsize=(9, 4), xlim=None, ylim=None):
    fig, ax = plt.subplots(figsize=figsize)

    if limit is not None:
        shapes = it.islice(shapes, limit)

    for poly in shapes:
        ax.add_patch(MplPolygon(
            poly, closed=True, fill=True,
            alpha=0.15, edgecolor="black", linewidth=1.5,
        ))

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_aspect("equal")
    ax.grid(True)

    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if not xlim and not ylim:
        ax.autoscale_view()

    ax.set_title(title)
    plt.show()


def area(poly):
    edges = zip(poly, poly[1:] + poly[:1])
    signed2 = ft.reduce(
        lambda acc, edge: acc + edge[0][0] * edge[1][1] - edge[1][0] * edge[0][1],
        edges, 0,
    )
    return abs(signed2) / 2


def side_lengths(poly):
    return tuple(map(lambda e: math.dist(e[0], e[1]), zip(poly, poly[1:] + poly[:1])))


def perimeter(poly):
    return ft.reduce(lambda acc, ln: acc + ln, side_lengths(poly), 0)


def min_side(poly):
    return min(side_lengths(poly))


def is_convex(poly):
    triples = zip(poly, poly[1:] + poly[:1], poly[2:] + poly[:2])
    signs = tuple(map(lambda t: cross(vector(t[0], t[1]), vector(t[1], t[2])), triples))
    return not (tuple(filter(lambda z: z > 0, signs)) and tuple(filter(lambda z: z < 0, signs)))


def point_inside_convex(pt, poly):
    edges = zip(poly, poly[1:] + poly[:1])
    signs = tuple(map(lambda e: cross(vector(e[0], e[1]), vector(e[0], pt)), edges))
    return not (tuple(filter(lambda z: z > 0, signs)) and tuple(filter(lambda z: z < 0, signs)))


def flt_convex_polygon():
    return is_convex


def flt_angle_point(pt):
    return lambda poly: pt in poly


def flt_square(max_area):
    return lambda poly: area(poly) < max_area


def flt_short_side(max_len):
    return lambda poly: min_side(poly) < max_len


def flt_point_inside(pt):
    return lambda poly: is_convex(poly) and point_inside_convex(pt, poly)


def flt_polygon_angles_inside(inner):
    return lambda poly: is_convex(poly) and any(map(lambda pt: point_inside_convex(pt, poly), inner))


def iterator_decorator(wrap):
    def decorator(fn):
        @ft.wraps(fn)
        def wrapper(*iters, **kwargs):
            return fn(*map(wrap, iters), **kwargs)
        return wrapper
    return decorator


def tr_translate_decorator(dx, dy):
    return iterator_decorator(lambda it_: map(tr_translate(dx, dy), it_))


def tr_rotate_decorator(angle, center=(0, 0)):
    return iterator_decorator(lambda it_: map(tr_rotate(angle, center), it_))


def tr_symmetry_decorator(axis="x"):
    return iterator_decorator(lambda it_: map(tr_symmetry(axis), it_))


def tr_homothety_decorator(scale, center=(0, 0)):
    return iterator_decorator(lambda it_: map(tr_homothety(scale, center), it_))


def flt_short_side_decorator(max_len):
    return iterator_decorator(lambda it_: filter(flt_short_side(max_len), it_))


def dist_origin(pt):
    return math.hypot(pt[0], pt[1])


def agr_origin_nearest(best, poly):
    closest = ft.reduce(lambda a, b: a if dist_origin(a) < dist_origin(b) else b, poly)
    return closest if best is None or dist_origin(closest) < dist_origin(best) else best


def agr_max_side(best, poly):
    longest = ft.reduce(lambda a, b: a if a > b else b, side_lengths(poly))
    return longest if best is None or longest > best else best


def agr_min_area(best, poly):
    s = area(poly)
    return s if best is None or s < best else best


def agr_perimeter(acc, poly):
    return acc + perimeter(poly)


def agr_area(acc, poly):
    return acc + area(poly)


def zip_tuple(*tuples):
    return ft.reduce(lambda a, b: a + b, tuples, tuple())


def zip_polygons(*iters):
    return map(lambda group: zip_tuple(*group), zip(*iters))


def count_2D(x0=0, y0=0, dx=1, dy=1):
    return map(lambda k: (x0 + k * dx, y0 + k * dy), it.count())


def show_lines_between_polygons():
    lo, hi = 0.18, 0.65

    def quad(k):
        x1 = 1.0 + k * 0.9
        x2 = x1 + 0.55
        return (
            (x1, lo * x1),
            (x2, lo * x2),
            (x2, hi * x2),
            (x1, hi * x1),
        )

    fig, ax = plt.subplots(figsize=(9, 5))
    xs = (0, 7)
    ax.plot(xs, tuple(map(lambda x: lo * x, xs)), linestyle="--", linewidth=1)
    ax.plot(xs, tuple(map(lambda x: hi * x, xs)), linestyle="--", linewidth=1)

    for poly in map(quad, range(6)):
        ax.add_patch(MplPolygon(poly, closed=True, fill=True, alpha=0.15, edgecolor="black", linewidth=1.5))

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_xlim(-0.2, 7)
    ax.set_ylim(-0.2, 4.8)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Четырёхугольники между двумя прямыми")
    plt.show()


def show_filter_angles_inside():
    shapes = tuple(it.islice(gen_rectangle(width=1.2, height=1.2, gap=0.25, x0=-3, y0=-0.6), 7))
    inner = ((0.1, 0.1), (0.35, 0.1), (0.2, 0.35))
    matched = tuple(filter(flt_polygon_angles_inside(inner), shapes))

    fig, ax = plt.subplots(figsize=(9, 4))

    for poly in shapes:
        ax.add_patch(MplPolygon(poly, closed=True, fill=True, alpha=0.08, edgecolor="gray", linewidth=1))
    for poly in matched:
        ax.add_patch(MplPolygon(poly, closed=True, fill=True, alpha=0.2, edgecolor="black", linewidth=2))

    ax.add_patch(MplPolygon(inner, closed=True, fill=True, alpha=0.35, edgecolor="black", linewidth=1.5))
    ax.scatter(tuple(map(lambda pt: pt[0], inner)), tuple(map(lambda pt: pt[1], inner)), zorder=5)

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_xlim(-3.5, 5.8)
    ax.set_ylim(-1.0, 1.3)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Фильтр: прямоугольник содержит угол заданного полигона")
    plt.show()

    print("Количество фигур после фильтра:", len(matched))


@tr_rotate_decorator(math.pi / 6)
def show_rotated(shapes):
    visualize(shapes, "Поворот через декоратор")


@flt_short_side_decorator(0.5)
def show_filtered(shapes):
    visualize(shapes, "Фильтр через декоратор: короткая сторона < 0.5")


def run_all_demos():
    visualize(gen_rectangle(x0=-4), "7 прямоугольников", limit=7)
    visualize(gen_triangle(x0=-4),  "7 треугольников",   limit=7)
    visualize(gen_hexagon(x0=-4),   "7 шестиугольников", limit=7)

    phi = math.pi / 6
    bands = [
        transform_sequence(
            it.islice(gen_rectangle(width=1, height=0.35, gap=0.1, x0=-4), 7),
            tr_translate(0, offset), tr_rotate(phi),
        )
        for offset in (-0.6, 0, 0.6)
    ]
    visualize(it.chain(*bands), "Три параллельные ленты")

    stripe1 = transform_sequence(
        it.islice(gen_rectangle(width=0.8, height=0.3, gap=0.15, x0=-4), 9),
        tr_rotate(math.pi / 6),
        tr_translate(1.5, 0.5),
    )
    stripe2 = transform_sequence(
        it.islice(gen_rectangle(width=0.8, height=0.3, gap=0.15, x0=-4), 9),
        tr_rotate(-math.pi / 6),
        tr_translate(1.5, 0.5),
    )
    visualize(it.chain(stripe1, stripe2), "Две пересекающиеся ленты")

    top = it.islice(gen_triangle(side=0.8, gap=0.2, x0=-4, y0=0.4), 7)
    bottom = map(tr_symmetry("x"), it.islice(gen_triangle(side=0.8, gap=0.2, x0=-4, y0=0.4), 7))
    visualize(it.chain(top, bottom), "Симметричные ленты треугольников")

    show_lines_between_polygons()

    base = ((0, 0), (1, 0), (1, 0.7), (0, 0.7))
    scaled = map(lambda i: tr_translate(i * 1.4 - 5, 0)(tr_homothety(0.4 + i * 0.12)(base)), range(12))
    chosen = tuple(it.islice(filter(flt_square(1.2), scaled), 6))
    visualize(chosen, "Фильтр по площади: выбрано 6 фигур", xlim=(-5.5, 4), ylim=(-0.2, 1.8))
    print("Количество отфильтрованных фигур:", len(chosen))

    growing = map(
        lambda k: tr_translate(k * 1.4, 0)(tr_homothety(k)(((0, 0), (1, 0), (1, 0.4), (0, 0.4)))),
        it.count(0.2, 0.15),
    )
    visualize(it.islice(filter(flt_short_side(0.25), it.islice(growing, 15)), 4), "Фильтрация по кратчайшей стороне")

    show_filter_angles_inside()

    show_rotated(it.islice(gen_rectangle(width=1, height=0.4, gap=0.2, x0=-4), 7))

    growing = map(
        lambda k: tr_translate(k * 1.4, 0)(tr_homothety(k)(((0, 0), (1, 0), (1, 0.4), (0, 0.4)))),
        it.count(0.2, 0.15),
    )
    show_filtered(it.islice(growing, 15))

    sample = tuple(it.islice(gen_rectangle(width=1, height=0.5, gap=0.2, x0=-2), 5))
    print("Ближайший угол к началу координат:", ft.reduce(agr_origin_nearest, sample, None))
    print("Самая длинная сторона:",             ft.reduce(agr_max_side,       sample, None))
    print("Минимальная площадь:",               ft.reduce(agr_min_area,       sample, None))
    print("Суммарный периметр:",                ft.reduce(agr_perimeter,      sample, 0))
    print("Суммарная площадь:",                 ft.reduce(agr_area,           sample, 0))

    seq1 = iter([((1, 1), (2, 2), (3, 1)), ((11, 11), (12, 12), (13, 11))])
    seq2 = iter([((1, -1), (2, -2), (3, -1)), ((11, -11), (12, -12), (13, -11))])
    print(list(zip_polygons(seq1, seq2)))

    top = it.islice(gen_triangle(side=1, gap=0.2, x0=-4, y0=0), 7)
    bottom = it.islice(gen_reversed_triangle(side=1, gap=0.2, x0=-4, y0=0), 7)
    visualize(zip_polygons(top, bottom), "Склейка треугольников zip_polygons")

    print(tuple(it.islice(count_2D(x0=0, y0=0, dx=2, dy=3), 5)))


if __name__ == "__main__":
    run_all_demos()
