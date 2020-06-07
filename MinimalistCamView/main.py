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

        self.__pull_frame_loop_enabled = False
        self.__cam_connect()
        self.__pull_frame_loop()

    def __composeUI(self):
        self.title(h.TITLE_STR)

        # Top
        def cam_playswitch():
            if not self.__pull_frame_loop_enabled:
                self.__pull_frame_loop_enabled = True
                self.__button_play_switch.config(text=h.U_SYMBOLS['pause'])
                self.__pull_frame_loop()
            else:
                self.__pull_frame_loop_enabled = False
                self.__button_play_switch.config(text=h.U_SYMBOLS['play'])

        self.__frame_top = tk.Frame(self, bg="#181818")
        self.__button_play_switch = tk.Button(self.__frame_top, text=h.U_SYMBOLS['play'], width=20, command=cam_playswitch, bg="#404040", fg="white", relief=tk.FLAT)
        self.__button_play_switch.grid(row=0, column=0, sticky="W")
        self.__frame_top.grid(row=0, column=0, sticky="NWE")

        # Bottom
        self.__frame_bot = tk.Frame(self)
        self.__frame_bot.grid(row=1, column=0)

        self.__label_cam = tk.Label(self.__frame_bot, bg='#181818')
        self.__label_cam.grid(row=0, column=0, sticky='NSEW')

    def __cam_connect(self):
        self.__cam_capture = cv2.VideoCapture('')  # TODO: Read from config

    def __pull_frame_loop(self):
        try:
            _, frame = self.__cam_capture.read()
        except cv2.error:
            self.__logger.error("Can't pull frame from camera. Trying again.")
            self.__pull_frame_loop()
        else:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.__label_cam.imgtk = imgtk
            self.__label_cam.configure(image=imgtk)

            if self.__pull_frame_loop_enabled:
                self.__label_cam.after(10, self.__pull_frame_loop)


if __name__ == "__main__":
    logging.basicConfig(filename='MCV.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    ui = MCV_UI()
    ui.mainloop()
