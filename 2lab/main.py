def ochistit_ekran():
    print("\n" * 2)

def pomosh():
    print("\n--- Команды ---")
    print("  start            - начать новую игру")
    print("  restart          - перезапустить текущую игру")
    print("  exit             - выйти из программы")
    print("  row col (цифры)  - сделать ход, например: 1 2")
    print("----------------")

def vybor_razmera():
    while True:
        try:
            a = input("\nВыберите размер поля (3 или 4): ").strip()
            if a == "3":
                return 3
            elif a == "4":
                return 4
            else:
                print("Ошибка: введите 3 или 4.")
        except:
            print("Ошибка ввода. Попробуйте снова.")

def sozdat_pole(n):
    pole = []
    for i in range(n):
        stroka = []
        for j in range(n):
            stroka.append(" ")
        pole.append(stroka)
    return pole

def risovat_pole(pole):
    n = len(pole)
    print("\n   ", end="")
    for j in range(1, n + 1):
        print(f" {j}  ", end="")
    print()
    
    for i in range(n):
        print(f"{i + 1}  ", end="")
        for j in range(n):
            print(f" {pole[i][j]} ", end="")
            if j < n - 1:
                print("|", end="")
        print()
        
        if i < n - 1:
            print("   ", end="")
            for j in range(n):
                if j < n - 1:
                    print("---+", end="")
                else:
                    print("---", end="")
            print()
    print()

def proverka_hoda(pole, x, y):
    n = len(pole)
    if x < 1 or x > n or y < 1 or y > n:
        return False
    if pole[x - 1][y - 1] != " ":
        return False
    return True

def sdelat_hod(pole, x, y, igrok):
    pole[x - 1][y - 1] = igrok

def proverka_pobedy(pole, x, y, igrok):
    n = len(pole)
    x1 = x - 1
    y1 = y - 1
    
    for j in range(n):
        if pole[x1][j] != igrok:
            break
        if j == n - 1:
            return True
    
    for i in range(n):
        if pole[i][y1] != igrok:
            break
        if i == n - 1:
            return True
    
    if x1 == y1:
        for i in range(n):
            if pole[i][i] != igrok:
                break
            if i == n - 1:
                return True
    
    if x1 + y1 == n - 1:
        for i in range(n):
            if pole[i][n - 1 - i] != igrok:
                break
            if i == n - 1:
                return True
    
    return False

def proverka_nichya(pole):
    n = len(pole)
    for i in range(n):
        for j in range(n):
            if pole[i][j] == " ":
                return False
    return True

def razbor_hoda(txt):
    chasti = txt.strip().split()
    if len(chasti) != 2:
        return None
    try:
        a = int(chasti[0])
        b = int(chasti[1])
        return a, b
    except:
        return None

def igra(n):
    pole = sozdat_pole(n)
    hod = 0
    igrok = "X"
    max_hodov = n * n
    
    ochistit_ekran()
    print(f"=== Игра началась! Поле {n}x{n} ===")
    risovat_pole(pole)
    
    while True:
        print(f"Ход игрока {igrok}")
        vvod = input("Введите команду или координаты: ").strip().lower()
        
        if vvod == "exit":
            print("Выход из игры. До свидания!")
            exit(0)
        elif vvod == "restart":
            print("Перезапуск игры...")
            return
        elif vvod == "start":
            print("Игра уже запущена. Используйте restart для новой игры.")
            continue
        elif vvod == "help":
            pomosh()
            continue
        
        koords = razbor_hoda(vvod)
        if koords is None:
            print("Ошибка: введите два числа через пробел (например: 1 2)")
            print("Или используйте команды: restart, exit, help")
            continue
        
        x, y = koords
        if not proverka_hoda(pole, x, y):
            print("Ошибка: клетка занята или координаты вне поля!")
            print(f"Допустимый диапазон: 1..{n}")
            continue
        
        sdelat_hod(pole, x, y, igrok)
        hod = hod + 1
        ochistit_ekran()
        risovat_pole(pole)
        
        if proverka_pobedy(pole, x, y, igrok):
            print(f"🎉 Игрок {igrok} победил! 🎉")
            break
        
        if hod == max_hodov or proverka_nichya(pole):
            print("Ничья! Поле полностью заполнено.")
            break
        
        if igrok == "X":
            igrok = "O"
        else:
            igrok = "X"
    
    print("\nИгра завершена.")
    while True:
        komanda = input("Хотите сыграть ещё? (да/нет/restart/exit): ").strip().lower()
        if komanda in ["да", "yes", "restart"]:
            return
        elif komanda in ["нет", "no", "exit"]:
            print("До свидания!")
            exit(0)
        else:
            print("Введите 'да' для новой игры, 'нет' для выхода.")

def main():
    print("Добро пожаловать в Крестики-нолики!")
    print("===================================")
    pomosh()
    
    while True:
        print("\nДля начала игры выберите размер поля.")
        r = vybor_razmera()
        igra(r)

if __name__ == "__main__":
    main()
