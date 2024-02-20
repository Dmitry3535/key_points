import cv2
import numpy as np
import json
import os

class DrawPolygonOnImages:
    def __init__(self, folder_path, points_folde):
        self.folder_path = folder_path
        self.image_paths = [os.path.join(self.folder_path, img) for img in os.listdir(self.folder_path) if img.endswith(('.png', '.jpg'))]
        self.points_folder = points_folder

    def mouse_callback(self, event, x, y, flags, params):
        image_resized = params['image_resized']
        points = params['points']

        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            for i in range(len(points)-1):
                cv2.line(image_resized, points[i], points[i+1], (0, 0, 255), 2)
                cv2.circle(image_resized, points[i], 3, (0, 255, 0), -1)
            cv2.circle(image_resized, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow('image', image_resized)

    def resize_image(self, image, scale_percent=30):
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    def draw_polygon_and_save_points(self, img_path):
        image = cv2.imread(img_path)
        image_resized = self.resize_image(image)

        cv2.imshow('image', image_resized)
        points = []
        cv2.setMouseCallback('image', self.mouse_callback, {'image_resized': image_resized, 'points': points})

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                if len(points) >= 2:
                    cv2.line(image_resized, points[0], points[-1], (0, 0, 255), 2)
                    cv2.imshow('image', image_resized)
                    points.append(points[0])  # Замыкаем полигон
                    points_json_path = os.path.join(self.points_folder, os.path.splitext(os.path.basename(img_path))[0] + ".json")
                    with open(points_json_path, "w") as file:
                        json.dump(points, file)
                    print(f"Сохранены координаты полигона для {img_path}.")

            elif key == ord('n'):
                break

        cv2.destroyAllWindows()
        return key

    def process_images(self):
        for img_path in self.image_paths:
            key = self.draw_polygon_and_save_points(img_path)
            if key == ord('q'):
                break
            elif key == ord('n'):
                continue


folder_path = "start_fotos"
points_folder = "points_poligon_1"
draw_tool = DrawPolygonOnImages(folder_path, points_folder)
draw_tool.process_images()
