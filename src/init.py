#  French Class Project Game Website application init file.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.


# ------- Libraries -------
import logging
from flask import Flask
from config import AppConfig


# ------- Flask and Flask plug-in init -------
app = Flask(__name__)
app.config.from_object(AppConfig)


# -=-=-= Logging init =-=-=-
formatter = logging.Formatter("[%(asctime)s] [%(threadName)s/%(levelname)s] [%(module)s/%(funcName)s]: %(message)s")

# ---- Get a logger with custom settings ----
def get_logger(name, log_file, level):
    handler = logging.FileHandler(AppConfig.LOG_FILE_PATH + log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


waitress_logger = get_logger("waitress", "FRGS_WaitressPyLog.log", logging.DEBUG)
log = get_logger("main", "FRGS_ProgramPyLog.log", AppConfig.LOG_LEVEL)