from datetime import datetime
from collections.abc import Callable
from typing import Optional

import pygame

from button import Button
from window import Window

_POSITION_WINNER = (290, 190)
_SIZE_WINNER = (290, 150)


class BaseGameMode:
    def __init__(self,
                 theme: str,
                 exit_to_lobby: Callable[[], None],
                 exit_to_options: Callable[[], None]):
        """
        Базовый класс для игрового режима.

        Параметры:
        theme (str): Тема игры.
        exit_to_lobby (Callable): Функция для выхода в лобби.
        exit_to_options (Callable): Функция для выхода в настройки.
        """
        self._theme: str = theme
        self.class_arg: Optional[str] = None
        self._board: Window = Window(icon='images/icon.png', width=840, height=640,
                                     background=self._theme, caption="RENJU")
        self._game_end: bool = False
        self._winner: Optional[pygame.Surface] = None
        self._exit_to_lobby_callback: Callable[[], None] = exit_to_lobby
        self._exit_to_options_callback: Callable[[], None] = exit_to_options

        winner = pygame.transform.scale(pygame.image.load("images/winner.png"), _SIZE_WINNER)
        self._robot: pygame.Surface = pygame.transform.scale(pygame.image.load("images/robot.png"), _POSITION_WINNER)
        self._player: pygame.Surface = pygame.transform.scale(pygame.image.load("images/player.png"), _POSITION_WINNER)
        self._board.draw_figure(winner, 593, 300)

        self._grid_size: int = 15
        self._grid: list[list[Optional[str]]] = [[None for _ in range(self._grid_size)] for _ in range(self._grid_size)]
        self._total_time: int = 180  # Общее время на игру (в секундах)
        self._player_time: int = 15  # Время игрока на ход (в секундах)
        self._last_time: datetime = datetime.now()

        # Стеки для отмены и повтора ходов
        self._move_undo_stack: list[tuple] = []
        self._move_redo_stack: list[tuple] = []
        self.create_control_buttons()

    def create_control_buttons(self):
        """
        Создает кнопки управления для базового игрового режима.
        """
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
        current_time = datetime.now()
        elapsed = current_time - self._last_time
        if elapsed.seconds >= 1:
            self._total_time -= elapsed.seconds
            self._player_time -= elapsed.seconds
            self._last_time = current_time

        if self._total_time <= 0:
            self._game_end = True
            self._winner = None
        elif self._player_time <= 0:
            self._game_end = True
            self._winner = self._robot

    def restart(self, args: Optional[tuple[int, int]] = None) -> None:
        """
        Перезапускает игру.
        """
        self._board.on_close()
        new_game = self.__class__(self.class_arg, self._theme, self._exit_to_lobby_callback,
                                  self._exit_to_options_callback)
        new_game.run()

    def exit_to_lobby(self, args: Optional[tuple[int, int]] = None) -> None:
        """
        Выход в лобби.
        """
        self._board.on_close()
        self._exit_to_lobby_callback()

    def exit_to_options(self, args: Optional[tuple[int, int]] = None) -> None:
        """
        Выход в настройки.
        """
        self._board.on_close()
        self._exit_to_options_callback()

    def undo_move(self, args: Optional[tuple[int, int]] = None) -> None:
        """Отменяет последний ход."""
        if self._game_end or not self._move_undo_stack:
            return
        # Логика для отмены хода

    def redo_move(self, args: Optional[tuple[int, int]] = None) -> None:
        """Повторяет последний отмененный ход."""
        if self._game_end or not self._move_redo_stack:
            return
        # Логика для повтора хода

    def place_move(self, move: tuple[int, int], color: str) -> None:
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
