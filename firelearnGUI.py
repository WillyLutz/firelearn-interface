import logging
import logging.config
logging.config.fileConfig("../firelearn-interface/logging.config", disable_existing_loggers=True)
import os

from matplotlib import pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

logger = logging.getLogger("__main__")

from scripts import main
if __name__ == '__main__':
    main.main()
    # exit()

# to generate the distribution for linux, with the venv activated
# >>> pyinstaller firelearnGUI.spec
# >>> y

# to run the distribution
# >>> cd ../dist/firelearnGUI
# >>> ./firelearnGUI

# to generate the distribution for windows,
# pyinstaller --noconfirm --onedir firelearnGUI.py --add-data "C:\Users\wlutz\PycharmProjects\firelearn-interface\venv\Lib\site-packages\customtkinter;customtkinter." --add-data "C:\Users\wlutz\PycharmProjects\firelearn-interface\data;data"
