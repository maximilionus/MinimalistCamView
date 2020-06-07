import os
import json
import logging


# CONST
TITLE_STR = "Minimalist Cam View"
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
    "vertical_dots": "\u22EE"
}


class MCVConfig:
    __logging = logging.getLogger('MCVConfig')

    @classmethod
    def create(cls):
        if not cls.is_exist():
            os.makedirs(MCVCFG_PATH)
            with open(os.path.join(MCVCFG_PATH, MCVCFG_NAME), 'wt') as configfile:
                json.dump(MCVCFG_PROTO, configfile, indent=4)
            cls.__logging.info('Config file was created')
        else: cls.__logging.info('Config file already exists')

    @classmethod
    def get(cls) -> dict:
        if cls.is_exist():
            with open(MCVCFG_PATH_FULL, 'rt') as configfile:
                cfg = json.load(configfile)
            return cfg
        else:
            cls.__logging.error("Config file doesn't exist. Can't read values.")

    @staticmethod
    def is_exist() -> bool:
        return True if os.path.exists(MCVCFG_PATH) and os.path.exists(MCVCFG_PATH_FULL) else False
