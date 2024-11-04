import random
from typing import Optional, List, Tuple

_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))
_ROW_LENGTH = 5


def find_threat_or_win(grid_size: int, grid: List[List[Optional[str]]], color: str, length: int) \
        -> Optional[Tuple[int, int]]:
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

    for x in range(grid_size):
        for y in range(grid_size):
            if grid[y][x] != color:
                continue
            for dr, dc in _DIRECTIONS:
                count = 1
                empty_spots = []

                for direction in [1, -1]:
                    for i in range(1, length):
                        r, c = y + dr * i * direction, x + dc * i * direction
                        if 0 <= r < grid_size and 0 <= c < grid_size:
                            if grid[r][c] == color:
                                count += 1
                            elif grid[r][c] is None:
                                empty_spots.append((c, r))
                                break
                            else:
                                break
                        else:
                            break

                if count == length - 1 and empty_spots:
                    return empty_spots[0]


def find_best_move_near_bot(grid_size: int, grid: List[List[Optional[str]]], bot_color: str) \
        -> Optional[Tuple[int, int]]:
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
    potential_moves: List[Tuple[int, int]] = []
    for x in range(grid_size):
        for y in range(grid_size):
            if grid[y][x] == bot_color:
                for dr, dc in _DIRECTIONS:
                    r, c = y + dr, x + dc
                    if 0 <= r < grid_size and 0 <= c < grid_size and grid[r][c] is None:
                        potential_moves.append((c, r))
    if potential_moves:
        return random.choice(potential_moves)
    return None


def bot_move(grid_size, grid, bot_color, player_color) -> Tuple[int, int]:
    """
    Логика хода бота.
    """
    # 1. Поиск победного хода
    if winning_move := find_threat_or_win(grid_size, grid, bot_color, 5):
        return winning_move

    # 2. Блокировка игрока, если у него есть 4 фишки подряд
    if threat_move := find_threat_or_win(grid_size, grid, player_color, 5):
        return threat_move

    # 3. Блокировка игрока, если у него есть 3 фишки подряд
    if threat_move := find_threat_or_win(grid_size, grid, player_color, 4):
        return threat_move

    # 4. Поиск хода рядом с фишками бота
    if best_move := find_best_move_near_bot(grid_size, grid, bot_color):
        return best_move

    # 5. Если нет угроз и победных ходов, делаем случайный ход
    available_moves: List[Tuple[int, int]] = [(x, y) for x in range(grid_size) for y in range(grid_size)
                                              if grid[y][x] is None]
    if available_moves:
        return random.choice(available_moves)


def check_winner(grid_size: int, grid: List[List[Optional[str]]], move: Tuple[int, int]) -> bool:
    """
    Проверяет наличие 5 фишек одного цвета в ряду.
    """
    col, row = move
    current_color: Optional[str] = grid[row][col]

    for dr, dc in _DIRECTIONS:
        count: int = 1
        for i in range(1, _ROW_LENGTH):
            r, c = row + dr * i, col + dc * i
            if 0 <= r < grid_size and 0 <= c < grid_size and grid[r][c] == current_color:
                count += 1
            else:
                break
        for i in range(1, _ROW_LENGTH):
            r, c = row - dr * i, col - dc * i
            if 0 <= r < grid_size and 0 <= c < grid_size and grid[r][c] == current_color:
                count += 1
            else:
                break

        if count >= 5:
            return True

    return False
