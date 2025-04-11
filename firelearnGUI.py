import logging
import logging.config

import os
import sys

import logging
import logging.config
import sys

logging_dict = {
    'version': 1,
    'formatters': {
        'consoleFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M'
        },
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'consoleFormatter',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'  # Correct way to specify sys.stdout
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['consoleHandler'],  # List of handlers
    },
    'disable_existing_loggers': True,
}

logging.config.dictConfig(logging_dict)

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
