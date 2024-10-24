import random
from typing import Callable, Optional, Tuple, List

import pygame

from button import ColorPath, Button
from robot_logic import find_threat_or_win, find_best_move_near_bot
from window import Window


class Board:
    def __init__(self,
                 player_color: str,
                 theme: str,
                 exit_to_lobby: Callable[[], None],
                 exit_to_options: Callable[[], None]):
        """
        Инициализирует игровое поле и необходимые параметры.

        Параметры:
        player_color (str): Цвет фишки игрока (путь к изображению фишки).
        theme (str): Тема игры.
        exit_to_lobby (Callable): Функция для выхода в лобби.
        exit_to_options (Callable): Функция для выхода в настройки.
        """
        self._restart_board: Optional[Board] = None
        self._theme: str = theme
        self._board: Window = Window(icon='images/icon.png', width=840, height=640,
                                     background=self._theme, caption="RENJU")
        self._player_color: str = player_color
        self._bot_color: str = ColorPath.BLACK if player_color == ColorPath.WHITE else ColorPath.WHITE
        self._game_end: bool = False
        self._winner: Optional[pygame.Surface] = None
        self._exit_to_lobby_callback: Callable[[], None] = exit_to_lobby
        self._exit_to_options_callback: Callable[[], None] = exit_to_options

        # Создание кнопок для игрового поля
        size: int = 15
        for x in range(size):
            for y in range(size):
                button = Button(x=20 + 40 * x, y=20 + 40 * y, width=40, height=40,
                                size=36,
                                function=self.handle_click,
                                args=(20 + 40 * x, 20 + 40 * y),
                                is_transparent=True,
                                obj=player_color)
                self._board.add_button(button)

        # Кнопки для управления игрой
        button_restart = Button(x=640, y=0,
                                width=200, height=100,
                                size=26,
                                color=(255, 255, 255), hover_color=(185, 186, 189),
                                function=self.restart,
                                text='Перезапуск')
        button_exit_to_lobby = Button(x=640, y=100,
                                      width=200, height=100,
                                      size=26,
                                      color=(255, 255, 255), hover_color=(185, 186, 189),
                                      function=self.exit_to_lobby,
                                      text='Выход в главное меню')
        button_exit_to_options = Button(x=640, y=200,
                                        width=200, height=100,
                                        size=26,
                                        color=(255, 255, 255), hover_color=(185, 186, 189),
                                        function=self.exit_to_options,
                                        text='Выход в настройки')
        self._board.add_button(button_restart)
        self._board.add_button(button_exit_to_options)
        self._board.add_button(button_exit_to_lobby)

        # Загрузка изображений для победителя и бота
        winner = pygame.transform.scale(pygame.image.load("images/winner.png"), (290, 150))
        self._robot: pygame.Surface = pygame.transform.scale(pygame.image.load("images/robot.png"), (290, 190))
        self._player: pygame.Surface = pygame.transform.scale(pygame.image.load("images/player.png"), (290, 190))
        self._board.draw_figure(winner, 593, 300)

        # Инициализация сетки
        self._grid_size: int = 15
        self._grid: List[List[Optional[str]]] = [[None for _ in range(self._grid_size)] for _ in range(self._grid_size)]
        self._grid[7][7] = ColorPath.BLACK
        self._board.buttons[(300, 300)].obj = (
            pygame.transform.scale(pygame.image.load(ColorPath.BLACK).convert_alpha(), (40, 40)))
        self._board.buttons[(300, 300)].is_transparent = False

        if player_color == ColorPath.BLACK:
            self.bot_move()

    def restart(self, args: Optional[Tuple[int, int]]) -> None:
        """
        Перезапускает игру, создавая новое игровое поле.
        """
        self._board.on_close()
        restart_board = Board(self._player_color, self._theme, self._exit_to_lobby_callback,
                              self._exit_to_options_callback)
        restart_board.run()

    def exit_to_lobby(self, args: Optional[Tuple[int, int]]) -> None:
        """
        Выход в лобби.
        """
        self._board.on_close()
        self._exit_to_lobby_callback()

    def exit_to_options(self, args: Optional[Tuple[int, int]]) -> None:
        """
        Выход в настройки.
        """
        self._board.on_close()
        self._exit_to_options_callback()

    def check_winner(self, row: int, col: int) -> bool:
        """
        Проверяет наличие 5 фишек одного цвета в ряду.
        """
        directions: List[Tuple[int, int]] = [(0, 1), (1, 0), (1, 1), (1, -1)]
        current_color: Optional[str] = self._grid[row][col]

        for dr, dc in directions:
            count: int = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self._grid_size and 0 <= c < self._grid_size and self._grid[r][c] == current_color:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self._grid_size and 0 <= c < self._grid_size and self._grid[r][c] == current_color:
                    count += 1
                else:
                    break

            if count >= 5:
                return True

        return False

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """
        Обрабатывает нажатие на поле и ставит фишку в нужное место.
        """
        if not self._game_end:
            x, y = pos
            gridx = (x - 20) // 40
            gridy = (y - 20) // 40
            if self._grid[gridy][gridx] is None:
                self._grid[gridy][gridx] = self._player_color
                self._board.buttons[pos].is_transparent = False
                if self.check_winner(gridy, gridx):
                    self._game_end = True
                    self._winner = self._player
                    return
                self.bot_move()

    def bot_move(self) -> None:
        """
        Логика хода бота.
        """
        # 1. Поиск победного хода
        winning_move: Optional[Tuple[int, int]] = find_threat_or_win(self._grid_size, self._grid, self._bot_color, 5)
        if winning_move:
            self.place_bot_move(winning_move)
            return

        # 2. Блокировка игрока, если у него есть 4 фишки подряд
        threat_move: Optional[Tuple[int, int]] = find_threat_or_win(self._grid_size, self._grid, self._player_color, 5)
        if threat_move:
            self.place_bot_move(threat_move)
            return

        # 3. Блокировка игрока, если у него есть 3 фишки подряд
        threat_move = find_threat_or_win(self._grid_size, self._grid, self._player_color, 4)
        if threat_move:
            self.place_bot_move(threat_move)
            return

        # 4. Поиск хода рядом с фишками бота
        best_move: Optional[Tuple[int, int]] = find_best_move_near_bot(self._grid_size, self._grid, self._bot_color)
        if best_move:
            self.place_bot_move(best_move)
            return

        # 5. Если нет угроз и победных ходов, делаем случайный ход
        available_moves: List[Tuple[int, int]] = [(x, y) for x in range(self._grid_size) for y in range(self._grid_size)
                                                  if self._grid[y][x] is None]
        if available_moves:
            self.place_bot_move(random.choice(available_moves))

    def place_bot_move(self, move: Tuple[int, int]) -> None:
        """
        Размещает фишку бота на поле.
        """
        x, y = move
        button_pos = (x * 40 + 20, y * 40 + 20)

        if button_pos in self._board.buttons:
            self._grid[y][x] = self._bot_color
            self._board.buttons[button_pos].obj = (
                pygame.transform.scale(pygame.image.load(self._bot_color).convert_alpha(), (40, 40))
            )
            self._board.buttons[button_pos].is_transparent = False

            if self.check_winner(y, x):
                self._game_end = True
                self._winner = self._robot
        else:
            print(f"Invalid button position: {button_pos}")

    def run(self) -> None:
        """
        Запуск игрового цикла.
        """
        while self._board.running:
            self._board.draw_interface(0, 0)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._board.on_close()
                if event.type == pygame.MOUSEMOTION:
                    self._board.update_buttons(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._board.clicked(event.pos)
                if self._board.running and self._game_end:
                    self._board.draw_figure(self._winner, 593, 450)
