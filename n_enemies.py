import time
from typing import Callable, Optional, Tuple, List

import pygame

from bot_logic import check_winner, bot_move
from button import ColorPath, Button
from window import Window


class NEnemiesMode:
    def __init__(self,
                 count_enemies: int,
                 theme: str,
                 exit_to_lobby: Callable[[], None],
                 exit_to_options: Callable[[], None]):
        """
        Инициализирует игровое поле и необходимые параметры.

        Параметры:
        count_enemies (int): Количество противников.
        theme (str): Тема игры.
        exit_to_lobby (Callable): Функция для выхода в лобби.
        exit_to_options (Callable): Функция для выхода в настройки.
        """
        self._restart_board: Optional[NEnemiesMode] = None
        self._theme: str = theme
        self.count_enemies: int = count_enemies
        self._player_color = ColorPath.BLACK
        self._move_undo_stack = []
        self._move_redo_stack = []
        self._board: Window = Window(icon='images/icon.png', width=840, height=640,
                                     background=self._theme, caption="RENJU")
        self._game_end: bool = False
        self._winner: Optional[pygame.Surface] = None
        self._exit_to_lobby_callback: Callable[[], None] = exit_to_lobby
        self._exit_to_options_callback: Callable[[], None] = exit_to_options

        self._grid_size: int = 15
        self._grid: List[List[Optional[str]]] = [[None for _ in range(self._grid_size)] for _ in range(self._grid_size)]
        self.create_game_buttons()

        # Загрузка изображений для победителя и бота
        winner = pygame.transform.scale(pygame.image.load("images/winner.png"), (290, 150))
        self._robot: pygame.Surface = pygame.transform.scale(pygame.image.load("images/robot.png"), (290, 190))
        self._player: pygame.Surface = pygame.transform.scale(pygame.image.load("images/player.png"), (290, 190))
        self._board.draw_figure(winner, 593, 300)

        self._bot_colors = [f'images/bot_{i}.png' for i in range(count_enemies)]
        self._bots = [pygame.transform.scale(pygame.image.load(bot_color), (290, 190)) for bot_color in
                      self._bot_colors]
        self._current_bot_index = 0

        self._total_time: int = 180  # Общее время на игру в секундах (3 минуты)
        self._player_time: int = 15  # Время игрока на ход в секундах
        self._last_time: float = time.time()

    def create_game_buttons(self):
        """
        Создает кнопки на игровом поле и кнопки управления игрой.
        """
        size: int = 15
        for x in range(size):
            for y in range(size):
                button = Button(x=20 + 40 * x, y=20 + 40 * y, width=40, height=40,
                                size=36, function=self.handle_click,
                                args=(20 + 40 * x, 20 + 40 * y),
                                is_transparent=True, obj=ColorPath.BLACK)
                self._board.add_button(button)

        button_restart = Button(x=640, y=0, width=200, height=60, size=26, color=(255, 255, 255),
                                hover_color=(185, 186, 189), function=self.restart, text='Перезапуск')
        button_exit_to_lobby = Button(x=640, y=60, width=200, height=60, size=26, color=(255, 255, 255),
                                      hover_color=(185, 186, 189), function=self.exit_to_lobby,
                                      text='Выход в главное меню')
        button_exit_to_options = Button(x=640, y=120, width=200, height=60, size=26, color=(255, 255, 255),
                                        hover_color=(185, 186, 189), function=self.exit_to_options,
                                        text='Выход в настройки')
        button_undo = Button(x=640, y=180, width=200, height=60, size=26, color=(255, 255, 255),
                             hover_color=(185, 186, 189), function=self.undo_move, text='Undo')
        button_redo = Button(x=640, y=240, width=200, height=60, size=26, color=(255, 255, 255),
                             hover_color=(185, 186, 189), function=self.redo_move, text='Redo')

        self._board.add_button(button_restart)
        self._board.add_button(button_exit_to_options)
        self._board.add_button(button_exit_to_lobby)
        self._board.add_button(button_undo)
        self._board.add_button(button_redo)

    def update_timers(self):
        """
        Обновляет общий и ходовой таймеры.
        """
        current_time = time.time()
        elapsed = current_time - self._last_time
        if elapsed >= 1:  # Обновляем каждую секунду
            self._total_time -= int(elapsed)  # Уменьшаем общий таймер
            self._player_time -= int(elapsed)  # Уменьшаем таймер игрока
            self._last_time = current_time  # Сбрасываем время обновления

        # Проверка окончания времени
        if self._total_time <= 0:
            self._game_end = True
            self._winner = None  # Завершаем игру ничьей, если общий таймер истек
        elif self._player_time <= 0:
            self._game_end = True
            self._winner = self._robot  # Бот выигрывает, если время игрока истекло

    def undo_move(self, args: Optional[Tuple[int, int]] = None) -> None:
        """Отменяет последний ход (игрока и всех ботов)."""
        if self._game_end or not self._move_undo_stack:
            return
        moves = self._move_undo_stack.pop()
        for move in moves:
            if move:
                self._remove_move(move)
        self._move_redo_stack.append(moves)

    def redo_move(self, args: Optional[Tuple[int, int]] = None) -> None:
        """Повторяет последний отмененный ход (игрока и ботов)."""
        if self._game_end or not self._move_redo_stack:
            return
        moves = self._move_redo_stack.pop()
        for i, move in enumerate(moves):
            color = self._player_color if i == 0 else self._bot_colors[i - 1]
            self.place_move(move, color)
        self._move_undo_stack.append(moves)

    def _remove_move(self, move: Optional[Tuple[int, int]]) -> None:
        """
        Удаляет фишку с указанной позиции на поле.
        """
        x, y = move
        self._grid[y][x] = None
        button_pos = (x * 40 + 20, y * 40 + 20)
        if button_pos in self._board.buttons:
            self._board.buttons[button_pos].is_transparent = True
            self._board.buttons[button_pos].change_obj(self._player_color)

    def restart(self, args: Optional[Tuple[int, int]]) -> None:
        """
        Перезапускает игру, создавая новое игровое поле.
        """
        self._board.on_close()
        restart_board = NEnemiesMode(self.count_enemies, self._theme, self._exit_to_lobby_callback,
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

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Обрабатывает клик игрока и инициирует ход ботов поочередно."""
        if self._game_end:
            return
        self._player_time = 15
        x, y = pos
        gridx = (x - 20) // 40
        gridy = (y - 20) // 40
        if self._grid[gridy][gridx] is None:
            self._grid[gridy][gridx] = self._player_color
            self._board.buttons[pos].is_transparent = False
            self._move_undo_stack.append([(gridx, gridy)])
            if check_winner(self._grid_size, self._grid, gridy, gridx):
                self._game_end = True
                self._winner = self._player
                return
            self._move_redo_stack = []

            # Ход каждого бота поочередно
            bot_moves = []
            for bot_color in self._bot_colors:
                x, y = bot_move(self._grid_size, self._grid, bot_color, self._player_color)
                self.place_move((x, y), bot_color)
                self._total_time -= 1
                bot_moves.append((x, y))
                if check_winner(self._grid_size, self._grid, y, x):
                    self._game_end = True
                    self._winner = self._robot
                    return
            self._move_undo_stack[-1].extend(bot_moves)

    def place_move(self, move: Tuple[int, int], color) -> None:
        """
        Размещает фишку бота на поле.
        """
        x, y = move
        button_pos = (x * 40 + 20, y * 40 + 20)
        self._grid[y][x] = color
        self._board.buttons[button_pos].obj = (
            pygame.transform.scale(pygame.image.load(color).convert_alpha(), (40, 40))
        )
        self._board.buttons[button_pos].is_transparent = False

    def run(self) -> None:
        """
        Запуск игрового цикла.
        """
        while self._board.running:
            self._board.draw_interface(0, 0)
            if not self._game_end:
                self.update_timers()
            self._board.draw_text(f'Общее время: {self._total_time // 60}:{self._total_time % 60:02d}', 0, 0)
            self._board.draw_text(f'Время игрока: {self._player_time}', 200, 0)
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