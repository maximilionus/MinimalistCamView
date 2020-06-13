import logging
from time import strftime
from sys import argv, exit as sexit

if __name__ == "__main__":
    logging.basicConfig(filename=f'MCV-{strftime("%Y-%m-%d__%H-%M-%S")}.log', filemode='w', level=logging.NOTSET, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
    logger = logging.getLogger("MCV_Boot")

    if '--no-gui-record' in argv:
        logger.info("Running in no-gui recording mode.")
        from MinimalistCamView.helpers import MCVVideoRecord, MCVConfig
        MCVConfig.initialize()
        recorder = MCVVideoRecord()
        recorder.record()
        input("PRESS ENTER TO STOP RECORDING")
        recorder.stop()
        sexit()
    else:
        logger.info("Running in default gui mode.")
        from MinimalistCamView.Gui import run
        run()
