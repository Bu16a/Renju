import pygame
from collections.abc import Callable

from base_game import BaseGameMode
from bot_logic import check_winner, bot_move
from button import ColorPath, Button


class ClassicMode(BaseGameMode):
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
        super().__init__(theme, exit_to_lobby, exit_to_options)
        self._player_color: str = player_color
        self.class_arg: str = player_color
        self._bot_color: str = ColorPath.BLACK if player_color == ColorPath.WHITE else ColorPath.WHITE
        self.create_game_buttons()

        self._grid[7][7] = ColorPath.BLACK
        self._board.buttons[(300, 300)].obj = (
            pygame.transform.scale(pygame.image.load(ColorPath.BLACK).convert_alpha(), (40, 40)))
        self._board.buttons[(300, 300)].is_transparent = False
        if player_color == ColorPath.BLACK:
            self.place_move(bot_move(self._grid_size, self._grid, self._bot_color, self._player_color), self._bot_color)

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
                                is_transparent=True, obj=self._player_color)
                self._board.add_button(button)

    def redo_move(self, args: tuple[int, int] | None = None) -> None:
        """
        Повторяет последний отмененный ход (по одному ходу игрока и бота).
        """
        if self._game_end or not self._move_redo_stack:
            return
        player_and_bot_moves = self._move_redo_stack.pop()
        move_of_player_move, move_of_bot = player_and_bot_moves
        self.place_move(move_of_player_move, self._player_color)
        self.place_move(move_of_bot, self._bot_color)
        self._move_undo_stack.append(player_and_bot_moves)

    def undo_move(self, args: tuple[int, int] | None = None) -> None:
        """
        Отменяет последний ход (по одному ходу игрока и бота).
        """
        if self._game_end:
            return
        if self._move_undo_stack:
            player_and_bot_moves = self._move_undo_stack.pop()
            self._remove_move(player_and_bot_moves[0])  # Удалить фишку игрока
            self._remove_move(player_and_bot_moves[1])  # Удалить фишку бота
            self._move_redo_stack.append(player_and_bot_moves)

    def _remove_move(self, move: tuple[int, int] | None) -> None:
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
        """
        Обрабатывает нажатие на поле и ставит фишку в нужное место.
        """
        if self._game_end:
            return
        self._player_time = 15
        x, y = pos
        gridx, gridy = (x - 20) // 40, (y - 20) // 40
        if self._grid[gridy][gridx] is None:
            self._grid[gridy][gridx] = self._player_color
            self._board.buttons[pos].is_transparent = False
            self._move_undo_stack.append([(gridx, gridy), None])
            if check_winner(self._grid_size, self._grid, (gridx, gridy)):
                self._game_end = True
                self._winner = self._player
                return
            self._move_redo_stack = []
            move = bot_move(self._grid_size, self._grid, self._bot_color, self._player_color)
            self.place_move(move, self._bot_color)
            self._total_time -= 1
            if self._move_undo_stack:
                self._move_undo_stack[-1] = [self._move_undo_stack[-1][0], move]
            if check_winner(self._grid_size, self._grid, move):
                self._game_end = True
                self._winner = self._robot
