from pathlib import Path
from typing import Callable, Optional, List, Tuple

import pygame

from board import Board
from button import ColorPath, Button
from window import Window


class Options:
    def __init__(self, exit_to_lobby_callback: Callable[[], None]) -> None:
        """
        Инициализация класса Options.

        Создает окно настроек, загружает тему из файла и устанавливает
        цвет фишки игрока. Также добавляет кнопки для смены цвета фишки,
        смены темы и начала новой игры. Кнопки связываются с соответствующими методами.

        Параметры:
        - exit_to_lobby_callback: Функция, вызываемая для выхода в лобби.
        """
        self.new_game: Optional[Board] = None
        self.exit_to_lobby_callback: Callable[[], None] = exit_to_lobby_callback
        self.color: str = ColorPath.BLACK
        with open('setting/theme.txt') as f:
            self.theme: str = f'images/{f.readline()}'
        self.options_window: Window = Window('images/icon.png', 640, 640, self.theme, 'RENJU')
        button_start_game = Button(x=195, y=550,
                                   width=250, height=60,
                                   size=30,
                                   color=(255, 255, 255), hover_color=(185, 186, 189),
                                   function=self.start_game,
                                   text='Начать игру')
        button_change_chip = Button(x=40, y=450,
                                    width=250, height=60,
                                    size=30,
                                    color=(255, 255, 255), hover_color=(185, 186, 189),
                                    function=self.change_chip,
                                    text='Сменить цвет фишки')
        button_change_theme = Button(x=350, y=450,
                                     width=250, height=60,
                                     size=30,
                                     color=(255, 255, 255), hover_color=(185, 186, 189),
                                     function=self.change_theme,
                                     text='Сменить тему')
        self.options_window.add_button(button_start_game)
        self.options_window.add_button(button_change_chip)
        self.options_window.add_button(button_change_theme)

    def change_theme(self, args: Optional[Tuple] = None) -> None:
        """
        Смена темы игры.

        Загружает следующую тему из списка доступных тем и обновляет фон
        окна настроек. Изменения темы сохраняются в файл.
        """
        themes: List[str] = ['grid0.jpg', 'grid1.jpg', 'grid2.jpg']
        theme_file = Path('setting/theme.txt')
        prev_theme: str = theme_file.read_text().strip()
        theme_index: int = (themes.index(prev_theme) + 1) % len(themes)
        theme_file.write_text(themes[theme_index])
        theme_image_path = Path('images') / themes[theme_index]
        new_theme: pygame.Surface = pygame.image.load(str(theme_image_path)).convert()

        self.theme = new_theme
        self.options_window.change_background(self.theme)

    def change_chip(self, args: Optional[Tuple] = None) -> None:
        """
        Смена цвета фишки игрока.

        Переключает цвет фишки между черным и белым. Также обновляет
        значение переменной `user`, указывая, какой цвет фишки у игрока.
        """
        self.color = ColorPath.WHITE if self.color == ColorPath.BLACK else ColorPath.BLACK

    def start_game(self, args: Optional[Tuple] = None) -> None:
        """
        Начинает новую игру.

        Закрывает окно настроек, создает новый экземпляр класса `Board`,
        передавая выбранный цвет фишки, тему и функцию для выхода в лобби.
        Затем запускает игру.
        """
        self.options_window.on_close()
        theme_file: str = 'setting/theme.txt'
        with open(theme_file, 'r') as file:
            theme: str = file.readline().strip()
        self.new_game = Board(self.color, f'images/{theme}', self.exit_to_lobby_callback, self.exit_to_options)
        self.new_game.run()

    def exit_to_options(self) -> None:
        """
        Выход из текущих опций и возвращение в меню настроек.

        Закрывает текущее окно настроек и создает новый экземпляр класса `Options`,
        после чего запускает метод `run_options` для отображения окна настроек.
        """
        self.options_window.on_close()
        back_to_options: Options = Options(self.exit_to_lobby_callback)
        back_to_options.run_options()

    def run_options(self) -> None:
        """
        Запускает главный цикл окна настроек.

        Отображает интерфейс настроек и обрабатывает события, такие как
        нажатия на кнопки и закрытие окна. Цикл продолжается, пока
        окно настроек открыто.

        В процессе цикла обрабатываются следующие события:
        - QUIT: закрытие окна.
        - MOUSEMOTION: обновление кнопок в зависимости от положения курсора.
        - MOUSEBUTTONDOWN: обработка нажатий на кнопки.
        """
        while self.options_window.running:
            self.options_window.draw_interface(0, 0)
            chip_image: pygame.Surface = pygame.image.load(self.color).convert_alpha()
            self.options_window.draw_figure(chip_image, 300, 460)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.options_window.on_close()
                if event.type == pygame.MOUSEMOTION:
                    self.options_window.update_buttons(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.options_window.clicked(event.pos)
