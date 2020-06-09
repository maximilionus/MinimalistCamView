import os
import json
import logging
from cv2 import cv2
from threading import Thread


# CONST
TITLE_STR = "Minimalist Cam View"
ICON_APP = "./data/icons/mcv_icon.ico"
MCVCFG_PATH = "./data/config"
MCVCFG_NAME = "config.json"
MCVCFG_PATH_FULL = os.path.join(MCVCFG_PATH, MCVCFG_NAME)
MCVCFG_PROTO = {
    "cam_selected": "",
    "cam_list": {}
}
U_SYMBOLS = {
    "play": "\u25B6",
    "stop": "\u23f9",
    "vertical_dots": "\u22EE",
    "record": "\u23FA"
}


class MCVConfig:
    __logging = logging.getLogger('MCVConfig')

    @classmethod
    def create(cls):
        if not cls.is_config_exist():
            cls.create_dirs()
            with open(os.path.join(MCVCFG_PATH, MCVCFG_NAME), 'wt') as configfile:
                json.dump(MCVCFG_PROTO, configfile, indent=4)
            cls.__logging.info('Config file was created')
        else: cls.__logging.info('Config file already exists')

    @classmethod
    def get(cls) -> dict:
        if cls.is_config_exist():
            with open(MCVCFG_PATH_FULL, 'rt') as configfile:
                cfg = json.load(configfile)
            return cfg
        else:
            cls.__logging.error("Config file doesn't exist. Can't read values.")

    @staticmethod
    def create_dirs() -> bool:
        if not os.path.isdir(MCVCFG_PATH):
            os.makedirs(MCVCFG_PATH)

    @staticmethod
    def is_config_exist():
        return True if os.path.isfile(MCVCFG_PATH_FULL) else False


class MCVVideoRecord:
    __logger = logging.getLogger("MCV_VideoRecord")

    def __init__(self, stream: object):
        self.is_recording = False
        self.__stream = stream
        self.__logger.info("Object is ready.")

    def record(self):
        def record_thread():
            self.__init_writer()
            while self.is_recording:
                frame = self.__pull_frame()
                self.__writer.write(frame)
                # sleep(0.01)
            self.__writer.release()
            self.__logger.debug("Writer released. End of record.")
            return 0

        self.is_recording = True
        Thread(target=record_thread).start()
        self.__logger.info("Begin record.")

    def stop(self):
        self.is_recording = False
        self.__logger.info("Recording was stopped. Result saved to file.")

    def __init_writer(self):
        w, h = self.__get_frame_size()

        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        self.__writer = cv2.VideoWriter('output.avi', fourcc, 25, (w, h))
        self.__logger.debug("Writer initialized.")

    def __pull_frame(self) -> object:
        is_pulled, frame = self.__stream.read()
        return frame if is_pulled else self.__pull_frame()

    def __get_frame_size(self) -> tuple:
        w = int(self.__stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.__stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        return (w, h)
