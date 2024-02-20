import cv2
import numpy as np
import json
import time
import os

class VideoPolygonDrawer:
    def __init__(self, video_path, points_path, start_foto, start_frame_number):
        self.start_frame_number = start_frame_number
        self.path_start_points = points_path                  # путь к папке "points_poligon_1"
        self.start_foto = start_foto                    # путь к фото "frame_0.jp"
        self.list_start_poligons = os.listdir(self.path_start_points)
        self.list_start_poligons.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame_number)  # Установка начального кадра
        self.prev_points = self.load_points(self.list_start_poligons[0])  # загружаем точки из frame_00.json
        self.prev_frame = self.resize_image(cv2.imread(start_foto))  # начальное фото frame_0.jpg

        self.frame = None
        self.points_list = None
        self.frame_count = 0



    def resize_image(self, image, scale_percent=30):
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        return resized_image

    def load_points(self, file_pname):
        file_path = os.path.join(self.path_start_points, file_pname)
        with open(file_path, "r") as file:
            points = json.load(file)
            return points

    def find_homography_and_transform_points(self):
        # Перевод абсолютных координат точек в формат OpenCV
        print("Загрузка стартовых точек полигона :")
        print(self.prev_points)
        points_img1 = np.array(self.prev_points).astype(np.float32).reshape(-1, 1, 2)

        # Инициализация детектора ключевых точек (например, SIFT, ORB)
        detector = cv2.SIFT_create()
        # detector = cv2.ORB_create()
        # detector = cv2.AKAZE_create()

        # Нахождение ключевых точек и их дескрипторов на обоих изображениях
        keypoints1, descriptors1 = detector.detectAndCompute(self.prev_frame, None)
        keypoints2, descriptors2 = detector.detectAndCompute(self.frame, None)

        # Сопоставление дескрипторов ключевых точек между изображениями
        matcher = cv2.BFMatcher()
        matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

        # Фильтрация сопоставлений с помощью метода лучших соответствий
        good_matches = []
        for m, n in matches:
            if m.distance < 0.3 * n.distance:
                good_matches.append(m)

        # Проверка, что найдено достаточно хороших сопоставлений
        if len(good_matches) > 10:
            # Формирование массивов точек из хороших сопоставлений
            src_points = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_points = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Нахождение гомографии между изображениями на основе сопоставленных точек с помощью метода RANSAC
            homography_matrix, _ = cv2.findHomography(src_points[:, :2], dst_points[:, :2], cv2.RANSAC)

            # Применение гомографии к координатам точек изображения 1 для получения их координат на изображении 2
            self.transformed_points = cv2.perspectiveTransform(points_img1, homography_matrix)
            print("Применение гомографии к точкам 1 для получение координат 2")
            print(self.transformed_points)
            self.points_list = self.transformed_points.squeeze().astype(int).tolist()


        else:
            print("Недостаточно хороших сопоставлений для нахождения гомографии.")

    # def save_points_to_file(self, points):
    #     with open(self.points_path, "w") as file:
    #         json.dump(points.tolist(), file)

    def process_video(self):
        num = 0
        num_frames_skip = 10  # Количество кадров, которые пропускаются между итерациями
        print(f"Начало обработки кадр : {self.start_frame_number}")
        iter_points = iter(self.list_start_poligons[1:])
        while self.cap.isOpened():

            ret, frame = self.cap.read()
            if not ret:
                break

            # Уменьшение размера кадра до 30% от исходного
            self.frame = self.resize_image(frame)


            self.find_homography_and_transform_points()

            print(f"Точки образца : {self.prev_points}")
            print(f"Новые точки : {self.points_list}")
            print()
            cv2.polylines(self.frame, [np.array(self.points_list)], isClosed=True, color=(0, 255, 0), thickness=2)

            cv2.imshow('Video with Polygon', self.frame)
            print(f"Номер кадра {self.frame_count}")
            if ((num ) % 50 == 0) and (num > 1):
                print("Меняем точки 500")
                path = os.path.join(self.path_start_points, next(iter_points))
                print(path)
                with open(path, "r") as file:
                    self.prev_points = json.load(file)
                    print("Новые точки 500")
                    print(self.prev_points)
                # Сохранение текущего кадра в переменной prev_frame
                self.prev_frame = self.frame.copy()


            if num % 3 == 0:
                print("Сменили стартовые точки")
                self.prev_points = self.points_list.copy()
                # Сохранение текущего кадра в переменной prev_frame
                self.prev_frame = self.frame.copy()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Пропуск нескольких кадров между итерациями
            for _ in range(num_frames_skip):
                ret, frame = self.cap.read()
                if not ret:
                    break
            self.frame_count += 1
            num += 1
            print(f"Номер итерации : {num}")

        self.cap.release()
        cv2.destroyAllWindows()


video_path = "179_part_1.mp4"
points_path = "points_poligon_1"
start_foto = "start_fotos/frame_0.jpg"
start_frame_number = 0  # Установка номера начального

p_1 = VideoPolygonDrawer(video_path, points_path, start_foto, start_frame_number)
p_1.process_video()
# print(p_1.list_start_poligons)
# print(p_1.start_foto)

