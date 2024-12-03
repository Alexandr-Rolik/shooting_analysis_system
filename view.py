import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, QLineEdit, QDialog,
    QTableWidget, QTableWidgetItem, QTextEdit, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt
from functools import partial
from controller import Controller


def add_centered_item(table, row, column, text):
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignCenter)
    table.setItem(row, column, item)


class WelcomeWindow(QMainWindow):
    def __init__(self, controller_link):
        super().__init__()
        self.controller = controller_link
        self.setWindowTitle("Shooting Analysis")
        self.setGeometry(590, 320, 700, 500)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        welcome_label = QLabel("Welcome", self)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        welcome_label.setAlignment(Qt.AlignCenter)

        login_button = QPushButton("Логін", self)
        login_button.clicked.connect(self.show_login_dialog)

        register_button = QPushButton("Реєстрація", self)
        register_button.clicked.connect(self.show_register_dialog)

        button_layout = QHBoxLayout()
        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(welcome_label)
        main_layout.addLayout(button_layout)
        main_layout.setSpacing(20)

        central_widget.setLayout(main_layout)

    def show_login_dialog(self):
        dialog = LoginDialog(self.controller, self)
        dialog.exec_()

    @staticmethod
    def show_register_dialog():
        dialog = RegisterDialog()
        dialog.exec_()


