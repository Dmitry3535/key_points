import cv2
import os

# Укажите путь к вашему видео и папку для сохранения кадров
video_path = "179_part_1.mp4"
output_folder = "start_fotos"

# Открытие видеофайла
cap = cv2.VideoCapture(video_path)

# Перемещение указателя на начальный кадр
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


# Цикл по кадрам с шагом 500
num  = 0
num_frames_skip = 10
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Сохранение кадра, если его номер кратен 500
    if ((num) % 50 == 0) and (num > 1):
        cv2.imwrite(os.path.join(output_folder, f"frame_{num*10}.jpg"), frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

        # Пропуск нескольких кадров между итерациями
    for _ in range(num_frames_skip):
        ret, frame = cap.read()
        if not ret:
            break

    num += 1
    print(f"Номер итерации : {num}")

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()
