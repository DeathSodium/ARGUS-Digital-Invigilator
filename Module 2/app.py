import tkinter as tk
from tkinter import simpledialog
import PIL.Image, PIL.ImageTk
import cv2 as cv
import os

import model
import camera

class App:

    def __init__(self, window=tk.Tk(), window_title="Camera Classifier"):

        self.window = window
        self.window.title(window_title)

        self.counters = [1, 1]
        self.auto_predict = False

        self.model = model.Model()
        self.camera = camera.Camera()

        self.init_gui()

        self.delay = 15
        self.update()

        self.window.attributes("-topmost", True)
        self.window.mainloop()

    def init_gui(self):

        self.canvas = tk.Canvas(
            self.window,
            width=self.camera.width,
            height=self.camera.height
        )
        self.canvas.pack()

        self.btn_auto = tk.Button(
            self.window, text="Auto Prediction",
            width=50, command=self.auto_predict_toggle
        )
        self.btn_auto.pack()

        self.classname_one = simpledialog.askstring(
            "Class 1", "Enter name of first class:", parent=self.window
        )
        self.classname_two = simpledialog.askstring(
            "Class 2", "Enter name of second class:", parent=self.window
        )

        self.btn_class1 = tk.Button(
            self.window, text=self.classname_one,
            width=50, command=lambda: self.save_for_class(1)
        )
        self.btn_class1.pack()

        self.btn_class2 = tk.Button(
            self.window, text=self.classname_two,
            width=50, command=lambda: self.save_for_class(2)
        )
        self.btn_class2.pack()

        self.btn_train = tk.Button(
            self.window, text="Train Model",
            width=50, command=lambda: self.model.train_model(self.counters)
        )
        self.btn_train.pack()

        self.btn_predict = tk.Button(
            self.window, text="Predict",
            width=50, command=self.predict
        )
        self.btn_predict.pack()

        self.btn_reset = tk.Button(
            self.window, text="Reset",
            width=50, command=self.reset
        )
        self.btn_reset.pack()

        self.class_label = tk.Label(self.window, text="CLASS", font=("Arial", 20))
        self.class_label.pack()

    def auto_predict_toggle(self):
        self.auto_predict = not self.auto_predict

    def save_for_class(self, class_num):
        ret, frame = self.camera.get_frame()
        if not ret:
            return

        os.makedirs(str(class_num), exist_ok=True)

        gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
        resized = cv.resize(gray, (150, 112))

        path = f"{class_num}/frame{self.counters[class_num - 1]}.jpg"
        cv.imwrite(path, resized)

        self.counters[class_num - 1] += 1

    def reset(self):
        for folder in ['1', '2']:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    os.unlink(os.path.join(folder, file))

        self.counters = [1, 1]
        self.model = model.Model()
        self.class_label.config(text="CLASS")

    def update(self):
        if self.auto_predict:
            self.predict()

        ret, frame = self.camera.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame)
            )
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def predict(self):
        ret, frame = self.camera.get_frame()
        if not ret:
            return

        prediction = self.model.predict(frame)

        if prediction is None:
            self.class_label.config(text="Train model first")
        elif prediction == 1:
            self.class_label.config(text=self.classname_one)
        elif prediction == 2:
            self.class_label.config(text=self.classname_two)
