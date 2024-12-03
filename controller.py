import os
import sys
import json
import hashlib
import datetime
from PyQt5.QtWidgets import QMessageBox
from database import DatabaseManager
from camera_manager import CameraManager
from image_processor import ShotProcessingThread
from argon2 import PasswordHasher


class Controller:
    def __init__(self):
        self.database = DatabaseManager()
        self.camera_manager = CameraManager()
        self.ph = PasswordHasher()
        self.config_file = "json/config.json"
        self.current_window = None
        self.comment_window = None
        self.shot_thread = None

    # Функція для хешування паролю методом Argon2
    def hash_password(self, password):
        try:
            return self.ph.hash(password)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при шифруванні паролю: {str(e)}\n"
            self.log_error(error_message)
            return None

    def verify_password(self, hashed_password, input_password):
        try:
            return self.ph.verify(hashed_password, input_password)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при перевірці паролю: {str(e)}\n"
            self.log_error(error_message)
            return False

    def check_empty_fields(self, *fields, error_message="Всі поля повинні бути заповнені."):
        for field in fields:
            if not field:
                self.show_warning("Помилка", error_message)
                return False
        return True

    @staticmethod
    def log_error(error_message):
        log_file_path = "error_log.txt"
        try:
            with open(log_file_path, "a") as log_file:
                log_file.write(error_message)
        except Exception as e:
            print(f"Помилка при запису в лог-файл: {e}")

    def save_user_data(self, user_id, login, user_type):
        try:
            user_info = {
                "id": user_id,
                "login": login,
                "user_type": user_type
            }
            # Відкрити файл у режимі запису
            with open("json/user_data.json", "w") as file:
                json.dump(user_info, file)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при збереженні до тимчасового файлу: {str(e)}\n"
            self.log_error(error_message)

    def get_user_data(self):
        try:
            with open("json/user_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            error_message = f"{datetime.datetime.now()} Файл user_data.json не знайдено.\n"
            self.log_error(error_message)
            return None
        except Exception as e:
            error_message = f"{datetime.datetime.now()} Помилка при зчитуванні даних з файлу user_data.json: {str(e)}\n"
            self.log_error(error_message)
            return None

    def clean_temp_file(self):
        try:
            empty_data = {
                "id": "",
                "login": "",
                "user_type": ""
            }
            with open("json/user_data.json", "w") as file:
                json.dump(empty_data, file)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка очищення тимчасового файлу: {str(e)}\n"
            self.log_error(error_message)
            return False

    def register_user(self, login, password, name, surname, user_type):
        if not self.check_empty_fields(login, password, name, surname):
            return False

        if user_type not in ("shooter", "instructor"):
            self.show_warning("Помилка", "Невідомий тип користувача.")
            return False

        # Перевірка, чи не є логін "admin"
        if login == "admin":
            self.show_warning("Помилка", "Логін 'admin' недопустимий.")
            return False

        # Перевірка, чи логін вже існує в базі даних
        existing_logins = self.database.get_all_logins()
        if login in existing_logins:
            self.show_warning("Помилка", "Цей логін вже зайнятий.")
            return False

        # Хешування паролю
        hashed_password = self.hash_password(password)

        # Збереження даних у базі даних
        success = self.database.insert_user(user_type, login, hashed_password, name, surname)
        if success:
            self.show_message("Успіх", "Реєстрація успшіна.")
        else:
            self.show_warning("Помилка", "Помилка при реєстрації користувача.")
        return success

    def login_user(self, login_input, password_input):
        if not self.check_empty_fields(login_input, password_input):
            return False

        # Перевірка для адміністратора
        if login_input == "admin":
            return self.login_admin(password_input)

        # Пошук логіну в базі даних
        user_data = self.database.find_user_by_login(login_input)
        if not user_data:
            self.show_warning("Помилка", "Користувача з таким логіном не знайдено.")
            return False

        user_id, user_login, user_password, user_type = user_data

        # Перевірка паролю
        if not self.verify_password(user_password, password_input):
            return self.show_warning("Помилка", "Неправильний пароль.")

        # Збереження даних користувача у тимчасовий файл
        self.save_user_data(user_id, user_login, user_type)

        # Перехід до відповідного меню
        if user_type == "shooter":
            self.open_shooter_menu()
        elif user_type == "instructor":
            self.open_instructor_menu()
        return True

    def login_admin(self, input_password):
        try:
            # Зчитування даних адміністратора з JSON
            with open("json/admin_data.json", "r") as file:
                admin_data = json.load(file)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при завантажені даних адміністратора: {str(e)}\n"
            self.log_error(error_message)
            return False

        password = admin_data.get("password")

        if not self.verify_password(password, input_password):
            return self.show_warning("Помилка", "Неправильний пароль.")

        self.open_admin_menu()
        return True

    def open_shooter_menu(self):
        from view import ShooterMenu
        self.show_message("Успіх", "Вхід виконано. Ви увійшли як стрілець.")
        self.current_window = ShooterMenu()
        self.current_window.show()

    def open_instructor_menu(self):
        from view import InstructorMenu
        self.show_message("Успіх", "Вхід виконано. Ви увійшли як інструктор.")
        self.current_window = InstructorMenu()
        self.current_window.show()

    def open_admin_menu(self):
        from view import AdminMenu
        self.show_message("Успіх", "Вхід виконано. Ви увійшли як адміністратор.")
        self.current_window = AdminMenu()
        self.current_window.show()

    # Функція для відображення вспливаючих повідомлень
    @staticmethod
    def show_message(title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def show_warning(title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def get_user_data_from_db(self):
        user_info = self.get_user_data()

        login = user_info["login"]
        user_type = user_info["user_type"]

        return self.database.get_user_data_db(login, user_type)

    def update_user_data(self, first_name, last_name):
        if not self.check_empty_fields(first_name, last_name, error_message="Поля не можуть бути порожніми."):
            return False

        user_info = self.get_user_data()
        login = user_info["login"]
        user_type = user_info["user_type"]

        if self.database.update_user_data_db(login, user_type, first_name, last_name):
            self.show_message("Успіх", "Дані успішно змінено.")
            return True
        else:
            self.show_warning("Помилка", "Виникла помилка при зміні даних")
            return False

    def change_password_handler(self, input_password):
        user_info = self.get_user_data()
        user_id = user_info["id"]
        user_type = user_info["user_type"]
        return self.change_user_password(user_type, user_id, input_password)

    def get_training_sessions(self):
        user_info = self.get_user_data()
        shooter_id = user_info["id"]

        training_sessions = self.database.get_training_sessions_by_shooter(shooter_id)

        enriched_sessions = []
        for session in training_sessions:
            session_id = session['id']
            avg_score = session['avgHitScore']
            date = session['date']
            instructor_id = session['idInstructor']

            instructor_data = self.database.get_user_name_surname(instructor_id, 'instructor')
            instructor_name = instructor_data['name']
            instructor_surname = instructor_data['surname']
            enriched_sessions.append((session_id, avg_score, date, instructor_name, instructor_surname))

        return enriched_sessions

    def load_commentary(self, session_id):
        comment_data = self.database.get_commentary_by_session(session_id)
        if comment_data:
            commentary = comment_data['commentary']
            date = comment_data['date']
            self.show_commentary_window(commentary, date)
        else:
            self.show_message(" ", "Коментар відсутній для цієї сесії.")

    def show_commentary_window(self, commentary, date):
        from view import CommentaryWindow
        self.comment_window = CommentaryWindow(commentary, date)  # Збереження як атрибут
        self.comment_window.show()

    def view_training_session(self, session_id):
        session_data = self.database.get_target_data(session_id)

        formatted_data = []
        for target in session_data:
            target_id = target['id']
            id_firearm = target['idFirearm']
            distance = target['distance']
            shots_number = target['shotsNumber']
            avg_hit_score = target['avgHitScore']
            date = target['date']

            firearm_data = self.get_firearm_data(id_firearm)
            brand_name, model, firearm_type, caliber, serial_number = firearm_data

            weapon_info = f"{brand_name} {model}"

            formatted_data.append((target_id, distance, shots_number, avg_hit_score, weapon_info, date))

        self.show_session_details(formatted_data)

    def get_firearm_data(self, id_firearm):
        firearm_data = self.database.get_firearm_data_db(id_firearm)

        brand_name = firearm_data['brandName']
        model = firearm_data['model']
        firearm_type = firearm_data['type']
        caliber = firearm_data['caliber']
        serial_number = firearm_data['serialNumber']

        return brand_name, model, firearm_type, caliber, serial_number

    def show_session_details(self, session_details):
        from view import SessionDetailsWindow
        self.session_details_window = SessionDetailsWindow(session_details)
        self.session_details_window.show()

    def get_hits(self, target_id):
        hit_data = self.database.get_hits_by_target(target_id)

        if not hit_data:  # Перевірка на None
            self.show_warning(" ", "Для цієї мішені не зафіксовано влучань.")
            return False

        processed_hits = []

        for hit in hit_data:
            # hit_id = hit['id']
            x = hit['coordinateX']
            y = hit['coordinateY']
            score = hit['score']
            mistake_type = hit['mistakeType']
            date = hit['date']

            if mistake_type is None:
                mistake_description = "-"
            else:
                mistake_description = self.get_mistake_description(mistake_type)
            processed_hits.append((x, y, score, mistake_description, date))

        self.show_hit_details(processed_hits)

    def get_mistake_description(self, mistake_type):
        try:
            with open("json/mistake_types.json", "r", encoding="utf-8") as file:
                mistakes = json.load(file)
                return mistakes.get(str(mistake_type))
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при зчитуванні mistake_types.json: {str(e)}\n"
            self.log_error(error_message)
            return False

    def show_hit_details(self, hit_details):
        from view import HitDetailsWindow
        self.hit_window = HitDetailsWindow(hit_details)
        self.hit_window.show()

    def validate_shooter_login(self, login):
        if not self.check_empty_fields(login, error_message="Логін не може бути порожніми."):
            return False
        result = self.database.find_user_by_login(login)

        if result:
            user_id, user_login, user_password, user_type = result
            if user_type == 'shooter':
                return True
            self.show_warning("Помилка", "Введений логін не є коректним.")
            return False
        self.show_warning("Помилка", "Логін стрільця не знайдено у системі.")
        return False

    def get_firearms(self):
        firearms = self.database.get_all_firearms()

        firearms_data = []

        if firearms:
            for firearm in firearms:
                firearm_id = firearm['id']
                brand_name = firearm['brandName']
                model = firearm['model']

                firearm_name = f"{brand_name} {model}"
                firearms_data.append((firearm_id, firearm_name))

            return firearms_data
        return False

    def start_training_session(self, track_number, shots_number, weapon_id, shooter_login):
        if not self.check_empty_fields(track_number, weapon_id, shooter_login,
                                       error_message="Рядки мають бути заповненими."):
            return False

        if not self.start_camera(track_number):
            self.show_warning("Помилка", "Підключення до камери неуспішне.")
            return False

        if not shots_number:
            shots_number = self.get_max_shots_number()

        if not self.check_shots_number(int(shots_number)):
            return False

        # Функція обробки даних тренування
        self.process_training(shots_number, weapon_id, shooter_login)

        # Запуск фонового потоку для обробки влучань
        self.shot_thread = ShotProcessingThread(self, track_number, shots_number, weapon_id)
        self.shot_thread.finished.connect(self.on_training_finished)
        self.shot_thread.error.connect(self.on_training_error)
        self.shot_thread.start()

        return "Підключення успішне. Тренування розпочато."

    def get_max_shots_number(self):
        config = self.load_config()
        max_shots = config["max_shots_amount"]
        return max_shots

    def check_shots_number(self, shots_number):
        max_shots = self.get_max_shots_number()
        if shots_number > max_shots:
            self.show_warning("Помилка", f"Введена кількість пострілів більша за допустиме значення {max_shots}")
            return False
        else:
            return True

    def start_camera(self, track_number):
        return self.camera_manager.connect_to_camera(track_number)

    def process_training(self, shots_number, weapon_id, shooter_login):
        """Обробка даних тренування."""
        instructor_info = self.get_user_data()
        instructor_login = instructor_info["login"]
        # training_session_id = self.database.create_training_session(shooter_login, instructor_login, weapon_id)
        # Подальша реалізація логіки

    def handle_shot_result(self, result):
        """Обробка отриманих результатів зображень."""
        shot_number = result['shot_number']
        processed_data = result['processed_data']
        self.database_manager.save_target_data(shot_number, processed_data)

    def on_training_finished(self, message):
        print(f"[INFO]: {message}")  # Логування та реалізація логіки завершення тренування

    def on_training_error(self, message):
        print(f"[ERROR]: {message}")  # Логування та реалізація логіки обробки помилок

    def get_firearms_list(self):
        firearms = self.database.get_all_firearms()
        firearms_list = []

        if firearms:
            for firearm in firearms:
                firearm_id = firearm['id']
                brand_name = firearm['brandName']
                model = firearm['model']
                firearm_type = firearm['type']
                caliber = firearm['caliber']
                serial_number = firearm['serialNumber']

                firearms_list.append((firearm_id, brand_name, model, firearm_type, caliber, serial_number))

        return firearms_list

    def add_firearm_to_database(self, brand, model, firearm_type, caliber, serial_number):
        if not self.check_empty_fields(brand, model, firearm_type, caliber, serial_number):
            return False

        if self.database.add_firearm_db(brand, model, firearm_type, caliber, serial_number):
            self.show_message("Успіх", "Зброю успішно додано.")
            return True
        else:
            self.show_warning("Помилка", "Виникла помилка при додаванні зброї.")
            return False

    def delete_firearm_by_id(self, firearm_id):
        if self.database.delete_firearm(firearm_id):
            self.show_message("Успіх", "Зброю успішно видалено.")
            return True
        else:
            self.show_warning("Помилка", "Виникла помилка при видаленні зброї.")
            return False

    def view_shooter_trainings(self):
        user_data = self.get_user_data()
        id_instructor = user_data["id"]

        training_sessions = self.database.get_training_sessions_by_instructor(id_instructor)

        result = []
        if training_sessions:
            for session in training_sessions:
                session_id = session["id"]
                session_score = session["avgHitScore"]
                session_date = session["date"]

                commentary_result = self.database.get_commentary_by_session(session_id)

                shooter_data = self.database.get_user_name_surname(session["idShooter"], "shooter")
                shooter_name = shooter_data["name"]
                shooter_surname = shooter_data["surname"]
                shooter_info = f"{shooter_name} {shooter_surname}"

                result.append((session_id, session_score, session_date, shooter_info, commentary_result))
            return result
        return Falsec

    def add_instructor_commentary(self, session_id, commentary):
        if not self.check_empty_fields(commentary, error_message="Коменатрій не може бути порожнім."):
            return False
        user_id = self.get_user_data()["id"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.database.add_commentary_to_db(session_id, user_id, commentary, current_time):
            self.show_message("Успіх", "Коментар успішно додано.")
            return True
        else:
            self.show_warning("Помилка", "Виникла помилка при збереженні коментаря.")
            return False

    def get_all_users(self):
        users_data = self.database.fetch_all_users()
        # Перевірка, чи є дані для відображення
        if not users_data or not all(isinstance(user, dict) for user in users_data):
            error_message = f"{datetime.datetime.now()} - Дані користувачів некоректні або відсутні.\n"
            self.log_error(error_message)
            return False
        return users_data

    def change_user_password(self, user_type, user_id, new_password):
        if not self.check_empty_fields(new_password, error_message="Пароль не може бути порожнім."):
            return False

        hashed_password = self.hash_password(new_password)

        if self.database.update_password(user_type, user_id, hashed_password):
            self.show_message("Успіх", "Пароль успішно змінено.")
            return True

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при відкритті файлу config.json: {str(e)}\n"
            self.log_error(error_message)
            return False

    def save_config(self, rings_value, critical_score_value, max_shots_amount):
        try:
            new_config = {
                "scoring_rings_number": int(rings_value),
                "scoring_critical_value": int(critical_score_value),
                "max_shots_amount": int(max_shots_amount)
            }
            with open(self.config_file, "w") as file:
                json.dump(new_config, file, indent=4)
                return self.show_message("Успіх", "Конфігурацію успішно збережено!")
        except ValueError:
            self.show_warning("Помилка", "Введіть коректні числові значення!")
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Помилка при збереженні файлу config.json: {str(e)}\n"
            self.log_error(error_message)
            self.show_warning("Помилка", "Виникла помилка при збереженні файлу!")
            return False

    def change_admin_password(self, new_password):
        if not self.check_empty_fields(new_password, error_message="Пароль не може бути порожнім."):
            return False
        hashed_password = self.hash_password(new_password)
        try:
            with open("json/admin_data.json", "r") as file:
                admin_data = json.load(file)

            admin_data["password"] = hashed_password

            with open("json/admin_data.json", "w") as file:
                json.dump(admin_data, file)

            self.show_message("Успіх", "Пароль успішно змінено.")
            return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Не вдалося змінити пароль: {str(e)}\n"
            self.log_error(error_message)
            return False

    def open_log_file(self):
        log_file_path = "error_log.txt"

        try:
            with open(log_file_path, "r") as log_file:
                log_content = log_file.read()
            return log_content
        except FileNotFoundError:
            error_message = f"{datetime.datetime.now()} - Лог-файл не знайдено.\n"
            self.log_error(error_message)
            return False
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Сталася помилка при відкритті лог-файлу: {e}\n"
            self.log_error(error_message)
            return False



