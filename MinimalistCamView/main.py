from cv2 import cv2
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
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
        self.__ttk_style = ThemedStyle(self)
        self.__ttk_style.set_theme('equilux')
        self.geometry("400x300")
        self.minsize(240, 200)
        self.__showUI__cam_view()
        self.__logger.info('User Interface is ready.')

        self.__pull_frame_loop_enabled = False

    def __showUI__cam_view(self):
        self.title(h.TITLE_STR)

        # Top
        def cam_playswitch():
            if not self.__pull_frame_loop_enabled:
                self.__pull_frame_loop_enabled = True
                self.__button_play_switch.config(text=h.U_SYMBOLS['stop'])
                self.__logger.info('Begin frame pulling.')
                self.__cam_connect()
                self.__pull_frame_loop()
            else:
                self.__pull_frame_loop_enabled = False
                self.__button_play_switch.config(text=h.U_SYMBOLS['play'])
                self.__cam_capture.release()
                self.__logger.info('End frame pulling.')

        self.columnconfigure(0, weight=1)
        self.__frame_top = ttk.Frame(self)
        self.__button_play_switch = ttk.Button(self.__frame_top, text=h.U_SYMBOLS['play'], width=20, command=cam_playswitch)
        self.__button_play_switch.grid(row=0, column=0, sticky="W")
        self.__button_cams = ttk.Button(self.__frame_top, text=h.U_SYMBOLS['vertical_dots'], command=self.__showUI__cam_list, width=10)
        self.__button_cams.grid(row=0, column=2, sticky="W")
        self.__frame_top.grid(row=0, column=0, sticky="NWE")

        # Bottom
        self.rowconfigure(1, weight=1)
        self.__frame_bot = ttk.Frame(self)
        self.__frame_bot.rowconfigure(0, weight=1)
        self.__frame_bot.columnconfigure(0, weight=1)
        self.__frame_bot.grid(row=1, column=0, sticky="NSEW")

        self.__label_cam = ttk.Label(self.__frame_bot, justify=tk.CENTER)
        self.__label_cam.grid(row=0, column=0, sticky='NSEW')

    def __cam_connect(self):
        self.__cam_capture = cv2.VideoCapture(temp_config.CONNECTION)  # TODO: Read from config
        self.__logger.info("Successfully connected to cam.")

    def __pull_frame_loop(self):
        is_pulled, frame = self.__cam_capture.read()
        if is_pulled:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img_ratio = min(
                self.__label_cam.winfo_width() / img.width,
                self.__label_cam.winfo_height() / img.height
            )
            img = img.resize((round(img.width * img_ratio), round(img.height * img_ratio)), Image.ANTIALIAS)
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
                    lb_cams.insert(tk.END, cam)
            Thread(target=ucl_thread).start()

        def on_close():
            root.destroy()
            self.__button_cams.config(state=tk.NORMAL)

        self.__button_cams.config(state=tk.DISABLED)

        root = tk.Toplevel(self)
        root.geometry('300x500')
        root.title('Cams')
        root.protocol("WM_DELETE_WINDOW", on_close)

        # Left Frame
        frame_left = ttk.Frame(root)
        frame_left.grid(row=0, column=0, sticky="NSEW")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        lb_cams = tk.Listbox(frame_left, bg="#303030", selectmode=tk.SINGLE)
        lb_cams.grid(row=0, column=0, sticky="NSEW")
        lb_cams_scroll = ttk.Scrollbar(frame_left, command=lb_cams.yview)
        lb_cams.config(yscrollcommand=lb_cams_scroll.set)
        lb_cams_scroll.grid(row=0, column=1, sticky="NS")
        frame_left.rowconfigure(0, weight=1)
        frame_left.columnconfigure(0, weight=1)

        # Right Frame
        frame_right = ttk.Frame(root)
        frame_right.grid(row=0, column=1, sticky="NSEW")
        root.columnconfigure(1, weight=1)

        button_use = ttk.Button(frame_right, text="Use")
        button_edit = ttk.Button(frame_right, text="Edit")
        button_add = ttk.Button(frame_right, text="Add")
        button_use.grid(row=0, column=0, sticky="NEW")
        button_edit.grid(row=1, column=0, sticky="NEW")
        button_add.grid(row=2, column=0, sticky="NEW")
        frame_right.columnconfigure(0, weight=1)

        update_cam_list()


if __name__ == "__main__":
    logging.basicConfig(filename='MCV.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    ui = MCV_UI()
    ui.mainloop()
