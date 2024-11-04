from collections.abc import Callable
from typing import Optional

import pygame

from base_game import BaseGameMode
from bot_logic import check_winner, bot_move
from button import ColorPath, Button


class NEnemiesMode(BaseGameMode):
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
        super().__init__(theme, exit_to_lobby, exit_to_options)
        self.count_enemies: int = count_enemies
        self._player_color = ColorPath.BLACK
        self.create_game_buttons()
        self.class_arg: int = count_enemies

        self._bot_colors = [f'images/bot_{i}.png' for i in range(count_enemies)]
        self._bots = [pygame.transform.scale(pygame.image.load(bot_color), (290, 190)) for bot_color in
                      self._bot_colors]
        self._current_bot_index = 0

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

    def undo_move(self, args: Optional[tuple[int, int]] = None) -> None:
        """Отменяет последний ход (игрока и всех ботов)."""
        if self._game_end or not self._move_undo_stack:
            return
        moves = self._move_undo_stack.pop()
        for move in moves:
            if move:
                self._remove_move(move)
        self._move_redo_stack.append(moves)

    def redo_move(self, args: Optional[tuple[int, int]] = None) -> None:
        """Повторяет последний отмененный ход (игрока и ботов)."""
        if self._game_end or not self._move_redo_stack:
            return
        moves = self._move_redo_stack.pop()
        for i, move in enumerate(moves):
            color = self._player_color if i == 0 else self._bot_colors[i - 1]
            self.place_move(move, color)
        self._move_undo_stack.append(moves)

    def _remove_move(self, move: Optional[tuple[int, int]]) -> None:
        """
        Удаляет фишку с указанной позиции на поле.
        """
        x, y = move
        self._grid[y][x] = None
        button_pos = (x * 40 + 20, y * 40 + 20)
        if button_pos in self._board.buttons:
            self._board.buttons[button_pos].is_transparent = True
            self._board.buttons[button_pos].change_obj(self._player_color)

    def handle_click(self, pos: tuple[int, int]) -> None:
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
            if check_winner(self._grid_size, self._grid, (gridx, gridy)):
                self._game_end = True
                self._winner = self._player
                return
            self._move_redo_stack = []

            # Ход каждого бота поочередно
            bot_moves = []
            for bot_color in self._bot_colors:
                move = bot_move(self._grid_size, self._grid, bot_color, self._player_color)
                self.place_move(move, bot_color)
                self._total_time -= 1
                bot_moves.append(move)
                if check_winner(self._grid_size, self._grid, move):
                    self._game_end = True
                    self._winner = self._robot
                    return
            self._move_undo_stack[-1].extend(bot_moves)
