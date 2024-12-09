#  French Class Project Game Website flask and flask plugin config file.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.


# ------- Libraries -------
import logging
import os


class AppConfig():
    # ------- Flask config -------
    SECRET_KEY = "AjkhgAgjhAJJKHAjggaiuy786AygAygAGgyya9iAOAF87a"
    SEND_FILE_MAX_AGE_DEFAULT = 0
    DEBUG = False

    # ------- Module configs -------
    GAME_QUESTION_TIME = 30                  # IN SECONDS
    GAME_ANSWER_TIME = 6                     # IN SECONDS
    MAX_QUESTIONS_PER_CAT = 4
    GAME_MAX_PLAYERS = 4
    GAME_MIN_PLAYERS = 2
    GAME_MIN_CATEGORIES = 3
    FIND_QUESTION_RETRY_COUNT = 200
    LOG_FILE_PATH = "logs/"                  # THERE MUST BE A "/" AFTER THE PATH
    LOG_LEVEL = logging.DEBUG
    GAMEDATA_DIR = "/data/gamedata/"         # THERE MUST BE A "/" AFTER AND BEFORE THE PATH
    QUESTION_DATA_DIR = "/data/questions/"   # THERE MUST BE A "/" AFTER AND BEFORE THE PATH
    FILE_NAME_DATETIME_AUTO_FORMAT = "%d-%m-%Y_%H-%M-%S"
    WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
    QUESTION_PACK = "DEFAULT_PACK"