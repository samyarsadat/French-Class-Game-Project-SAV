#  French Class Project Game Website JSON models file.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.

"""JSON models for the French Class Project Game Website.

"""


# ------- JSON models -------

# -=-=-= Game player =-=-=-
class GamePlayer():
    name: str
    score: int

    def __init__(self, name: str, score: int):
        self.name = name
        self.score = score


    # ---- Convert model to a JSON serializable object ----
    def as_json(self) -> dict:
        return {"name": self.name, "score": self.score}
    
    
    # ---- Convert to model from a JSON serializable object ----
    def from_json(dict: dict):
        return GamePlayer(dict["name"], dict["score"])


# -=-=-= Gamedata question =-=-=-
class GameDataQuestion():
    question_html: str
    correct_answer_id: int
    answer_opts_html: list[str]
    category_id: int
    points: int
    is_multiplier: bool
    multiplier_selec_amount: int
    is_enabled: bool
    picked_by_id: int
    is_timed_out: bool
    buzzed_by_id: int
    attempted_answer_by_id: list[int]
    answered_by_id: int

    def __init__(self, question_html: str, correct_answer_id: int, answer_opts_html: str, category_id: int, points: int, is_multiplier: bool, multiplier_selec_amount: int, is_enabled: bool, picked_by_id: int, is_timed_out: bool, buzzed_by_id:int, attempted_answer_by_id: list[int], answered_by_id: int):
        self.question_html = question_html
        self.correct_answer_id = correct_answer_id
        self.answer_opts_html = answer_opts_html
        self.category_id = category_id
        self.points = points
        self.is_multiplier = is_multiplier
        self.multiplier_selec_amount = multiplier_selec_amount
        self.is_enabled = is_enabled
        self.picked_by_id = picked_by_id
        self.is_timed_out = is_timed_out
        self.buzzed_by_id = buzzed_by_id
        self.attempted_answer_by_id = attempted_answer_by_id
        self.answered_by_id = answered_by_id
        

    # ---- Convert model to a JSON serializable object ----
    def as_json(self) -> dict:
        return {"question_html": self.question_html, "correct_answer_id": self.correct_answer_id, "answer_opts_html": self.answer_opts_html, "category_id": self.category_id, "points": self.points, "is_multiplier": self.is_multiplier, "multiplier_selec_amount": self.multiplier_selec_amount, "is_enabled": self.is_enabled, "picked_by_id": self.picked_by_id, "is_timed_out": self.is_timed_out, "buzzed_by_id": self.buzzed_by_id, "attempted_answer_by_id": self.attempted_answer_by_id, "answered_by_id": self.answered_by_id}
    
    
    # ---- Convert to model from a JSON serializable object ----
    def from_json(dict: dict):
        return GameDataQuestion(dict["question_html"], dict["correct_answer_id"], dict["answer_opts_html"], dict["category_id"], dict["points"], dict["is_multiplier"], dict["multiplier_selec_amount"], dict["is_enabled"], dict["picked_by_id"], dict["is_timed_out"], dict["buzzed_by_id"], dict["attempted_answer_by_id"], dict["answered_by_id"])
    
    
# -=-=-= Game question =-=-=-
class GameQuestion():
    question_html: str
    correct_answer_id: int
    answer_opts_html: list[str]
    category_id: int
    points: int

    def __init__(self, question_html: str, correct_answer_id: int, answer_opts_html: str, category_id: int, points: int):
        self.question_html = question_html
        self.correct_answer_id = correct_answer_id
        self.answer_opts_html = answer_opts_html
        self.category_id = category_id
        self.points = points
        

    # ---- Convert model to a JSON serializable object ----
    def as_json(self) -> dict:
        return {"question_html": self.question_html, "correct_answer_id": self.correct_answer_id, "answer_opts_html": self.answer_opts_html, "category_id": self.category_id, "points": self.points}
    
    
    # ---- Convert to model from a JSON serializable object ----
    def from_json(dict: dict):
        return GameQuestion(dict["question_html"], dict["correct_answer_id"], dict["answer_opts_html"], dict["category_id"], dict["points"])