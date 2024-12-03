import sys
from PyQt5.QtWidgets import QApplication
from controller import Controller
from view import WelcomeWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    welcome_window = WelcomeWindow(controller)
    controller.current_window = welcome_window
    welcome_window.show()
    sys.exit(app.exec_())


