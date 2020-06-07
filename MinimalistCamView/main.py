from cv2 import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
import logging

from MinimalistCamView import helpers as h
from MinimalistCamView import temp_config


class MCV_UI(tk.Tk):
    def __init__(self):
        super().__init__()
        h.MCVConfig.create()
        self.__logger = logging.getLogger('MCV_UI')
        self.__showUI__cam_view()
        self.__logger.info('User Interface is ready')

        self.__pull_frame_loop_enabled = False
        self.__cam_connect()
        self.__pull_frame_loop()

    def __showUI__cam_view(self):
        self.title(h.TITLE_STR)

        # Top
        def cam_playswitch():
            if not self.__pull_frame_loop_enabled:
                self.__pull_frame_loop_enabled = True
                self.__button_play_switch.config(text=h.U_SYMBOLS['pause'])
                self.__pull_frame_loop()
                self.__logger.info('Begin frame pulling.')
            else:
                self.__pull_frame_loop_enabled = False
                self.__button_play_switch.config(text=h.U_SYMBOLS['play'])
                self.__logger.info('End frame pulling.')

        self.__frame_top = tk.Frame(self, bg="#181818")
        self.__button_play_switch = tk.Button(self.__frame_top, text=h.U_SYMBOLS['play'], width=20, command=cam_playswitch, bg="#404040", fg="#ffffff", relief=tk.FLAT)
        self.__button_play_switch.grid(row=0, column=0, sticky="W")
        self.__button_cams = tk.Button(self.__frame_top, text=h.U_SYMBOLS['vertical_dots'], command=self.__showUI__cam_list, bg="#404040", fg="#ffffff", relief=tk.FLAT, width=10)
        self.__button_cams.grid(row=0, column=2, sticky="W")
        self.__frame_top.grid(row=0, column=0, sticky="NWE")

        # Bottom
        self.__frame_bot = tk.Frame(self)
        self.__frame_bot.grid(row=1, column=0)

        self.__label_cam = tk.Label(self.__frame_bot, bg='#181818')
        self.__label_cam.grid(row=0, column=0, sticky='NSEW')

    def __cam_connect(self):
        self.__cam_capture = cv2.VideoCapture(temp_config.CONNECTION)  # TODO: Read from config

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

    def __showUI__cam_list(self):
        def update_cam_list():
            def ucl_thread():
                cams = h.MCVConfig.get()["cam_list"].keys()
                for cam in cams:
                    listbox.insert(tk.END, cam)
            Thread(target=update_cam_list).start()

        root = tk.Toplevel(self)
        root.title('Settings')
        listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        update_cam_list()


if __name__ == "__main__":
    logging.basicConfig(filename='MCV.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    ui = MCV_UI()
    ui.mainloop()
