from typing import Optional, Tuple

import pygame

from button import Button
from options import Options
from window import Window


class Lobby:
    def __init__(self) -> None:
        """
        Инициализация класса Lobby.

        Создает главное окно лобби, устанавливает заголовок, размеры и фон,
        а также добавляет кнопку для начала новой игры. Кнопка связывается с
        методом `start_new_game`.
        """
        self.options: Optional[Options] = None
        self.main_window: Window = Window('images/icon.png', 660, 390, 'images/background.png', "RENJU")
        button_start_new_game = Button(x=180, y=220,
                                       width=300, height=60,
                                       size=40,
                                       color=(255, 255, 255), hover_color=(185, 186, 189),
                                       function=self.start_new_game,
                                       text='Начать новую игру')
        self.main_window.add_button(button_start_new_game)

    def start_new_game(self, args: Optional[Tuple]) -> None:
        """
        Обрабатывает нажатие кнопки "Начать новую игру".

        Закрывает текущее окно лобби и создает новый экземпляр класса `Options`,
        передавая метод `exit_to_lobby` для выхода обратно в лобби. Затем запускает
        метод `run_options` для отображения окна настроек.
        """
        self.main_window.on_close()
        self.options = Options(self.exit_to_lobby)
        self.options.run_options()

    def exit_to_lobby(self) -> None:
        """
        Метод для выхода в лобби.

        Закрывает текущее главное окно и создает новый экземпляр класса `Lobby`,
        после чего запускает метод `run_lobby` для отображения окна лобби.
        """
        self.main_window.on_close()
        s = Lobby()
        s.run_lobby()

    def run_lobby(self) -> None:
        """
        Запускает главный цикл лобби.

        Отображает интерфейс лобби и обрабатывает события, такие как
        нажатие на кнопки и закрытие окна. Цикл продолжается, пока
        окно лобби открыто.

        В процессе цикла обрабатываются следующие события:
        - QUIT: закрытие окна.
        - MOUSEMOTION: обновление кнопок в зависимости от положения курсора.
        - MOUSEBUTTONDOWN: обработка нажатий на кнопки.
        """
        while self.main_window.running:
            self.main_window.draw_interface(0, 0)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.main_window.on_close()
                if event.type == pygame.MOUSEMOTION:
                    self.main_window.update_buttons(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_window.clicked(event.pos)
