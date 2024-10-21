import random


def find_threat_or_win(grid_size, grid, color, length):
    """
    Проверяет наличие угрозы или возможности выиграть для заданного цвета.

    Ищет в каждом направлении (горизонтально, вертикально и по диагоналям) наличие ряда фишек
    заданного цвета и определяет, можно ли заблокировать ход противника или выиграть.

    Параметры:
    grid_size (int): Размер поля (количество строк и столбцов)
    grid (list): Двумерный массив, представляющий игровое поле, где None обозначает пустую клетку
    color (str): Цвет фишки, для которой проверяется угроза или возможность выигрыша
    length (int): Длина ряда, которая необходима для выигрыша или блокировки

    Возвращает:
    tuple или None: Координаты (столбец, строка) пустой клетки, в которую можно поставить фишку для блокировки,
                    или None, если такой клетки нет.
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for x in range(grid_size):
        for y in range(grid_size):
            if grid[y][x] == color:
                for dr, dc in directions:
                    count = 1
                    empty_spots = []

                    for i in range(1, length):
                        r, c = y + dr * i, x + dc * i
                        if 0 <= r < grid_size and 0 <= c < grid_size:
                            if grid[r][c] == color:
                                count += 1
                            elif grid[r][c] is None:
                                empty_spots.append((c, r))
                                break
                            else:
                                break

                    # Проверяем в противоположном направлении
                    for i in range(1, length):
                        r, c = y - dr * i, x - dc * i
                        if 0 <= r < grid_size and 0 <= c < grid_size:
                            if grid[r][c] == color:
                                count += 1
                            elif grid[r][c] is None:
                                empty_spots.append((c, r))
                                break
                            else:
                                break

                    if count == length - 1 and empty_spots:
                        return empty_spots[0]
    return None


def find_best_move_near_bot(grid_size, grid, bot_color):
    """
    Ищет наилучший ход для бота рядом с его фишками.

    Проверяет каждую клетку на наличие фишек заданного цвета и находит пустые клетки рядом
    с ними. Выбирает случайный ход из доступных.

    Параметры:
    grid_size (int): Размер поля (количество строк и столбцов)
    grid (list): Двумерный массив, представляющий игровое поле, где None обозначает пустую клетку
    bot_color (str): Цвет фишки бота.

    Возвращает:
    tuple или None: Координаты (столбец, строка) наилучшего хода для бота,
                    или None, если таких ходов нет.
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Направления: горизонталь, вертикаль, диагонали
    potential_moves = []
    for x in range(grid_size):
        for y in range(grid_size):
            if grid[y][x] == bot_color:
                for dr, dc in directions:
                    r, c = y + dr, x + dc
                    if 0 <= r < grid_size and 0 <= c < grid_size and grid[r][c] is None:
                        potential_moves.append((c, r))
    if potential_moves:
        return random.choice(potential_moves)
    return None
