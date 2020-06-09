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
    __logger = logging.getLogger('MCVConfig')

    @classmethod
    def initialize(cls):
        if not cls.is_config_exist():
            cls.create_dirs()
            cls.write(MCVCFG_PROTO)
            cls.__logger.info('Config file was created.')
        else: cls.__logger.info('Config file already exists.')

    @staticmethod
    def write(config_dict: dict):
        with open(MCVCFG_PATH_FULL, 'wt') as configfile:
            json.dump(config_dict, configfile, indent=4)

    @classmethod
    def get(cls) -> dict:
        if cls.is_config_exist():
            with open(MCVCFG_PATH_FULL, 'rt') as configfile:
                cfg = json.load(configfile)
            return cfg
        else:
            cls.__logger.error("Config file doesn't exist. Can't read values.")

    @classmethod
    def cam_add(cls, name='', address=''):
        """ Add camera to config.

        Args:
            name (str, optional): Name for the camera (Will be displayed in GUI). Defaults to ''.
            address ((str || int), optional): Address for connection. Can be string or integer. Defaults to 0 (Webcam).
        """
        cfg_dict = cls.get()
        cams_dict = cfg_dict["cam_list"]
        new_index = (max(cams_dict.keys()) + 1) if len(cams_dict.keys()) > 0 else 0

        new_cam_dict = {
            new_index: {
                "name": name,
                "address": address
            }
        }

        cams_dict.update(new_cam_dict)
        cfg_dict.update({"cam_list": cams_dict})
        cls.write(cfg_dict)
        cls.__logger.info(f"Successfully add new camera [{new_index}] to config.")

    @classmethod
    def cam_get(cls):
        # TODO
        pass

    @classmethod
    def cam_remove(cls, camera_index: int) -> bool:
        """ Remove camera from configuration file.

        Args:
            camera_index (int): Index of camera for removal.

        Returns:
            bool:
                True - camera was removed.
                False - camera doesn't exist.
        """
        cfg_dict = cls.get()
        if cfg_dict.get("cam_list", None):
            cams_dict = cfg_dict["cam_list"]
            if cams_dict.get(camera_index, None):
                del(cams_dict[camera_index])
                cfg_dict.update({"cam_list": cams_dict})
                cls.write(cfg_dict)
                cls.__logger.info(f"Camera with index {camera_index} has been removed.")
                return True
            else:
                cls.__logger.info("Can't remove unexisting camera.")
                return False

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
