import pygame

from Renju.board import Board
from window import Window

BLACK = "images/black.png"
WHITE = "images/white.png"


class Options:
    def __init__(self, exit_to_lobby_callback):
        """
        Инициализация класса Options.

        Создает окно настроек, загружает тему из файла и устанавливает
        цвет фишки игрока. Также добавляет кнопки для смены цвета фишки,
        смены темы и начала новой игры. Кнопки связываются с соответствующими методами.

        Параметры:
        - exit_to_lobby_callback: Функция, вызываемая для выхода в лобби.
        """
        self.new_game = None
        self.exit_to_lobby_callback = exit_to_lobby_callback
        self.color = BLACK
        with open('setting/theme.txt') as f:
            self.theme = f'images/{f.readline()}'
        self.options_window = Window('images/icon.png', 640, 640, self.theme, 'RENJU')
        self.options_window.add_button(195, 550, 250, 60, 30, (255, 255, 255), (185, 186, 189),
                                       self.start_game,
                                       True, None, False, None,
                                       'Начать игру')
        self.options_window.add_button(40, 450, 250, 60, 30, (255, 255, 255), (185, 186, 189),
                                       self.switch_chip, False, None, False, None,
                                       'Сменить цвет фишки')
        self.options_window.add_button(350, 450, 250, 60, 30, (255, 255, 255), (185, 186, 189),
                                       self.switch_theme, False, None,
                                       False, None, 'Сменить тему')

    def switch_theme(self, args):
        """
        Смена темы игры.

        Загружает следующую тему из списка доступных тем и обновляет фон
        окна настроек. Изменения темы сохраняются в файл.
        """
        themes = ['grid0.jpg', 'grid1.jpg', 'grid2.jpg']
        with open('setting/theme.txt', 'r') as file:
            prev_theme = file.readline().strip()
        theme_index = (themes.index(prev_theme) + 1) % len(themes)
        with open('setting/theme.txt', 'w') as file:
            file.write(themes[theme_index])
        new_theme = pygame.image.load(f'images/{themes[theme_index]}').convert()
        self.theme = new_theme
        self.options_window.change_background(self.theme)

    def switch_chip(self, args):
        """
        Смена цвета фишки игрока.

        Переключает цвет фишки между черным и белым. Также обновляет
        значение переменной `user`, указывая, какой цвет фишки у игрока.
        """
        self.color = WHITE if self.color == BLACK else BLACK

    def start_game(self, args):
        """
        Начинает новую игру.

        Закрывает окно настроек, создает новый экземпляр класса `Board`,
        передавая выбранный цвет фишки, тему и функцию для выхода в лобби.
        Затем запускает игру.
        """
        self.options_window.on_close()
        theme_file = 'setting/theme.txt'
        with open(theme_file, 'r') as file:
            theme = file.readline().strip()
        self.new_game = Board(self.color, f'images/{theme}', self.exit_to_lobby_callback, self.exit_to_options)
        self.new_game.run()

    def exit_to_options(self):
        """
        Выход из текущих опций и возвращение в меню настроек.

        Закрывает текущее окно настроек и создает новый экземпляр класса `Options`,
        после чего запускает метод `run_options` для отображения окна настроек.
        """
        self.options_window.on_close()
        s = Options(self.exit_to_lobby_callback)
        s.run_options()

    def run_options(self):
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
            self.options_window.draw_figure(pygame.image.load(self.color).convert_alpha(), 300, 460)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.options_window.on_close()
                if event.type == pygame.MOUSEMOTION:
                    self.options_window.update_buttons(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.options_window.clicked(event.pos)
