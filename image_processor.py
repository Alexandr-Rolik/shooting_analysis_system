import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class ShotProcessingThread(QThread):
    processed_result = pyqtSignal(dict)  # Сигнал для передачі результатів обробки
    finished = pyqtSignal(str)  # Сигнал успішного завершення
    error = pyqtSignal(str)     # Сигнал помилки

    def __init__(self, controller, track_number, shots_number, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.track_number = track_number
        self.shots_number = shots_number
        self.running = True  # Контроль завершення потоку

    def run(self):
        try:
            for shot_number in range(int(self.shots_number)):
                if not self.running:
                    break

                # Захоплення зображення
                image = self.controller.camera_manager.capture_image(self.track_number)
                if image is None:
                    raise Exception(f"Не вдалося захопити зображення для пострілу {shot_number + 1}")

                # Обробка зображення
                processed_data = self.process_image(image)

                # Відправка результату до контролера
                self.processed_result.emit({
                    'shot_number': shot_number + 1,
                    'processed_data': processed_data
                })

            self.finished.emit("Обробка всіх пострілів завершена успішно.")
        except Exception as e:
            self.error.emit(f"Помилка під час обробки пострілів: {str(e)}")

    def stop(self):
        """Метод для зупинки потоку коректно."""
        self.running = False

    def process_image(self, image):
        """Метод для обробки зображення за допомогою OpenCV та алгоритмів модуля аналізу."""
        # Перетворення зображення в градації сірого
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Попередня обробка: розмиття
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # Пошук контурів мішені
        _, thresholded = cv2.threshold(blurred_image, 100, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Аналіз контурів для пошуку координат влучань
        hit_coordinates = []
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if 5 < radius < 50:  # Відсікання занадто великих або малих об'єктів
                hit_coordinates.append((int(x), int(y)))

        # Формування результатів
        return {
            'coordinates': hit_coordinates,
            'image': image  # Може бути збережено або передано для візуалізації
        }