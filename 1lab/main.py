[14.04.2026 15:08] Иван Двизов: # -*- coding: utf-8 -*-
import copy

# --- Базовый класс ---
class Piece:
    def init(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.symbol = '?'

    def get_moves(self, board):
        return []

    def move_to(self, r, c):
        self.row = r
        self.col = c

    def repr(self):
        return self.symbol

# --- Стандартные фигуры ---
class King(Piece):
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'K' if color == 'white' else 'k'

    def get_moves(self, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                r, c = self.row + dr, self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board.grid[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))
        return moves

class Queen(Piece):
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'Q' if color == 'white' else 'q'

    def get_moves(self, board):
        moves = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            r, c = self.row + dr, self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board.grid[r][c] is None:
                    moves.append((r, c))
                else:
                    if board.grid[r][c].color != self.color:
                        moves.append((r, c))
                    break
                r, c = r + dr, c + dc
        return moves

class Knight(Piece):
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'N' if color == 'white' else 'n'

    def get_moves(self, board):
        moves = []
        steps = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr, dc in steps:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board.grid[r][c] is None or board.grid[r][c].color != self.color:
                    moves.append((r, c))
        return moves

class Pawn(Piece):
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'P' if color == 'white' else 'p'
        self.dir = -1 if color == 'white' else 1

    def get_moves(self, board):
        moves = []
        f_row = self.row + self.dir
        # Вперед
        if 0 <= f_row < 8 and board.grid[f_row][self.col] is None:
            moves.append((f_row, self.col))
            start_row = 6 if self.color == 'white' else 1
            f2_row = self.row + 2 * self.dir
            if self.row == start_row and board.grid[f2_row][self.col] is None:
                moves.append((f2_row, self.col))
        # Рубим
        for dc in [-1, 1]:
            c = self.col + dc
            if 0 <= f_row < 8 and 0 <= c < 8:
                target = board.grid[f_row][c]
                if target and target.color != self.color:
                    moves.append((f_row, c))
                # Взятие на проходе
                if (f_row, c) == board.ep_target:
                    moves.append((f_row, c))
        return moves

# --- НОВЫЕ ФИГУРЫ (3 балла) ---
class Guardian(Piece):
    """Страж: ходит как король, но на 2 клетки"""
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'G' if color == 'white' else 'g'

    def get_moves(self, board):
        moves = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0: continue
                r, c = self.row + dr, self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board.grid[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))
        return moves
[14.04.2026 15:08] Иван Двизов: class Archer(Piece):
    """Лучник: как слон, но не дальше 3 клеток"""
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'A' if color == 'white' else 'a'

    def get_moves(self, board):
        moves = []
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for step in range(1, 4):
                r, c = self.row + dr*step, self.col + dc*step
                if 0 <= r < 8 and 0 <= c < 8:
                    if board.grid[r][c] is None: moves.append((r, c))
                    else:
                        if board.grid[r][c].color != self.color: moves.append((r, c))
                        break
                else: break
        return moves

class Mage(Piece):
    """Маг: телепорт на любую пустую клетку того же цвета"""
    def init(self, color, r, c):
        super().init(color, r, c)
        self.symbol = 'M' if color == 'white' else 'm'

    def get_moves(self, board):
        moves = []
        my_cell_color = (self.row + self.col) % 2
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == my_cell_color and board.grid[r][c] is None:
                    moves.append((r, c))
        return moves

