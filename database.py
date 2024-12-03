import datetime
import mysql.connector
from mysql.connector import Error
import pymysql as sql


class DatabaseManager:

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 3306
        self.user = "root"
        self.password = "root"
        self.database = "shootingdb"
        self.connection = None

    def connect(self):
        try:
            self.connection = sql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=sql.cursors.DictCursor
            )
            print("Successfully connected to database.")
        except Exception as ex:
            error_message = f"{datetime.datetime.now()} - Connection to database failed: {str(ex)}\n"
            self.log_error(error_message)

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print("Connection closed.")
            except Exception as ex:
                error_message = f"{datetime.datetime.now()} - Failed to close connection: {str(ex)}\n"
                self.log_error(error_message)

    @staticmethod
    def log_error(error_message):
        log_file_path = "error_log.txt"
        try:
            with open(log_file_path, "a") as log_file:
                log_file.write(error_message)
        except Exception as e:
            print(f"Помилка при запису в лог-файл: {e}")

    # Функція для отримання всіх логінів з бази даних
    def get_all_logins(self):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT login FROM shooter UNION SELECT login FROM instructor"
                cursor.execute(query)
                result = cursor.fetchall()
                return [row['login'] for row in result]
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching logins: {str(e)}\n"
            self.log_error(error_message)
            return False
        finally:
            self.close_connection()

    # Функція для збереження нового користувача в базі даних
    def insert_user(self, user_type, login, password, name, surname):
        self.connect()
        try:
            # Виконання запиту на збереження нового користувача
            with self.connection.cursor() as cursor:
                query = f"INSERT INTO {user_type} (login, password, name, surname) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (login, password, name, surname))
                self.connection.commit()
                print("User successfully registered.")
                return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error saving user: {str(e)}\n"
            self.log_error(error_message)
            self.connection.rollback()
            return False
        finally:
            self.close_connection()

    def find_user_by_login(self, login):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                # Пошук логіну серед таблиць shooter та instructor
                query_shooter = "SELECT id, login, password, 'shooter' AS user_type FROM shooter WHERE login = %s"
                query_instructor = "SELECT id, login, password, 'instructor' AS user_type FROM instructor WHERE login = %s"

                cursor.execute(query_shooter, (login,))
                result_shooter = cursor.fetchone()

                if result_shooter:
                    return result_shooter["id"], result_shooter["login"], result_shooter["password"], \
                        result_shooter["user_type"]

                cursor.execute(query_instructor, (login,))
                result_instructor = cursor.fetchone()

                if result_instructor:
                    return result_instructor["id"], result_instructor["login"], result_instructor["password"], \
                        result_instructor["user_type"]

                return False
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error finding user in database: {str(e)}\n"
            self.log_error(error_message)
            return False
        finally:
            self.close_connection()

    def fetch_all_users(self):
        self.connect()
        try:
            query = """
            (SELECT id, 'shooter' as user_type, login, name, surname FROM shooter)
            UNION
            (SELECT id, 'instructor' as user_type, login, name, surname FROM instructor)
            """
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            return result
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching all users: {str(e)}\n"
            self.log_error(error_message)
            return []
        finally:
            self.close_connection()

    def update_password(self, user_type, user_id, new_password):
        self.connect()
        try:
            table = "shooter" if user_type == "shooter" else "instructor"
            query = f"UPDATE {table} SET password = %s WHERE id = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (new_password, user_id))
                self.connection.commit()
            return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error when changing password: {str(e)}\n"
            self.log_error(error_message)
            self.connection.rollback()
            return False
        finally:
            self.close_connection()

    def get_user_data_db(self, login, user_type):
        self.connect()
        try:
            query = f"SELECT name, surname FROM {user_type} WHERE login = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (login,))
                result = cursor.fetchone()
                if result:
                    return result
                else:
                    return {"name": "", "surname": ""}
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error getting user data: {str(e)}\n"
            self.log_error(error_message)
            self.connection.rollback()
            return False
        finally:
            self.close_connection()

    def update_user_data_db(self, login, user_type, first_name, last_name):
        self.connect()
        try:
            query = f"UPDATE {user_type} SET name = %s, surname = %s WHERE login = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (first_name, last_name, login))
                self.connection.commit()
                return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error updating user data: {str(e)}\n"
            self.log_error(error_message)
            self.connection.rollback()
            return False
        finally:
            self.close_connection()

    def get_training_sessions_by_shooter(self, shooter_id):
        self.connect()
        try:
            query = "SELECT id, avgHitScore, date, idInstructor FROM training_session WHERE idShooter = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (shooter_id,))
                result = cursor.fetchall()
                return result
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching all training sessions: {str(e)}\n"
            self.log_error(error_message)
            return []
        finally:
            self.close_connection()

    def get_user_name_surname(self, user_id, user_type):
        self.connect()
        try:
            query = f"SELECT name, surname FROM {user_type} WHERE id = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error getting instructor data: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_commentary_by_session(self, session_id):
        self.connect()
        try:
            query = "SELECT commentary, date FROM instructor_commentary WHERE idTrainingSession = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (session_id,))
                return cursor.fetchone()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching commentary: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_target_data(self, session_id):
        self.connect()
        try:
            query = "SELECT id, idFirearm, distance, shotsNumber, avgHitScore, date FROM target WHERE idTrainingSession = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (session_id,))
                return cursor.fetchall()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching targets: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_firearm_data_db(self, firearm_id):
        self.connect()
        try:
            query = "SELECT * FROM Firearm WHERE id = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (firearm_id,))
                return cursor.fetchone()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error geting firearm data: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_hits_by_target(self, target_id):
        self.connect()
        try:
            query = "SELECT * FROM hit WHERE idTarget = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (target_id,))
                return cursor.fetchall()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching hits: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_all_firearms(self):
        self.connect()
        try:
            query = "SELECT * FROM firearm"
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error fetching firearms: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def add_firearm_db(self, brand, model, firearm_type, caliber, serial_number):
        self.connect()
        try:
            query = "INSERT INTO Firearm (brandName, model, type, caliber, serialNumber) VALUES (%s, %s, %s, %s, %s)"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (brand, model, firearm_type, caliber, serial_number))
                self.connection.commit()
                return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error adding firearm: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def delete_firearm(self, firearm_id):
        self.connect()
        try:
            query = "DELETE FROM Firearm WHERE id = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (firearm_id,))
                self.connection.commit()
                return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error deleting firearm: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def get_training_sessions_by_instructor(self, id_instructor):
        self.connect()
        try:
            query = "SELECT id, avgHitScore, date, idShooter FROM training_session WHERE idInstructor = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (id_instructor,))
                return cursor.fetchall()
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error getting training sessions for instructor: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()

    def add_commentary_to_db(self, session_id, instructor_id, commentary, date):
        self.connect()
        try:
            query = "INSERT INTO instructor_commentary (idTrainingSession, idInstructor, commentary, date) " \
                    "VALUES (%s, %s, %s, %s)"
            with self.connection.cursor() as cursor:
                values = (session_id, instructor_id, commentary, date)
                cursor.execute(query, values)
                self.connection.commit()
                return True
        except Exception as e:
            error_message = f"{datetime.datetime.now()} - Error inserting commentary: {str(e)}\n"
            self.log_error(error_message)
            return None
        finally:
            self.close_connection()



# if __name__ == '__main__':
#     db = DatabaseManager()
#     db.connect()
#     db.close_connection()


