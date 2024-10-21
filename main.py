import ctypes

from lobby import Lobby

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('images/icon.png')


def main():
    lobby = Lobby()
    lobby.run_lobby()


if __name__ == '__main__':
    main()
