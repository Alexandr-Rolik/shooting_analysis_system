import logging


class CameraManager:
    def __init__(self):
        # Ініціалізація системи камер
        logging.basicConfig(level=logging.INFO)
        self.connected_cameras = {}

    def connect_to_camera(self, track_number):
        """
        Підключається до камери за вказаним номером доріжки.
        :param track_number: Номер доріжки, до якої необхідно підключитися.
        :return: True, якщо підключення успішне, інакше False.
        """
        try:
            # Симуляція пошуку та підключення до камери
            if track_number in self.connected_cameras:
                logging.warning(f"Камера для доріжки {track_number} вже підключена.")
                return True

            # Симуляція успішного підключення
            logging.info(f"Підключення до камери на доріжці {track_number}...")
            # У реальному коді тут буде виклик функції підключення до фізичної камери
            self.connected_cameras[track_number] = f"Camera_{track_number}"
            logging.info(f"Успішно підключено до камери на доріжці {track_number}.")
            return True
        except Exception as e:
            logging.error(f"Помилка підключення до камери на доріжці {track_number}: {e}")
            return False

    def disconnect_from_camera(self, track_number):
        """
        Відключається від камери за вказаним номером доріжки.
        :param track_number: Номер доріжки, від якої необхідно відключитися.
        :return: True, якщо відключення успішне, інакше False.
        """
        try:
            if track_number in self.connected_cameras:
                logging.info(f"Відключення від камери на доріжці {track_number}...")
                del self.connected_cameras[track_number]
                logging.info(f"Успішно відключено від камери на доріжці {track_number}.")
                return True
            else:
                logging.warning(f"Камера на доріжці {track_number} не підключена.")
                return False
        except Exception as e:
            logging.error(f"Помилка відключення від камери на доріжці {track_number}: {e}")
            return False

