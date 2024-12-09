#  French Class Project Game Website quiz module.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.

"""Data file handling module for the French Class Project Game Website.

"""


# ------- Libraries and utils -------
import os
import json
from flask import Blueprint
from config import AppConfig
from init import log
from utils.models import GameDataQuestion


# ------- Blueprint init -------
data = Blueprint("data", __name__, template_folder="../templates", static_folder="../static")


# ------- Global veriables -------
WORKING_DIR = AppConfig.WORKING_DIR
GAMEDATA_PATH = AppConfig.WORKING_DIR + AppConfig.GAMEDATA_DIR
QUESTIONS_PATH = AppConfig.WORKING_DIR + AppConfig.QUESTION_DATA_DIR


# ------- Data functions -------

# ---- List all saved game files ----
def list_saved_games(with_ext: bool):
    games = []
    
    for file in os.listdir(GAMEDATA_PATH):
        if os.path.isfile(GAMEDATA_PATH + file) and file.endswith(".json"):
            if not with_ext:
                games.append(file.replace(".json", ""))
                
            else:
                games.append(file)
    
    return games


# ------- Storage models -------

# ---- Gamedata file ----
class GameDataFile():
    players: list[dict]
    datetime: str
    categories: list[str]
    questions: list[dict]
    tiebreaker_question: dict
    current_board_owner_id: int
    won_by_id: int
    max_questions_per_cat: int
    points_increment: int

    def __init__(self, players: list[dict], datetime: str, categories: list[str], questions: list[dict], tiebreaker_question: dict, current_board_owner_id: int, won_by_id: int, max_questions_per_cat: int, points_increment: int):
        self.players = players
        self.datetime = datetime
        self.categories = categories
        self.questions = questions
        self.tiebreaker_question = tiebreaker_question
        self.current_board_owner_id = current_board_owner_id
        self.won_by_id = won_by_id
        self.max_questions_per_cat = max_questions_per_cat
        self.points_increment = points_increment
        
        
    # ---- Convert model to a JSON serializable object ----
    def as_json(self) -> dict:
        return {"players": self.players, "datetime": self.datetime, "categories": self.categories, "questions": self.questions, "tiebreaker_question": self.tiebreaker_question, "current_board_owner_id": self.current_board_owner_id, "won_by_id": self.won_by_id, "max_questions_per_cat": self.max_questions_per_cat, "points_increment": self.points_increment}
    
    
    # ---- Convert to model from a JSON serializable object ----
    def from_json(dict: dict):
        return GameDataFile(dict["players"], dict["datetime"], dict["categories"], dict["questions"], dict["tiebreaker_question"], dict["current_board_owner_id"], dict["won_by_id"], dict["max_questions_per_cat"], dict["points_increment"])
    
    
    # -=-=-= Read, write and delete =-=-=-
    # ---- Read gamedata from json file ----
    def read(filename_noext: str):
        try:
            with open(f"{GAMEDATA_PATH}{filename_noext}.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            log.debug(f"Gamedata file read: {filename_noext}")
            return GameDataFile.from_json(data)

        except Exception:
            log.exception("GameDataReadException")
            return False
    
    
    # ---- Update gamedata on json file ----
    def update(self, filename_noext: str) -> bool:
        try:
            with open(f"{GAMEDATA_PATH}{filename_noext}.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            data.update(self.as_json())

            with open(f"{GAMEDATA_PATH}{filename_noext}.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                
            log.debug(f"Gamedata file updated: {filename_noext}")
            return True

        except Exception:
            log.exception("GameDataWriteException")
            return False
        
        
    # ---- Create new gamedata file ----
    def create_new(self, filename_noext: str) -> bool:
        try:
            open(f"{GAMEDATA_PATH}{filename_noext}.json", "x")

            with open(f"{GAMEDATA_PATH}{filename_noext}.json", "w", encoding="utf-8") as file:
                json.dump(self.as_json(), file, indent=4, ensure_ascii=False)
                
            log.debug(f"Gamedata file created: {filename_noext}")
            return True

        except Exception:
            log.exception("GameDataCreateException")
            return False
        

    # ---- Delete gamedata file ----
    def delete(filename_noext: str) -> bool:
        try:
            os.remove(f"{GAMEDATA_PATH}{filename_noext}.json")
            log.debug(f"Gamedata file deleted: {filename_noext}")
            return True

        except Exception:
            log.exception("GameDataDeleteException")
            return False
        
        
# ---- Game questions file ----
class GameQuestions():
    question_pack_name: str
    categories: list[str]
    questions: list[dict]
    tiebreaker_questions: list[dict]
    points_increment: int

    def __init__(self, question_pack_name: str, categories: list[str], questions:list[dict], tiebreaker_questions: list[dict], points_increment: int):
        self.question_pack_name = question_pack_name
        self.categories = categories
        self.questions = questions
        self.tiebreaker_questions = tiebreaker_questions
        self.points_increment = points_increment
        
        
    # ---- Convert model to a JSON serializable object ----
    def as_json(self) -> dict:
        return {"question_pack_name": self.question_pack_name, "categories": self.categories, "questions": self.questions, "tiebreaker_questions": self.tiebreaker_questions, "points_increment": self.points_increment}
    
    
    # ---- Convert to model from a JSON serializable object ----
    def from_json(dict: dict):
        return GameQuestions(dict["question_pack_name"], dict["categories"], dict["questions"], dict["tiebreaker_questions"], dict["points_increment"])
    
    
    # -=-=-= Read, write and delete =-=-=-
    # ---- Read gamedata from json file ----
    def read(filename_noext: str):
        try:
            with open(f"{QUESTIONS_PATH}{filename_noext}.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            log.debug(f"Game questions file read: {filename_noext}")
            return GameQuestions.from_json(data)

        except Exception:
            log.exception("GameQuestionsReadException")
            return False
    
    
    # ---- Update gamedata on json file ----
    def update(self, filename_noext: str) -> bool:
        try:
            with open(f"{QUESTIONS_PATH}{filename_noext}.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            data.update(self.as_json())

            with open(f"{QUESTIONS_PATH}{filename_noext}.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                
            log.debug(f"Game questions file updated: {filename_noext}")
            return True

        except Exception:
            log.exception("GameQuestionsWriteException")
            return False
        
        
    # ---- Create new gamedata file ----
    def create_new(self, filename_noext: str) -> bool:
        try:
            open(f"{QUESTIONS_PATH}{filename_noext}.json", "x")

            with open(f"{QUESTIONS_PATH}{filename_noext}.json", "w", encoding="utf-8") as file:
                json.dump(self.as_json(), file, indent=4, ensure_ascii=False)
                
            log.debug(f"Game questions file created: {filename_noext}")
            return True

        except Exception:
            log.exception("GameQuestionsCreateException")
            return False
        

    # ---- Delete gamedata file ----
    def delete(filename_noext: str) -> bool:
        try:
            os.remove(f"{QUESTIONS_PATH}{filename_noext}.json")
            log.debug(f"Game questions file deleted: {filename_noext}")
            return True

        except Exception:
            log.exception("GameQuestionsDeleteException")
            return False