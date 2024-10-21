import pygame


class Button:
    def __init__(self, x, y, width, height, size, color, hover_color, function, on_close, args,
                 is_transparent, obj, text=''):
        """
        Инициализирует кнопку с заданными параметрами.

        Параметры:
        x (int): Позиция кнопки по оси X.
        y (int): Позиция кнопки по оси Y.
        width (int): Ширина кнопки в пикселях.
        height (int): Высота кнопки в пикселях.
        size (int): Размер шрифта текста на кнопке.
        color (tuple): Цвет кнопки в формате RGB.
        hover_color (tuple): Цвет кнопки при наведении в формате RGB.
        function (callable): Функция, вызываемая при нажатии на кнопку.
        on_close (bool): Флаг, указывающий, нужно ли закрывать приложение при нажатии на кнопку.
        args (tuple): Аргументы для функции.
        is_transparent (bool): Флаг, указывающий, является ли кнопка полупрозрачной.
        obj (str): Путь к изображению кнопки.
        text (str): Текст на кнопке (по умолчанию пустая строка).
        """
        self.new_obj = None
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.is_hovered = False
        self._pos = (x, y)
        self.size = size
        self.function = function
        self.on_close = on_close
        self.is_transparent = is_transparent
        self.args = args
        self.obj = None
        if obj is not None:
            self.obj = (
                pygame.transform.scale(pygame.image.load(obj).convert_alpha(), (self.rect.width, self.rect.height)))
        if self.is_transparent:
            self.new_obj = self.obj.copy()
            self.new_obj.set_alpha(128)

    def draw(self, screen):
        """
        Рисует кнопку на переданном экране.
        """
        if not self.is_transparent:
            if self.obj is None:
                button_surface = pygame.Surface((self.rect.width, self.rect.height))
                button_surface.fill(self.color)
                if self.is_hovered:
                    pygame.draw.rect(button_surface, self.hover_color, (0, 0, self.rect.width, self.rect.height))
                else:
                    pygame.draw.rect(button_surface, self.color, (0, 0, self.rect.width, self.rect.height))
                font = pygame.font.Font(None, self.size)
                text_surface = font.render(self.text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
                button_surface.blit(text_surface, text_rect)
                screen.blit(button_surface, self.rect)
            else:
                screen.blit(self.obj, self.rect)
        else:
            if self.is_hovered:
                screen.blit(self.new_obj, self.rect)

    def is_clicked(self, pos):
        """
        Проверяет, была ли кнопка нажата.
        """
        return self.rect.collidepoint(pos)

    def update(self, pos):
        """
        Обновляет состояние кнопки в зависимости от позиции курсора мыши.
        """
        if self.rect.collidepoint(pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def change_transparent(self):
        """
        Убирает полупрозрачность с кнопки.
        """
        self.is_transparent = False

    @property
    def get_pos(self):
        """
        Возвращает позицию кнопки.
        """
        return self._pos