# --- Логика доски ---
class Board:
    def init(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.ep_target = None # Клетка для взятия на проходе
        self.setup()

    def setup(self):
        # Расставляем новые и старые фигуры
        order = [King, Queen, Guardian, Archer, Mage, Knight, Knight, King] # Для примера
        # Упрощенная расстановка для теста
        for i, cls in enumerate([Guardian, Knight, Archer, Queen, King, Archer, Mage, Guardian]):
            self.grid[0][i] = cls('black', 0, i)
            self.grid[7][i] = cls('white', 7, i)
            self.grid[1][i] = Pawn('black', 1, i)
            self.grid[6][i] = Pawn('white', 6, i)

    def draw(self, highlights=[]):
        print("\n  a b c d e f g h")
        for r in range(8):
            print(8-r, end=" ")
            for c in range(8):
                char = str(self.grid[r][c]) if self.grid[r][c] else "."
                if (r, c) in highlights:
                    print(f"({char})", end="")
                else:
                    print(f" {char} ", end="")
            print(8-r)
        print("  a b c d e f g h\n")

    def is_check(self, color):
        k_pos = None
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and isinstance(p, King) and p.color == color:
                    k_pos = (r, c)
        if not k_pos: return False
        
        opp_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == opp_color:
                    if k_pos in p.get_moves(self): return True
        return False

# --- Управление игрой ---
class Game:
    def init(self):
        self.board = Board()
        self.turn = 'white'
        self.history = []

    def to_rc(self, s):
        try:
            return 8 - int(s[1]), ord(s[0]) - ord('a')
        except: return None

    def move(self, start_s, end_s):
        s_rc, e_rc = self.to_rc(start_s), self.to_rc(end_s)
        if not s_rc or not e_rc: return False

        p = self.board.grid[s_rc[0]][s_rc[1]]
        if not p or p.color != self.turn or e_rc not in p.get_moves(self.board):
            print("Недопустимый ход!")
            return False

        # Сохраняем состояние для отката
        prev_state = copy.deepcopy((self.board.grid, self.board.ep_target, self.turn))
        
        # Логика взятия на проходе
        if isinstance(p, Pawn) and e_rc == self.board.ep_target:
            self.board.grid[s_rc[0]][e_rc[1]] = None

        # Обычный ход
        captured = self.board.grid[e_rc[0]][e_rc[1]]
        self.board.grid[e_rc[0]][e_rc[1]] = p
        self.board.grid[s_rc[0]][s_rc[1]] = None
        p.move_to(e_rc[0], e_rc[1])
[14.04.2026 15:08] Иван Двизов: # Проверка шаха самому себе
        if self.board.is_check(self.turn):
            print("Король под ударом!")
            self.board.grid, self.board.ep_target, self.turn = prev_state[0], prev_state[1], prev_state[2]
            p.move_to(s_rc[0], s_rc[1])
            return False

        # Превращение пешки (1 балл)
        if isinstance(p, Pawn) and e_rc[0] in [0, 7]:
            print("1:Queen, 2:Guardian, 3:Archer, 4:Mage")
            choice = input("Выберите фигуру (1-4): ")
            classes = {'1': Queen, '2': Guardian, '3': Archer, '4': Mage}
            self.board.grid[e_rc[0]][e_rc[1]] = classes.get(choice, Queen)(self.turn, e_rc[0], e_rc[1])

        # Установка цели для en passant
        self.board.ep_target = None
        if isinstance(p, Pawn) and abs(e_rc[0] - s_rc[0]) == 2:
            self.board.ep_target = ((s_rc[0] + e_rc[0]) // 2, s_rc[1])

        self.history.append(prev_state)
        self.turn = 'black' if self.turn == 'white' else 'white'
        return True

    def undo(self):
        if self.history:
            self.board.grid, self.board.ep_target, self.turn = self.history.pop()
            print("Ход отменен.")
        else: print("История пуста.")

    def run(self):
        while True:
            self.board.draw()
            if self.board.is_check(self.turn): print("!!! ШАХ !!!")
            cmd = input(f"[{self.turn}] Введите ход (e2 e4), 'undo', 'moves e2' или 'exit': ").split()
            if not cmd: continue
            if cmd[0] == 'exit': break
            if cmd[0] == 'undo': self.undo()
            elif cmd[0] == 'moves':
                rc = self.to_rc(cmd[1])
                p = self.board.grid[rc[0]][rc[1]]
                if p: self.board.draw(highlights=p.get_moves(self.board))
            elif len(cmd) == 2:
                self.move(cmd[0], cmd[1])

if name == "main":
    Game().run()