class LoginDialog(QDialog):
    def __init__(self, controller_link, parent_window):
        super().__init__()
        self.controller = controller_link
        self.parent_window = parent_window
        self.setWindowTitle("Логін")
        self.setGeometry(800, 450, 300, 200)
        self.init_ui()

    def init_ui(self):
        login_label = QLabel("Введіть логін:", self)
        self.login_input = QLineEdit(self)

        login_layout = QHBoxLayout()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)

        password_label = QLabel("Введіть пароль:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        login_button = QPushButton("Увійти", self)
        login_button.clicked.connect(self.handle_login)

        main_layout = QVBoxLayout()
        main_layout.addLayout(login_layout)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(login_button)

        self.setLayout(main_layout)

    def handle_login(self):
        username = self.login_input.text()
        password = self.password_input.text()

        success = self.controller.login_user(username, password)
        if success:
            self.parent_window.close()  # Закриваємо WelcomeWindow
            self.accept()  # Закриваємо LoginDialog


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Реєстрація")
        self.setGeometry(800, 450, 300, 200)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        # Поле для логіну
        login_label = QLabel("Введіть логін:", self)
        self.login_input = QLineEdit(self)

        login_layout = QHBoxLayout()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)

        # Поле для паролю
        password_label = QLabel("Введіть пароль:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # Поле для імені
        first_name_label = QLabel("Введіть ім'я:", self)
        self.first_name_input = QLineEdit(self)

        first_name_layout = QHBoxLayout()
        first_name_layout.addWidget(first_name_label)
        first_name_layout.addWidget(self.first_name_input)

        # Поле для прізвища
        last_name_label = QLabel("Введіть прізвище:", self)
        self.last_name_input = QLineEdit(self)

        last_name_layout = QHBoxLayout()
        last_name_layout.addWidget(last_name_label)
        last_name_layout.addWidget(self.last_name_input)

        # Кнопка реєстрації
        register_button = QPushButton("Зареєструватися", self)
        register_button.clicked.connect(self.handle_register)

        # Основне вертикальне розташування
        main_layout = QVBoxLayout()
        main_layout.addLayout(login_layout)
        main_layout.addLayout(password_layout)
        main_layout.addLayout(first_name_layout)
        main_layout.addLayout(last_name_layout)
        main_layout.addWidget(register_button)

        self.setLayout(main_layout)

    def handle_register(self):
        username = self.login_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        user_type = "shooter"

        success = self.controller.register_user(username, password, first_name, last_name, user_type)

        # Якщо реєстрація пройшла успішно, закриваємо вікно
        if success:
            self.accept()

    def closeEvent(self, event):
        event.accept()


class ShooterMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_menu = None
        self.setWindowTitle("Меню стрільця")
        self.setGeometry(760, 400, 400, 300)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("Вітаємо, стрільцю!")
        layout.addWidget(welcome_label)

        results_training = QPushButton("Переглянути результати тренувань", self)
        results_training.clicked.connect(self.view_training_results)
        layout.addWidget(results_training)

        edit_profile_button = QPushButton("Налаштувати профіль", self)
        edit_profile_button.clicked.connect(self.edit_profile)
        layout.addWidget(edit_profile_button)

        exit_button = QPushButton("Вийти", self)
        exit_button.clicked.connect(self.exit_menu)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def view_training_results(self):
        training_data = self.controller.get_training_sessions()
        self.training_results_window = TrainingResultsWindow(training_data, self.controller)
        self.training_results_window.show()

    def edit_profile(self):
        self.profile_menu = ProfileMenu(self.controller)
        self.profile_menu.show()

    def exit_menu(self):
        self.close()
        self.controller.clean_temp_file()
        # Перезапуск процесу view
        os.execv(sys.executable, ['python'] + sys.argv)


class TrainingResultsWindow(QWidget):
    def __init__(self, training_data, controller_link, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результати тренувань")
        self.setGeometry(550, 400, 917, 400)
        self.training_data = training_data  # Список кортежів: (id, avg_score, date, instructor_name, instructor_surname)
        self.controller = controller_link
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.training_table = QTableWidget(self)
        self.training_table.setRowCount(len(self.training_data))
        self.training_table.setColumnCount(5)  # 4 для даних + 1 для кнопок
        self.training_table.setHorizontalHeaderLabels(["Сесія", "Середня оцінка", "Дата", "Інструктор", "Дії"])

        # Встановлення ширини для кожної колонки
        self.training_table.setColumnWidth(0, 70)  # Колонка "Сесія"
        self.training_table.setColumnWidth(1, 150)  # Колонка "Середня оцінка"
        self.training_table.setColumnWidth(2, 170)  # Колонка "Дата"
        self.training_table.setColumnWidth(3, 130)  # Колонка "Інструктор"
        self.training_table.setColumnWidth(4, 350)  # Колонка "Дії"

        # Встановлення висоти кожного рядка
        for row in range(len(self.training_data)):
            self.training_table.setRowHeight(row, 50)  # Висота рядка

        for row, session in enumerate(self.training_data):
            session_id, avg_score, date, instructor_name, instructor_surname = session

            add_centered_item(self.training_table, row, 0, str(session_id))
            add_centered_item(self.training_table, row, 1, str(avg_score))
            add_centered_item(self.training_table, row, 2, date.strftime("%Y-%m-%d %H:%M:%S"))
            add_centered_item(self.training_table, row, 3, f"{instructor_name} {instructor_surname}")

            # Створення кнопок для перегляду сесії та коментаря
            button_layout = QHBoxLayout()

            view_session_button = QPushButton("Переглянути сесію", self)
            view_session_button.clicked.connect(partial(self.view_session, session_id))
            button_layout.addWidget(view_session_button)

            view_comment_button = QPushButton("Переглянути коментар", self)
            view_comment_button.clicked.connect(partial(self.view_comment, session_id))
            button_layout.addWidget(view_comment_button)

            # Додавання віджету з кнопками до таблиці
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.training_table.setCellWidget(row, 4, button_widget)

        layout.addWidget(self.training_table)
        self.setLayout(layout)

    def view_session(self, session_id):
        self.controller.view_training_session(session_id)

    def view_comment(self, session_id):
        self.controller.load_commentary(session_id)


class CommentaryWindow(QWidget):
    def __init__(self, commentary, date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Коментар інструктора")
        self.setGeometry(750, 400, 500, 300)
        self.commentary = commentary
        self.date = date
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        comment_label = QLabel(f"Коментар: {self.commentary}")
        date_label = QLabel(f"Дата коментаря: {self.date.strftime('%Y-%m-%d %H:%M:%S')}")

        layout.addWidget(comment_label)
        layout.addWidget(date_label)

        close_button = QPushButton("Закрити", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class SessionDetailsWindow(QWidget):
    def __init__(self, session_details, parent=None):
        super().__init__(parent)
        self.table = None
        self.setWindowTitle("Деталі тренувальної сесії")
        self.setGeometry(600, 400, 800, 400)
        self.session_details = session_details
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.session_details))
        self.table.setColumnCount(6)  # 5 колонок + кнопка "Деталі"
        self.table.setHorizontalHeaderLabels(["Дистанція", "Кількість пострілів", "Середня оцінка", "Зброя", "Дата", ""])

        # Встановлення ширини для кожної колонки
        self.table.setColumnWidth(0, 100)  # Колонка "Дистанція"
        self.table.setColumnWidth(1, 150)  # Колонка "Кількість пострілів"
        self.table.setColumnWidth(2, 130)  # Колонка "Середня оцінка"
        self.table.setColumnWidth(3, 100)  # Колонка "Зброя"
        self.table.setColumnWidth(4, 150)  # Колонка "Дата"

        for row, data in enumerate(self.session_details):
            target_id, distance, shots_number, avg_score, weapon_info, date = data
            add_centered_item(self.table, row, 0, str(distance) + " м")
            add_centered_item(self.table, row, 1, str(shots_number))
            add_centered_item(self.table, row, 2, str(avg_score))
            add_centered_item(self.table, row, 3, weapon_info)
            add_centered_item(self.table, row, 4, str(date))

            details_button = QPushButton("Деталі")
            details_button.clicked.connect(partial(self.show_details, target_id))
            self.table.setCellWidget(row, 5, details_button)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def show_details(self, target_id):
        self.controller.get_hits(target_id)


class HitDetailsWindow(QWidget):
    def __init__(self, hit_details, parent=None):
        super().__init__(parent)
        self.table = None
        self.setWindowTitle("Деталі влучань")
        self.setGeometry(600, 400, 872, 400)
        self.hit_details = hit_details
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.hit_details))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Координата X", "Координата Y", "Оцінка", "Помилка", "Дата"])

        self.table.setColumnWidth(3, 300)  # Колонка "Помилка"
        self.table.setColumnWidth(4, 150)  # Колонка "Дата"

        for row, hit in enumerate(self.hit_details):
            x, y, score, mistake_description, date = hit
            add_centered_item(self.table, row, 0, str(x))
            add_centered_item(self.table, row, 1, str(y))
            add_centered_item(self.table, row, 2, str(score))
            add_centered_item(self.table, row, 3, mistake_description)
            add_centered_item(self.table, row, 4, str(date))

        layout.addWidget(self.table)
        self.setLayout(layout)


