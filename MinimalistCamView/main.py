from cv2 import cv2
import tkinter as tk
from PIL import Image, ImageTk
import logging

from MinimalistCamView import helpers as h


class MCV_UI(tk.Tk):
    def __init__(self):
        super().__init__()
        h.MCVConfig.create()
        self.__logger = logging.getLogger('MCV_UI')
        self.__composeUI()
        self.__logger.info('User Interface is ready')
        self.__pull_frame_loop()

    def __composeUI(self):
        self.title(h.TITLE_STR)
        self.__label_cam = tk.Label(self, bg='#181818')
        self.__label_cam.grid(row=0, column=0, sticky='NSEW')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.__cam_capture = cv2.VideoCapture('')  # TODO: Read from config

    def __pull_frame_loop(self):
        _, frame = self.__cam_capture.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.__label_cam.imgtk = imgtk
        self.__label_cam.configure(image=imgtk)
        self.__label_cam.after(10, self.__pull_frame_loop)


if __name__ == "__main__":
    logging.basicConfig(filename='MCV.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")

    ui = MCV_UI()
    ui.mainloop()
