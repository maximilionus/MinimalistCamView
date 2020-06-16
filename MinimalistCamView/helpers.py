import os
import json
import logging
from cv2 import cv2
import multiprocessing as mp
from time import strftime


# CONST
ICON_APP = os.path.abspath("./data/icons/mcv_icon.png")
TITLE_STR = "Minimalist Cam View"
RECORD_FOLDER = os.path.abspath("./Recordings")  # TODO: Make configurable in future
MCVCFG_PATH = os.path.abspath("./data/config")
MCVCFG_NAME = "config.json"
MCVCFG_PATH_FULL = os.path.normpath(os.path.join(MCVCFG_PATH, MCVCFG_NAME))
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
    __logger = logging.getLogger('MCV.Config')

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
    def cam_add(cls, name='', address=0):
        """ Add camera to config.

        Args:
            name (str, optional): Name for the camera (Will be displayed in GUI). Defaults to "".
            address ((str || int), optional): Address for connection. Can be string or integer. Defaults to 0 (Webcam).
        """
        cfg_dict = cls.get()
        cams_dict = cfg_dict["cam_list"]
        cams_indexes = [int(i) for i in cams_dict.keys()]
        new_index = str((max(cams_indexes) + 1)) if len(cams_dict.keys()) > 0 else "0"

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
    def cam_update(cls, camera_index: int, name: str, address: str):
        cfg_dict = cls.get()
        cfg_dict["cam_list"].get(str(camera_index), 0).update({"name": name, "address": address})
        cls.write(cfg_dict)

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
        camera_index = str(camera_index)
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

    @classmethod
    def cam_get(cls, camera_index: int) -> dict:
        """ Get camera dictionary by it's index.

        Args:
            camera_index (int): Index of existing camera in "cam_list"

        Returns:
            dict: Dictionary with camera information keys.
            None: if camera with this index doesn't exist.
        """
        cfg_dict = cls.get()
        cam_selected = cfg_dict["cam_list"].get(str(camera_index), None)
        return cam_selected

    @classmethod
    def cam_use(cls, camera_index: int):
        cfg_dict = cls.get()
        cfg_dict.update({"cam_selected": camera_index})
        cls.write(cfg_dict)

    @staticmethod
    def create_dirs() -> bool:
        if not os.path.isdir(MCVCFG_PATH):
            os.makedirs(MCVCFG_PATH)

    @staticmethod
    def is_config_exist():
        return True if os.path.isfile(MCVCFG_PATH_FULL) else False


class MCVVideoRecord:
    __logger = logging.getLogger("MCV.VideoRecord")

    def __init__(self):
        self.is_recording = mp.Value('i', 0)
        self.__logger.info("Object is ready.")

    def record(self):
        if not os.path.exists(RECORD_FOLDER):
            os.makedirs(RECORD_FOLDER)
            self.__logger.info("Create folder for recordings")

        self.is_recording.value = 1
        mp.Process(target=self.record_process, args=(self.is_recording,), name="MCV Stream Recorder").start()
        self.__logger.info("Begin record in detached process.")

    def stop(self):
        self.is_recording.value = 0
        self.__logger.info("Recording was stopped. Result saved to file.")

    @classmethod
    def record_process(cls, is_recording: mp.Value):
        def __pull_frame() -> object:
            is_pulled, frame = stream.read()
            return frame if is_pulled else __pull_frame()

        def __get_frame_size() -> tuple:
            w = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (w, h)

        # Initialize Connection
        selected_cam = str(MCVConfig.get()['cam_selected'])
        cam_address = MCVConfig.cam_get(selected_cam)["address"]
        stream = cv2.VideoCapture(cam_address)
        if not stream.isOpened(): return 1

        # Initialize Writer
        record_name = f'{RECORD_FOLDER}/{strftime("%Y-%m-%d__%H-%M-%S")}.avi'
        w, h = __get_frame_size()
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        writer = cv2.VideoWriter(record_name, fourcc, 25, (w, h))
        cls.__logger.debug("Writer initialized.")

        # Write frames to file
        while is_recording.value == 1:
            frame = __pull_frame()
            writer.write(frame)

        writer.release()
        cls.__logger.debug("Writer released. End of record.")
        return 0
