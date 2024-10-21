import random
import pygame
from Renju.robot_logic import find_threat_or_win, find_best_move_near_bot
from Renju.window import Window


class Board:
    def __init__(self, player_color, theme, exit_to_lobby, exit_to_options):
        """
        Инициализирует игровое поле и необходимые параметры.

        Параметры:
        player_color (str): Цвет фишки игрока (путь к изображению фишки).
        theme (str): Тема игры.
        exit_to_lobby (callable): Функция для выхода в лобби.
        exit_to_options (callable): Функция для выхода в настройки.
        """
        self.restart_board = None
        self.theme = theme
        self.board = Window('images/icon.png', 840, 640, self.theme, "RENJU")
        self.player_color = player_color
        self.bot_color = "images/black.png" if player_color == "images/white.png" else "images/white.png"
        self.game_end = False
        self.winner = None
        self.exit_to_lobby_callback = exit_to_lobby
        self.exit_to_options_callback = exit_to_options

        # Создание кнопок для игрового поля
        for x in range(15):
            for y in range(15):
                self.board.add_button(x=20 + 40 * x, y=20 + 40 * y, width=40, height=40,
                                      size=36, color=(0, 0, 0, 0),
                                      hover_color=(0, 0, 0, 0),
                                      function=self.handle_click,
                                      on_close=False,
                                      args=(20 + 40 * x, 20 + 40 * y),
                                      is_transparent=True,
                                      obj=player_color,
                                      text='')

        # Кнопки для управления игрой
        self.board.add_button(640, 0, 200, 100, 26, (255, 255, 255), (185, 186, 189),
                              self.restart,
                              True, None, False, None,
                              'Перезапуск')
        self.board.add_button(640, 100, 200, 100, 26, (255, 255, 255), (185, 186, 189),
                              self.exit_to_lobby,
                              True, None, False, None,
                              'Выход в '
                              'главное меню')
        self.board.add_button(640, 200, 200, 100, 26, (255, 255, 255), (185, 186, 189),
                              self.exit_to_options,
                              True, None, False, None,
                              'Выход в '
                              'настройки')

        # Загрузка изображений для победителя и бота
        winner = pygame.transform.scale(pygame.image.load("images/winner.png"), (290, 150))
        self.robot = pygame.transform.scale(pygame.image.load("images/robot.png"), (290, 190))
        self.player = pygame.transform.scale(pygame.image.load("images/player.png"), (290, 190))
        self.board.draw_figure(winner, 593, 300)

        # Инициализация сетки
        self.grid_size = 15
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.grid[7][7] = "images/black.png"
        self.board.buttons[(300, 300)].obj = (
            pygame.transform.scale(pygame.image.load("images/black.png").convert_alpha(), (40, 40)))
        self.board.buttons[(300, 300)].is_transparent = False

        if player_color == "images/black.png":
            self.bot_move()

    def restart(self, args):
        """
        Перезапускает игру, создавая новое игровое поле.
        """
        self.board.on_close()
        restart_board = Board(self.player_color, self.theme, self.exit_to_lobby_callback, self.exit_to_options_callback)
        restart_board.run()

    def exit_to_lobby(self, args):
        """
        Выход в лобби.
        """
        self.board.on_close()
        self.exit_to_lobby_callback()

    def exit_to_options(self, args):
        """
        Выход в настройки.
        """
        self.board.on_close()
        self.exit_to_options_callback()

    def check_winner(self, row, col):
        """
        Проверяет наличие 5 фишек одного цвета в ряду.
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        current_color = self.grid[row][col]

        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size and self.grid[r][c] == current_color:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size and self.grid[r][c] == current_color:
                    count += 1
                else:
                    break

            if count >= 5:
                return True

        return False

    def handle_click(self, pos):
        """
        Обрабатывает нажатие на поле и ставит фишку в нужное место.
        """
        if not self.game_end:
            x, y = pos
            gridx = (x - 20) // 40
            gridy = (y - 20) // 40
            if self.grid[gridy][gridx] is None:
                self.grid[gridy][gridx] = self.player_color
                self.board.buttons[pos].is_transparent = False
                if self.check_winner(gridy, gridx):
                    self.game_end = True
                    self.winner = self.player
                    return
                self.bot_move()

    def bot_move(self):
        """
        Логика хода бота.

        Выполняет последовательные проверки для определения, где бот должен ходить,
        включая поиск выигрышного хода, блокировку игрока, и случайный ход, если нет угроз.
        """
        # 1. Поиск победного хода
        winning_move = find_threat_or_win(self.grid_size, self.grid, self.bot_color, 5)
        if winning_move:
            self.place_bot_move(winning_move)
            return

        # 2. Блокировка игрока, если у него есть 4 фишки подряд
        threat_move = find_threat_or_win(self.grid_size, self.grid, self.player_color, 5)
        if threat_move:
            self.place_bot_move(threat_move)
            return

        # 3. Блокировка игрока, если у него есть 3 фишки подряд
        threat_move = find_threat_or_win(self.grid_size, self.grid, self.player_color, 4)
        if threat_move:
            self.place_bot_move(threat_move)
            return

        # 4. Поиск хода рядом с фишками бота
        best_move = find_best_move_near_bot(self.grid_size, self.grid, self.bot_color)
        if best_move:
            self.place_bot_move(best_move)
            return

        # 5. Если нет угроз и победных ходов, делаем случайный ход
        available_moves = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size) if
                           self.grid[y][x] is None]
        if available_moves:
            self.place_bot_move(random.choice(available_moves))

    def place_bot_move(self, move):
        """
        Размещает фишку бота на поле.
        """
        x, y = move
        self.grid[y][x] = self.bot_color
        self.board.buttons[(x * 40 + 20, y * 40 + 20)].obj = (
            pygame.transform.scale(pygame.image.load(self.bot_color).convert_alpha(), (40, 40)))
        self.board.buttons[(x * 40 + 20, y * 40 + 20)].is_transparent = False

        if self.check_winner(y, x):
            self.game_end = True
            self.winner = self.robot

    def run(self):
        """
        Запуск игрового цикла.

        Обрабатывает события и обновляет интерфейс игры, пока игра продолжается.
        """
        while self.board.running:
            self.board.draw_interface(0, 0)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.board.on_close()
                if event.type == pygame.MOUSEMOTION:
                    self.board.update_buttons(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.board.clicked(event.pos)
                if self.board.running and self.game_end:
                    self.board.draw_figure(self.winner, 593, 450)
