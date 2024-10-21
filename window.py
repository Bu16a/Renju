import ctypes
import pygame
from button import Button


class Window:
    def __init__(self, icon, width, height, background, caption):
        """
        Инициализирует окно Pygame с заданными параметрами.

        Параметры:
        icon (str): Путь к изображению иконки окна.
        width (int): Ширина окна в пикселях.
        height (int): Высота окна в пикселях.
        background (str): Путь к изображению фона.
        caption (str): Заголовок окна.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption(caption)
        self.background = pygame.image.load(background).convert()
        pygame.display.set_icon(pygame.image.load(icon))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(icon)
        self.buttons = {}
        self.running = True

    def add_button(self, x, y, width, height, size, color, hover_color, function, on_close,
                   args, is_transparent, obj, text=''):
        """
        Добавляет кнопку на окно.
        """
        button = Button(x, y, width, height, size, color, hover_color, function, on_close, args,
                        is_transparent, obj, text)
        self.buttons.setdefault(button.get_pos, button)

    def update_buttons(self, pos):
        """
        Обновляет состояние кнопок в зависимости от позиции мыши.
        """
        for button in self.buttons.values():
            button.update(pos)

    def change_background(self, theme):
        """
        Изменяет фоновое изображение окна.
        """
        self.background = theme

    def draw_interface(self, x_screen, y_screen):
        """
        Рисует интерфейс окна, включая фон и кнопки.
        """
        self.screen.blit(self.background, (x_screen, y_screen))
        for button in self.buttons.values():
            button.draw(self.screen)

    def draw_figure(self, figure, x, y):
        """
        Рисует заданную фигуру на экране.
        """
        self.screen.blit(figure, (x, y))

    def clicked(self, pos):
        """
        Обрабатывает нажатия на кнопки.
        """
        for button in self.buttons.values():
            if button.is_clicked(pos):
                if button.on_close:
                    self.on_close()
                button.function(button.args)

    def on_close(self):
        """
        Закрывает окно и завершает работу Pygame.
        """
        self.running = False
        pygame.quit()
