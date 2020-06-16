import logging
from time import strftime
from sys import argv, exit as sysexit
from os import mkdir


if __name__ == "__main__":
    if "--quiet" not in argv:
        try: mkdir("./Logs")
        except FileExistsError: pass
        logging.basicConfig(filename=f'./Logs/MCV-{strftime("%Y-%m-%d__%H-%M-%S")}.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    logger = logging.getLogger("MCV.Boot")

    if '--only-record' in argv:
        logger.info("Running in no-gui recording mode.")
        from MinimalistCamView.helpers import MCVVideoRecord, MCVConfig
        from MinimalistCamView.helpers import MCVCFG_PATH_FULL

        if not MCVConfig.is_config_exist():
            MCVConfig.initialize()
            MCVConfig.cam_add("Change my name", "Change my address")
            MCVConfig.cam_use(0)
            print(f"\n----\nConfiguration file with template camera was created : < {MCVCFG_PATH_FULL} >.\n\nSince this is the first run and you don't use gui, you will have to configure the configuration json file by yourself and then start this app again.\n----\n")
            sysexit()
        else:
            recorder = MCVVideoRecord()
            recorder.record()
            input("----\n>> Press [Enter] to stop recording <<\n")
            print("Stopping the recording process.\n----")
            recorder.stop()
            sysexit()
    else:
        logger.info("Running in default gui mode.")
        from MinimalistCamView.Gui import run
        run()
