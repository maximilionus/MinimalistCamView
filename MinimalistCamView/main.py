import logging
import tkinter as tk
from threading import Thread

from cv2 import cv2
from PIL import Image, ImageTk

from MinimalistCamView import helpers as h


class MCV_UI(tk.Tk):
    HEXC_BG = "#262626"
    HEXC_BG_BRIGHTER = "#303030"
    HEXC_FG = "#afafaf"

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('MCV_UI')
        h.MCVConfig.initialize()
        self.iconbitmap(h.ICON_APP)
        self.geometry("400x300")
        self.minsize(240, 200)
        self.createui__cam_view()
        self.__logger.info('User Interface is ready.')

        self.__pull_frame_loop_enabled = False

    def createui__cam_view(self):
        self.title(h.TITLE_STR)

        # Top
        def cam_playswitch():
            if not self.__pull_frame_loop_enabled:
                self.__pull_frame_loop_enabled = True
                self.__button_play_switch.config(text=h.U_SYMBOLS['stop'])
                self.__logger.info('Begin frame pulling.')
                self.__cam_connect()
                self.pull_frame_loop()
            else:
                self.__pull_frame_loop_enabled = False
                self.__button_play_switch.config(text=h.U_SYMBOLS['play'])
                self.__cam_capture.release()
                self.__logger.info('End frame pulling.')

        self.columnconfigure(0, weight=1)
        self.__frame_top = tk.Frame(self, bg=self.HEXC_BG_BRIGHTER)
        self.__button_play_switch = tk.Button(self.__frame_top, text=h.U_SYMBOLS['play'], width=20, bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT, command=cam_playswitch)
        self.__button_play_switch.grid(row=0, column=0, sticky="W")
        self.__button_record = tk.Button(self.__frame_top, text=h.U_SYMBOLS["record"], width=10, bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT, command=self.__recordSwitch)
        self.__button_record.grid(row=0, column=1, sticky="W")
        self.__button_cams = tk.Button(self.__frame_top, text=h.U_SYMBOLS['vertical_dots'], bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT, command=self.createui__cam_list, width=10)
        self.__button_cams.grid(row=0, column=2, sticky="W")
        self.__frame_top.grid(row=0, column=0, sticky="WE")

        # Bottom
        self.rowconfigure(1, weight=1)
        self.__frame_bot = tk.Frame(self, bg=self.HEXC_BG)
        self.__frame_bot.rowconfigure(0, weight=1)
        self.__frame_bot.columnconfigure(0, weight=1)
        self.__frame_bot.grid(row=1, column=0, sticky="NSEW")

        self.__label_cam = tk.Label(self.__frame_bot, bg=self.HEXC_BG, justify=tk.CENTER)
        self.__label_cam.grid(row=0, column=0, sticky='NSEW')
        self.__lcam_text_status = tk.Label(self.__label_cam, text="", fg=self.HEXC_FG, bg=self.HEXC_BG_BRIGHTER, font="40")
        self.set_lcam_banner(1)
        self.__label_cam.rowconfigure(0, weight=1)
        self.__label_cam.columnconfigure(0, weight=1)

    def __recordSwitch(self):
        if not hasattr(self, "__recorder"):
            self.__recorder = h.MCVVideoRecord(self.__cam_capture)
            self.__recorder.record()
        else:
            self.__recorder.stop()

    def __cam_connect(self):
        cfg_dict = h.MCVConfig.get()
        selected_cam = cfg_dict.get("cam_selected", 0)
        address = cfg_dict["cam_list"][str(selected_cam)].get("address", 0)

        self.__cam_capture = cv2.VideoCapture(address)
        if self.__cam_capture.isOpened():
            self.__logger.info("Successfully connected to cam.")
        else:
            self.set_lcam_banner(3)
            self.__logger.error("Can't connect to cam")

    def set_lcam_banner(self, status: int):
        """ Set status line

        Args:
            status (int):
                0 - Hide status bar.
                1 - NOT CONNECTED.
                2 - DISCONNECTED.
                3 - CONNECTION ERROR.
        """
        if status == 0:
            self.__lcam_text_status.grid_remove()
        else:
            if status == 1:
                self.__lcam_text_status.config(text='NOT CONNECTED')
            elif status == 2:
                self.__lcam_text_status.config(text='DISCONNECTED')
            elif status == 3:
                self.__lcam_text_status.config(text='CONNECTION ERROR')

            if not self.__lcam_text_status.grid_info():
                self.__lcam_text_status.grid(row=0, column=0, sticky="EW")

    def pull_frame_loop(self):
        is_pulled, frame = self.__cam_capture.read()
        if is_pulled:
            self.set_lcam_banner(0)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img_ratio = min(
                self.__label_cam.winfo_width() / img.width,
                self.__label_cam.winfo_height() / img.height
            )
            img = img.resize((round(img.width * img_ratio), round(img.height * img_ratio)), Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.__label_cam.imgtk = imgtk
            self.__label_cam.config(image=imgtk)

        if self.__pull_frame_loop_enabled:
            self.__label_cam.after(10, self.pull_frame_loop)
        else:
            self.set_lcam_banner(2)
            del(self.__label_cam.imgtk)
            self.__label_cam.config(image=None)

    def createui__cam_list(self):
        def update_cam_list():
            def ucl_thread():
                cams_cfg = h.MCVConfig.get()["cam_list"]
                cams_list = cams_cfg.keys()
                for cam in cams_list:
                    lb_cams.insert(tk.END, cams_cfg[cam].get("name", "No name"))
            Thread(target=ucl_thread).start()

        def on_close():
            root.destroy()
            self.__button_cams.config(state=tk.NORMAL)

        self.__button_cams.config(state=tk.DISABLED)

        root = tk.Toplevel(self)
        root.geometry('300x500')
        root.title('Cams')
        root.iconbitmap(h.ICON_APP)
        root.protocol("WM_DELETE_WINDOW", on_close)

        # Left Frame
        def get_camlbox_selected():
            selection = lb_cams.curselection()
            if len(selection) > 0:
                return selection[0]
            else:
                return 0

        frame_left = tk.Frame(root, bg=self.HEXC_BG)
        frame_left.grid(row=0, column=0, sticky="NSEW")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        lb_cams = tk.Listbox(frame_left, bg="#303030", fg="#bfbfbf", selectmode=tk.SINGLE)
        lb_cams.grid(row=0, column=0, sticky="NSEW")
        lb_cams_scroll = tk.Scrollbar(frame_left, command=lb_cams.yview)
        lb_cams.config(yscrollcommand=lb_cams_scroll.set)
        lb_cams_scroll.grid(row=0, column=1, sticky="NS")
        frame_left.rowconfigure(0, weight=1)
        frame_left.columnconfigure(0, weight=1)

        # Right Frame
        def useCam():
            cfg_dict = h.MCVConfig.get()
            selected_cam = get_camlbox_selected()
            cfg_dict["cam_selected"] = selected_cam
            h.MCVConfig.write(cfg_dict)

        frame_right = tk.Frame(root, bg=self.HEXC_BG)
        frame_right.grid(row=0, column=1, sticky="NSEW")
        root.columnconfigure(1, weight=1)

        button_use = tk.Button(frame_right, text="Use", bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT, command=useCam)
        button_edit = tk.Button(frame_right, text="Edit", bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT)
        button_add = tk.Button(frame_right, text="Add", bg=self.HEXC_BG_BRIGHTER, fg=self.HEXC_FG, relief=tk.FLAT)
        button_use.grid(row=0, column=0, sticky="NEW")
        button_edit.grid(row=1, column=0, sticky="NEW")
        button_add.grid(row=2, column=0, sticky="NEW")
        frame_right.columnconfigure(0, weight=1)

        update_cam_list()


if __name__ == "__main__":
    logging.basicConfig(filename='MCV.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    ui = MCV_UI()
    ui.mainloop()