class ProfileMenu(QWidget):
    def __init__(self, controller_link, parent=None):
        super().__init__(parent)
        self.name_menu = None
        self.setWindowTitle("Налаштування профілю")
        self.setGeometry(810, 460, 300, 200)
        self.controller = controller_link
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        name_button = QPushButton("Змінити ім'я", self)
        name_button.clicked.connect(self.change_name)
        layout.addWidget(name_button)

        password_button = QPushButton("Змінити пароль", self)
        password_button.clicked.connect(self.change_password)
        layout.addWidget(password_button)

        self.setLayout(layout)

    def change_name(self):
        self.close()
        self.name_menu = NameChangeMenu(self.controller)
        self.name_menu.show()

    def change_password(self):
        dialog = PasswordChangeDialog()
        dialog.exec_()


class NameChangeMenu(QWidget):
    def __init__(self, controller_link, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Зміна імені")
        self.setGeometry(810, 460, 300, 200)
        self.controller = controller_link
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        user_data = self.controller.get_user_data_from_db()
        first_name = user_data.get("name", "")
        last_name = user_data.get("surname", "")

        self.first_name_input = QLineEdit(self)
        self.first_name_input.setText(first_name)
        self.first_name_input.setPlaceholderText("Введіть ім'я")
        layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit(self)
        self.last_name_input.setText(last_name)
        self.last_name_input.setPlaceholderText("Введіть прізвище")
        layout.addWidget(self.last_name_input)

        save_button = QPushButton("Зберегти", self)
        save_button.clicked.connect(self.save_name_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_name_changes(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        if self.controller.update_user_data(first_name, last_name):
            self.close()


class PasswordChangeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Зміна паролю")
        self.setGeometry(810, 450, 300, 200)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        password_label = QLabel("Введіть новий пароль:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        confirm_button = QPushButton("Підтвердити", self)
        confirm_button.clicked.connect(self.handle_password_change)

        main_layout = QVBoxLayout()
        main_layout.addLayout(password_layout)
        main_layout.addWidget(confirm_button)

        self.setLayout(main_layout)

    def handle_password_change(self):
        new_password = self.password_input.text()
        success = self.controller.change_password_handler(new_password)
        if success:
            self.accept()


class InstructorMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = Controller()
        self.training_form_window = None
        self.firearms_table_window = None
        self.shooter_trainings_window = None
        self.profile_menu = None
        self.setWindowTitle("Меню інструктора")
        self.setGeometry(760, 400, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("Вітаємо, інструкторе!")
        layout.addWidget(welcome_label)

        start_training_button = QPushButton("Розпочати тренування", self)
        start_training_button.clicked.connect(self.open_shooter_login_window)
        layout.addWidget(start_training_button)

        view_training_results_button = QPushButton("Переглянути тренування стрільців", self)
        view_training_results_button.clicked.connect(self.view_shooter_sessions)
        layout.addWidget(view_training_results_button)

        view_firearms_list_button = QPushButton("Переглянути список зброї", self)
        view_firearms_list_button.clicked.connect(self.view_firearms_list)
        layout.addWidget(view_firearms_list_button)
        
        edit_profile_button = QPushButton("Налаштувати профіль", self)
        edit_profile_button.clicked.connect(self.edit_profile)
        layout.addWidget(edit_profile_button)

        exit_button = QPushButton("Вийти", self)
        exit_button.clicked.connect(self.exit_menu)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def open_shooter_login_window(self):
        shooter_login_dialog = ShooterLoginWindow(self.controller, self)
        if shooter_login_dialog.exec_() == QDialog.Accepted:
            shooter_login = shooter_login_dialog.get_login()
            self.show_training_form(shooter_login)

    def show_training_form(self, shooter_login):
        self.training_form_window = TrainingFormWindow(self.controller, shooter_login)
        self.training_form_window.show()

    def view_shooter_sessions(self):
        sessions = self.controller.view_shooter_trainings()
        self.shooter_trainings_window = ShooterTrainingsWindow(sessions)
        self.shooter_trainings_window.show()

    def view_firearms_list(self):
        firearms_list = self.controller.get_firearms_list()
        self.firearms_table_window = FirearmsListWindow(firearms_list)
        self.firearms_table_window.show()
        
    def edit_profile(self):
        self.profile_menu = ProfileMenu(self.controller)
        self.profile_menu.show()

    def exit_menu(self):
        self.close()
        self.controller.clean_temp_file()
        # Перезапуск процесу view
        os.execv(sys.executable, ['python'] + sys.argv)


class ShooterLoginWindow(QDialog):
    def __init__(self, controller_link, parent=None):
        super().__init__(parent)
        self.valid_login = None
        self.controller = controller_link
        self.setWindowTitle("Введення логіну стрільця")
        self.setGeometry(810, 450, 300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Введіть логін стрільця:")
        layout.addWidget(label)

        self.login_input = QLineEdit()
        layout.addWidget(self.login_input)

        button_submit = QPushButton("Підтвердити")
        button_submit.clicked.connect(self.check_shooter_login)
        layout.addWidget(button_submit)

        button_cancel = QPushButton("Відмінити")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        self.setLayout(layout)

    def check_shooter_login(self):
        login = self.login_input.text()

        is_valid = self.controller.validate_shooter_login(login)
        if is_valid:
            self.valid_login = login
            self.accept()

    def get_login(self):
        return self.valid_login


class TrainingFormWindow(QWidget):
    def __init__(self, controller_link, shooter_login, parent=None):
        super().__init__(parent)
        self.controller = controller_link
        self.shooter_login = shooter_login
        self.setWindowTitle("Тренувальний підхід")
        self.setGeometry(750, 400, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Поле для вибору номера доріжки
        self.track_input = QLineEdit(self)
        self.track_input.setPlaceholderText("Введіть номер доріжки")
        layout.addWidget(self.track_input)

        # Поле для кількості пострілів
        self.shots_input = QLineEdit(self)
        self.shots_input.setPlaceholderText("Введіть кількість пострілів")
        layout.addWidget(self.shots_input)

        # Випадаючий список для вибору зброї
        self.weapon_combobox = QComboBox(self)
        weapons = self.controller.get_firearms()
        for weapon_id, weapon_name in weapons:
            self.weapon_combobox.addItem(weapon_name, weapon_id)
        layout.addWidget(self.weapon_combobox)

        # Кнопка початку підходу
        start_button = QPushButton("Почати підхід", self)
        start_button.clicked.connect(self.start_shooting_session)
        layout.addWidget(start_button)

    def start_shooting_session(self):
        track_number = self.track_input.text()
        shots_number = self.shots_input.text()
        weapon_id = self.weapon_combobox.currentData()

        message = self.controller.start_training_session(track_number, shots_number, weapon_id, self.shooter_login)
        QMessageBox.information(self, "Статус", message)


class ShooterTrainingsWindow(QWidget):
    def __init__(self, sessions, parent=None):
        super().__init__(parent)
        self.controller = Controller()
        self.setWindowTitle("Тренування стрільців")
        self.setGeometry(600, 300, 850, 400)
        self.sessions = sessions
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.sessions))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Середній бал", "Дата", "Ім'я стрільця", " ", " "])

        self.table.setColumnWidth(0, 50)  # Колонка "ID"
        self.table.setColumnWidth(2, 150)  # Колонка "Дата"
        self.table.setColumnWidth(4, 170)  # Колонка кнопок
        self.table.setColumnWidth(5, 180)

        for row, session in enumerate(self.sessions):
            session_id, avg_score, date, shooter_name, commentary_data = session

            # Додавання інформації до таблиці
            add_centered_item(self.table, row, 0, str(session_id))
            add_centered_item(self.table, row, 1, str(avg_score))
            add_centered_item(self.table, row, 2, str(date))
            add_centered_item(self.table, row, 3, shooter_name)

            # Кнопка "Переглянути сесію"
            view_session_button = QPushButton("Переглянути сесію")
            view_session_button.clicked.connect(partial(self.view_session, session_id))
            self.table.setCellWidget(row, 4, view_session_button)

            # Відображення кнопки "Коментарій" або "Залишити коментарій"
            if commentary_data:
                comment_button = QPushButton("Коментарій")
                comment_button.clicked.connect(partial(self.show_commentary, commentary_data))
            else:
                comment_button = QPushButton("Залишити коментарій")
                comment_button.clicked.connect(partial(self.add_commentary, session_id))

            self.table.setCellWidget(row, 5, comment_button)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def view_session(self, session_id):
        self.controller.view_training_session(session_id)

    def show_commentary(self, commentary):
        QMessageBox.information(self, "Коментарій", f"Коментарій: {commentary['commentary']}\nДата: {commentary['date']}")

    def add_commentary(self, session_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Додати коментарій")
        dialog.setGeometry(830, 400, 300, 200)

        layout = QVBoxLayout()

        label = QLabel("Введіть коментарій:")
        layout.addWidget(label)

        comment_input = QLineEdit(dialog)
        layout.addWidget(comment_input)

        submit_button = QPushButton("Додати коментарій", dialog)
        submit_button.clicked.connect(lambda: self.submit_commentary(dialog, comment_input.text(), session_id))
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def submit_commentary(self, dialog, commentary, session_id):
        if self.controller.add_instructor_commentary(session_id, commentary):
            dialog.accept()


class FirearmsListWindow(QWidget):
    def __init__(self, firearms_list, parent=None):
        super().__init__(parent)
        self.add_firearm_window = None
        self.controller = Controller()
        self.setWindowTitle("Список зброї")
        self.setGeometry(480, 300, 920, 400)
        self.firearms_list = firearms_list
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопка "Додати зброю"
        add_firearm_button = QPushButton("Додати зброю", self)
        add_firearm_button.clicked.connect(self.add_firearm)
        layout.addWidget(add_firearm_button)

        # Створюємо таблицю
        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.firearms_list))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Бренд", "Модель", "Тип", "Калібр", "Серійний номер", "", ""])

        # Ширина стовпців
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(1, 100)  # Brand
        self.table.setColumnWidth(2, 100)  # Model
        self.table.setColumnWidth(3, 100)  # Type
        self.table.setColumnWidth(4, 100)  # Caliber
        self.table.setColumnWidth(5, 150)  # Serial Number
        self.table.setColumnWidth(6, 170)
        self.table.setColumnWidth(7, 100)

        for row, firearm in enumerate(self.firearms_list):
            for col, data in enumerate(firearm):
                add_centered_item(self.table, row, col, str(data))  # Додаємо значення у таблицю

            # Кнопка "Додати модифікатор"
            add_modifier_button = QPushButton("Додати модифікатор")
            add_modifier_button.clicked.connect(partial(self.add_modifier, firearm[0]))
            self.table.setCellWidget(row, 6, add_modifier_button)

            # Кнопка "Видалити"
            delete_button = QPushButton("Видалити")
            delete_button.clicked.connect(partial(self.delete_firearm, firearm[0]))
            self.table.setCellWidget(row, 7, delete_button)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_firearm(self):
        self.add_firearm_window = AddFirearmWindow()
        self.add_firearm_window.show()

    def add_modifier(self):
        """Логіка для додавання модифікатора до зброї"""
        pass

    def delete_firearm(self, firearm_id):
        result = self.controller.delete_firearm_by_id(firearm_id)

        if result:
            # Оновлення таблиці: шукаємо рядок з таким ID та видаляємо його
            for row in range(self.table.rowCount()):
                if int(self.table.item(row, 0).text()) == firearm_id:
                    self.table.removeRow(row)
                    break


class AddFirearmWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = Controller()
        self.setWindowTitle("Додати зброю")
        self.setGeometry(750, 300, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для вводу
        self.brand_input = QLineEdit(self)
        self.brand_input.setPlaceholderText("Марка:")
        layout.addWidget(self.brand_input)

        self.model_input = QLineEdit(self)
        self.model_input.setPlaceholderText("Модель:")
        layout.addWidget(self.model_input)

        self.type_input = QLineEdit(self)
        self.type_input.setPlaceholderText("Тип:")
        layout.addWidget(self.type_input)

        self.caliber_input = QLineEdit(self)
        self.caliber_input.setPlaceholderText("Калібр:")
        layout.addWidget(self.caliber_input)

        self.serial_number_input = QLineEdit(self)
        self.serial_number_input.setPlaceholderText("Серійний номер:")
        layout.addWidget(self.serial_number_input)

        # Кнопка для додавання
        add_button = QPushButton("Додати", self)
        add_button.clicked.connect(self.add_firearm)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_firearm(self):
        brand = self.brand_input.text()
        model = self.model_input.text()
        firearm_type = self.type_input.text()
        caliber = self.caliber_input.text()
        serial_number = self.serial_number_input.text()

        result = self.controller.add_firearm_to_database(brand, model, firearm_type, caliber, serial_number)
        if result:
            self.close()


class AdminMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Меню адміністратора")
        self.setGeometry(760, 400, 400, 300)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("Вітаємо, адміністраторе!")
        layout.addWidget(welcome_label)

        view_users_button = QPushButton("Переглянути список користувачів", self)
        view_users_button.clicked.connect(self.view_user_list)
        layout.addWidget(view_users_button)

        register_button = QPushButton("Зареєструвати інструктора", self)
        register_button.clicked.connect(self.register_instructor)
        layout.addWidget(register_button)

        edit_system_config_button = QPushButton("Редагувати конфігурацію системи", self)
        edit_system_config_button.clicked.connect(self.edit_system_config)
        layout.addWidget(edit_system_config_button)

        change_password_button = QPushButton("Змінити пароль", self)
        change_password_button.clicked.connect(self.change_password)
        layout.addWidget(change_password_button)

        log_file_button = QPushButton("Лог-файл помилок", self)
        log_file_button.clicked.connect(self.open_log_file)
        layout.addWidget(log_file_button)

        exit_button = QPushButton("Вийти", self)
        exit_button.clicked.connect(self.exit_admin_menu)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def view_user_list(self):
        users_data = self.controller.get_all_users()
        dialog = UserListDialog(users_data, self.controller)
        dialog.exec_()

    def register_instructor(self):
        dialog = RegisterInstructorDialog()
        dialog.exec_()

    def edit_system_config(self):
        dialog = ConfigDialog(self.controller, self)
        dialog.exec_()

    def change_password(self):
        dialog = ChangeAdminPasswordDialog()
        dialog.exec_()

    def open_log_file(self):
        log_content = self.controller.open_log_file()
        self.show_log_file_content(log_content)

    @staticmethod
    def show_log_file_content(content):
        log_window = QDialog()
        log_window.setWindowTitle("Лог-файл помилок")
        log_window.setGeometry(590, 320, 900, 600)

        layout = QVBoxLayout()
        log_text_area = QTextEdit()
        log_text_area.setText(content)  # Відображаємо вміст файлу
        log_text_area.setReadOnly(True)  # Робимо текстове поле тільки для читання
        layout.addWidget(log_text_area)

        log_window.setLayout(layout)
        log_window.exec_()

    def exit_admin_menu(self):
        self.close()
        # Перезапуск процесу view
        os.execv(sys.executable, ['python'] + sys.argv)


class UserListDialog(QDialog):
    def __init__(self, users_data, controller_link):
        super().__init__()
        self.users_data = users_data  # Очікується список словників
        self.controller = controller_link  # Передаємо екземпляр контролера
        self.setWindowTitle("Список користувачів")
        self.setGeometry(600, 400, 800, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.users_table = QTableWidget(self)
        self.users_table.setRowCount(len(self.users_data))
        self.users_table.setColumnCount(6)  # 5 колонок для даних + 1 для кнопки
        self.users_table.setHorizontalHeaderLabels(["ID", "User Type", "Login", "Name", "Surname", "Change Password"])

        for row, user in enumerate(self.users_data):
            # Додавання даних до таблиці
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))          # ID
            self.users_table.setItem(row, 1, QTableWidgetItem(user['user_type']))       # User Type
            self.users_table.setItem(row, 2, QTableWidgetItem(user['login']))           # Login
            self.users_table.setItem(row, 3, QTableWidgetItem(user['name']))            # Name
            self.users_table.setItem(row, 4, QTableWidgetItem(user['surname']))         # Surname

            # Додавання кнопки "Змінити пароль"
            change_password_button = QPushButton("Змінити пароль", self)
            change_password_button.clicked.connect(
                partial(self.change_password, user_id=user['id'], user_type=user['user_type'])
            )
            self.users_table.setCellWidget(row, 5, change_password_button)

        layout.addWidget(self.users_table)
        self.setLayout(layout)

    def change_password(self, user_id, user_type):
        dialog = ChangeUserPasswordDialog(user_id, user_type, self.controller)
        dialog.exec_()


class ChangeUserPasswordDialog(QDialog):
    def __init__(self, user_id, user_type, controller_link):
        super().__init__()
        self.user_id = user_id
        self.user_type = user_type
        self.controller = controller_link
        self.setWindowTitle("Зміна паролю")
        self.setGeometry(800, 450, 300, 150)
        self.init_ui()

    def init_ui(self):
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        password_label = QLabel("Введіть новий пароль:", self)

        confirm_button = QPushButton("Підтвердити", self)
        confirm_button.clicked.connect(self.change_password)

        layout = QVBoxLayout()
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

    def change_password(self):
        new_password = self.password_input.text()
        success = self.controller.change_user_password(self.user_type, self.user_id, new_password)
        if success:
            self.accept()


class RegisterInstructorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Реєстрація інструктора")
        self.setGeometry(760, 450, 300, 250)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        login_label = QLabel("Введіть логін:", self)
        self.login_input = QLineEdit(self)

        login_layout = QHBoxLayout()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)

        password_label = QLabel("Введіть пароль:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        first_name_label = QLabel("Введіть ім'я:", self)
        self.first_name_input = QLineEdit(self)

        first_name_layout = QHBoxLayout()
        first_name_layout.addWidget(first_name_label)
        first_name_layout.addWidget(self.first_name_input)

        last_name_label = QLabel("Введіть прізвище:", self)
        self.last_name_input = QLineEdit(self)

        last_name_layout = QHBoxLayout()
        last_name_layout.addWidget(last_name_label)
        last_name_layout.addWidget(self.last_name_input)

        register_button = QPushButton("Зареєструвати", self)
        register_button.clicked.connect(self.handle_register)

        main_layout = QVBoxLayout()
        main_layout.addLayout(login_layout)
        main_layout.addLayout(password_layout)
        main_layout.addLayout(first_name_layout)
        main_layout.addLayout(last_name_layout)
        main_layout.addWidget(register_button)

        self.setLayout(main_layout)

    def handle_register(self):
        username = self.login_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        user_type = "instructor"

        success = self.controller.register_user(username, password, first_name, last_name, user_type)

        if success:
            self.accept()


class ConfigDialog(QDialog):
    def __init__(self, controller_link, parent=None):
        super().__init__(parent)
        self.controller = controller_link
        self.setWindowTitle("Редагування конфігурації системи")
        self.setGeometry(760, 450, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Завантаження поточних конфігурацій
        current_config = self.controller.load_config()

        # Поля вводу
        self.rings_input = QLineEdit(str(current_config["scoring_rings_number"]))
        self.critical_value_input = QLineEdit(str(current_config["scoring_critical_value"]))
        self.max_shots_amount_input = QLineEdit(str(current_config["max_shots_amount"]))

        form_layout.addRow("Кількість оціночних кілець:", self.rings_input)
        form_layout.addRow("Критичне значення оціночного балу:", self.critical_value_input)
        form_layout.addRow("Максимальна кількість влучань:", self.max_shots_amount_input)
        layout.addLayout(form_layout)

        save_button = QPushButton("Зберегти", self)
        save_button.clicked.connect(self.update_config)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def update_config(self):
        self.controller.save_config(self.rings_input.text(), self.critical_value_input.text(),
                                    self.max_shots_amount_input.text())
        self.accept()


class ChangeAdminPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Зміна пароля адміністратора")
        self.setGeometry(810, 450, 300, 200)
        self.init_ui()
        self.controller = Controller()

    def init_ui(self):
        password_label = QLabel("Введіть новий пароль:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        confirm_button = QPushButton("Підтвердити", self)
        confirm_button.clicked.connect(self.handle_password_change)

        main_layout = QVBoxLayout()
        main_layout.addLayout(password_layout)
        main_layout.addWidget(confirm_button)

        self.setLayout(main_layout)

    def handle_password_change(self):
        new_password = self.password_input.text()
        success = self.controller.change_admin_password(new_password)

        if success:
            self.accept()


