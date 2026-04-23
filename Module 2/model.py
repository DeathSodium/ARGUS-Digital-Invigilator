from sklearn.svm import LinearSVC
import numpy as np
import cv2 as cv
import os

class Model:

    def __init__(self):
        self.model = LinearSVC()
        self.trained = False
        self.img_size = (150, 112)  # width, height

    def _process_image(self, img):
        gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        resized = cv.resize(gray, self.img_size)
        return resized.flatten()

    def train_model(self, counters):
        img_list = []
        class_list = []

        for i in range(1, counters[0]):
            path = f'1/frame{i}.jpg'
            if os.path.exists(path):
                img = cv.imread(path)
                img_list.append(self._process_image(img))
                class_list.append(1)

        for i in range(1, counters[1]):
            path = f'2/frame{i}.jpg'
            if os.path.exists(path):
                img = cv.imread(path)
                img_list.append(self._process_image(img))
                class_list.append(2)

        if len(img_list) == 0:
            print("No training data found!")
            return

        self.model.fit(np.array(img_list), np.array(class_list))
        self.trained = True
        print("✅ Model successfully trained!")

    def predict(self, frame):
        if not self.trained:
            return None

        img = self._process_image(frame)
        prediction = self.model.predict([img])
        return prediction[0]
