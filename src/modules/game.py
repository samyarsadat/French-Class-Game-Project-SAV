#  French Class Project Game Website game module.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.

"""Game module for the Samyar Projects Website.

"""


# ------- Libraries and utils -------
import datetime
from config import AppConfig
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from modules.data import GameDataFile
from init import log
from utils.models import GameDataQuestion, GamePlayer


# ------- Blueprint init -------
game_pages = Blueprint("game_pages", __name__, template_folder="../templates", static_folder="../static")


# ------- Global variables -------
current_game_filename = None
tied_player_ids = None


# ------- Page routes -------
@game_pages.route("/file/<filename>")
def load_game(filename):
    filedata = GameDataFile.read(filename)
    
    if filedata:
        global current_game_filename
        global tied_player_ids
        
        if current_game_filename and current_game_filename != filename:
            flash(f'Il y a un autre jeu actif en cours. <a href="{url_for("game_pages.reset_game", next=filename)}">Cliquez ici pour passer outre.</a> Le remplacement peut entraîner la corruption du fichier de jeu.', "warning")
            return redirect(url_for("index"))
        
        if not filedata.players:
            return redirect(url_for("set_game_names", filename=filename))
        
        current_game_filename = filename
        
        if filedata.current_board_owner_id == None:
            filedata.current_board_owner_id = 0
            if not filedata.update(filename):
                log.warning(f"Failed to set board owner. Game name: [{filename}]")
                abort(500)
                
        set_win = True
                
        for quest in filedata.questions:
            quest = GameDataQuestion.from_json(quest)
                
            if quest.is_enabled:
                set_win = False
                break
                
        if set_win:
            highest_score = None
            player_won_id = None
            player_tied_with_player_ids = []
                
            for index, player in enumerate(filedata.players):
                if not highest_score:
                    highest_score = player["score"]
                    player_won_id = index
                    
                if player["score"] > highest_score:
                    highest_score = player["score"]
                    player_won_id = index
                    
            for index, player in enumerate(filedata.players):
                if player["score"] == highest_score and index != player_won_id:
                    player_tied_with_player_ids.append(index)
                    
            if player_tied_with_player_ids:
                log.debug(f"Tied players, redirecting to tied player page. Game name: [{filename}] - Tied players: {player_tied_with_player_ids + [player_won_id]}")
                tied_player_ids = player_tied_with_player_ids + [player_won_id]
                return redirect(url_for(".players_tied", filename=filename))
                    
            filedata.won_by_id = player_won_id
            if not filedata.update(filename):
                log.warning(f"Failed to set win status. Game name: [{filename}]")
                abort(500)
                
            tied_player_ids = None
            
        return render_template("game_pages/questions_board.html", gamedata=filedata, filename=filename)
    
    log.debug(f"Attempted to open a game that does not exist. Game name: [{filename}]")
    flash(f"Un jeu avec le nom <strong>{filename}</strong> n'existe pas.", "warning")
    abort(404)
    
    
@game_pages.route("/file/<filename>/question/<quest_id>", methods=["POST", "GET"])
def load_question(filename, quest_id):
    global current_game_filename
    
    if filename == current_game_filename:
        filedata = GameDataFile.read(filename)
        
        if filedata:
            try:
                question = filedata.questions[int(quest_id)]
                question = GameDataQuestion.from_json(question)
                
            except Exception:
                log.debug(f"Attempted to open a question that does not exist. Game name: [{filename}] - QID: [{quest_id}]")
                flash("ID de question non valide.", "warning")
                abort(404)
            
            if request.method == "GET":   
                if question.is_enabled:
                    filedata.questions[int(quest_id)]["is_enabled"] = False
                    filedata.questions[int(quest_id)]["picked_by_id"] = filedata.current_board_owner_id
                    
                    if filedata.update(filename):
                        return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None)
                    
                log.warning(f"Attempted to open a question that is disabled or question data write failed. Game name: [{filename}] - QID: [{quest_id}]")
                abort(500)
                    
            else:
                buzz_player = request.form.get("player")
                answer = request.form.get("answ")
                
                if answer == "ANSW_TIMEOUT":
                    filedata.questions[int(quest_id)]["is_timed_out"] = True
                    filedata.questions[int(quest_id)]["is_enabled"] = False
                    
                    if filedata.update(filename):
                        log.debug(f"Question timed out. Game name: [{filename}] - QID: [{quest_id}]")
                        return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=True, actual_answ=None, buzzed=False, buzzed_by=None)
                    
                    log.warning(f"Attempted to set time out for a question but failed. Game name: [{filename}] - QID: [{quest_id}]")
                    abort(500)
                    
                elif answer == "ANSW_BUZZED_TIMEOUT":
                    return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None)
                    
                elif buzz_player:
                    log.debug(f"Player buzzed. Player: [{buzz_player}] - Game name: [{filename}] - QID: [{quest_id}]")
                    
                    if not filedata.questions[int(quest_id)]["buzzed_by_id"]:
                        filedata.questions[int(quest_id)]["buzzed_by_id"] = []
                        
                    if filedata.players[int(buzz_player)] in filedata.questions[int(quest_id)]["buzzed_by_id"]:
                        return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None)
                    
                    filedata.questions[int(quest_id)]["buzzed_by_id"].append(filedata.players[int(buzz_player)])
                    if filedata.update(filename):
                        return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=False, actual_answ=None, buzzed=True, buzzed_by=int(buzz_player))
                    
                    log.warning(f"Attempted to set buzz status for a question but failed. Game name: [{filename}] - QID: [{quest_id}]")
                    abort(500)
                    
                elif int(answer.split("_")[1]) in range(0, AppConfig.MAX_QUESTIONS_PER_CAT):
                    s_answer = answer.split("_")
                    
                    if not question.answered_by_id and filedata.players[int(s_answer[2])] not in filedata.questions[int(quest_id)]["attempted_answer_by_id"]:
                        if not filedata.questions[int(quest_id)]["attempted_answer_by_id"]:
                            filedata.questions[int(quest_id)]["attempted_answer_by_id"] = []
                        
                        if question.correct_answer_id == int(s_answer[1]):
                            filedata.players[int(s_answer[2])]["score"] += question.points
                            filedata.questions[int(quest_id)]["attempted_answer_by_id"].append(int(s_answer[2]))
                            filedata.questions[int(quest_id)]["answered_by_id"] = int(s_answer[2])
                            filedata.current_board_owner_id = int(s_answer[2])
                            
                            if filedata.update(filename):
                                return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=True, actual_answ=int(s_answer[1]), buzzed=False, buzzed_by=None)
                            
                            log.warning(f"Attempted to write question correct answer data but failed. Game name: [{filename}] - QID: [{quest_id}]")
                            abort(500)
                            
                        else:
                            filedata.players[int(s_answer[2])]["score"] -= question.points
                            filedata.questions[int(quest_id)]["attempted_answer_by_id"].append(int(s_answer[2]))
                            filedata.current_board_owner_id = int(s_answer[2])
                            
                            if filedata.update(filename):
                                return render_template("game_pages/question.html", filedata=filedata, filename=filename, quest_id=int(quest_id), show_answer=True, actual_answ=int(s_answer[1]), buzzed=False, buzzed_by=None)
                            
                            log.warning(f"Attempted to write question wrong answer data but failed. Game name: [{filename}] - QID: [{quest_id}]")
                            abort(500)
                            
                    log.debug(f"Attempted to open already answered question. Game name: [{filename}] - QID: [{quest_id}]")
                    abort(405)
                    
                else:
                    abort(404)
    
    log.debug(f"Attempted to open a question from a game that is not open. Game name: [{filename}] - QID: [{quest_id}]")
    flash("Le nom du jeu ne correspond pas au jeu actuellement actif.", "warning")
    abort(404)
    
    
@game_pages.route("/file/<filename>/players-tied")
def players_tied(filename):
    global current_game_filename
    global tied_player_ids
    
    if filename == current_game_filename:
        if tied_player_ids:
            filedata = GameDataFile.read(filename)
            
            if filedata:
                return render_template("game_pages/tied_players.html", filename=filename, gamedata=filedata, tied_player_ids=tied_player_ids)
        
        log.debug(f"Attempted to open players tied page but no players are tied. Game name: [{filename}]")
        flash("Il n'y a pas de joueurs actuellement à égalité.", "warning")
        abort(404)
    
    log.debug(f"Attempted to open players tied page from a game that is not open. Game name: [{filename}]")
    flash("Le nom du jeu ne correspond pas au jeu actuellement actif.", "warning")
    abort(404)
    
    
@game_pages.route("/file/<filename>/question/tiebreaker", methods=["POST", "GET"])
def load_tiebreaker(filename):
    global current_game_filename
    global tied_player_ids
    
    if filename == current_game_filename:
        if tied_player_ids:
            filedata = GameDataFile.read(filename)
            
            if filedata:
                try:
                    question = filedata.tiebreaker_question
                    question = GameDataQuestion.from_json(question)
                    
                except Exception:
                    log.debug(f"Attempted to open a question that does not exist. Game name: [{filename}] - Tiebreaker")
                    flash("ID de question non valide.", "warning")
                    abort(404)
                
                if request.method == "GET":   
                    if question.is_enabled:
                        filedata.tiebreaker_question["is_enabled"] = False
                        
                        if filedata.update(filename):
                            return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None, tied_player_ids=tied_player_ids)
                        
                    log.warning(f"Attempted to open a question that is disabled or question data write failed. Game name: [{filename}] - Tiebreaker")
                    abort(500)
                        
                else:
                    buzz_player = request.form.get("player")
                    answer = request.form.get("answ")
                        
                    if answer == "ANSW_BUZZED_TIMEOUT":
                        return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None, tied_player_ids=tied_player_ids)
                        
                    elif buzz_player:
                        log.debug(f"Player buzzed. Player: [{buzz_player}] - Game name: [{filename}] - Tiebreaker")
                        
                        if not filedata.tiebreaker_question["buzzed_by_id"]:
                            filedata.tiebreaker_question["buzzed_by_id"] = []
                            
                        if filedata.tiebreaker_question["buzzed_by_id"]:
                            if filedata.players[int(buzz_player)] == filedata.tiebreaker_question["buzzed_by_id"][-1]:
                                return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_answer=False, actual_answ=None, buzzed=False, buzzed_by=None, tied_player_ids=tied_player_ids)
                        
                        filedata.tiebreaker_question["buzzed_by_id"].append(filedata.players[int(buzz_player)])
                        if filedata.update(filename):
                            return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_answer=False, actual_answ=None, buzzed=True, buzzed_by=int(buzz_player), tied_player_ids=tied_player_ids)
                        
                        log.warning(f"Attempted to set buzz status for a question but failed. Game name: [{filename}] - Tiebreaker")
                        abort(500)
                        
                    elif int(answer.split("_")[1]) in range(0, AppConfig.MAX_QUESTIONS_PER_CAT):
                        s_answer = answer.split("_")
                        
                        if not question.answered_by_id and filedata.players[int(s_answer[2])] not in filedata.tiebreaker_question["attempted_answer_by_id"]:
                            if not filedata.tiebreaker_question["attempted_answer_by_id"]:
                                filedata.tiebreaker_question["attempted_answer_by_id"] = []
                            
                            if question.correct_answer_id == int(s_answer[1]):
                                filedata.players[int(s_answer[2])]["score"] += question.points
                                filedata.tiebreaker_question["attempted_answer_by_id"].append(int(s_answer[2]))
                                filedata.tiebreaker_question["answered_by_id"] = int(s_answer[2])
                                
                                if filedata.update(filename):
                                    return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_answer=True, actual_answ=int(s_answer[1]), buzzed=False, buzzed_by=None, tied_player_ids=tied_player_ids)
                                
                                log.warning(f"Attempted to write question correct answer data but failed. Game name: [{filename}] - Tiebreaker")
                                abort(500)
                                
                            else:
                                filedata.tiebreaker_question["attempted_answer_by_id"].append(int(s_answer[2]))
                                
                                if filedata.update(filename):
                                    return render_template("game_pages/tiebreaker.html", filedata=filedata, filename=filename, show_wrong_answer=True, actual_answ=int(s_answer[1]), buzzed=False, buzzed_by=None, tied_player_ids=tied_player_ids)
                                
                                log.warning(f"Attempted to write question wrong answer data but failed. Game name: [{filename}] - Tiebreaker")
                                abort(500)
                                
                        log.debug(f"Attempted to open already answered question. Game name: [{filename}] - Tiebreaker")
                        abort(405)
                        
                    else:
                        abort(404)
                        
        log.debug(f"Attempted to open tiebreaker question but no players are tied. Game name: [{filename}] - Tiebreaker")
        flash("Il n'y a pas de joueurs actuellement à égalité.", "warning")
        abort(404)
    
    log.debug(f"Attempted to open a question from a game that is not open. Game name: [{filename}] - Tiebreaker")
    flash("Le nom du jeu ne correspond pas au jeu actuellement actif.", "warning")
    abort(404)
    
    
@game_pages.route("/closegame/<filename>")
def close_game(filename):
    global current_game_filename
    global tied_player_ids
    
    if filename == current_game_filename:
        current_game_filename = None
        tied_player_ids = None
        gamefile = GameDataFile.read(filename)
        
        if gamefile:
            date_time = datetime.datetime.now()
            gamefile.datetime = date_time.strftime("%d/%m/%Y-%H:%M:%S")
            gamefile.update(filename)
            
            log.debug(f"Game closed successfully. Game name: [{filename}]")
            flash("Le jeu s'est terminé avec succès.", "success")
            return redirect(url_for("index"))
        
    log.debug(f"Failed to close game (Invalid game name). Game name: [{filename}]")
    flash("Impossible de fermer le jeu (nom de jeu invalide).", "danger")
    return redirect(url_for("index"))
    

@game_pages.route("/reset/<next>")
def reset_game(next):
    global current_game_filename
    global tied_player_ids
    
    filename = current_game_filename
    current_game_filename = None
    tied_player_ids = None
    gamefile = GameDataFile.read(filename)
        
    if gamefile:
        date_time = datetime.datetime.now()
        gamefile.datetime = date_time.strftime("%d/%m/%Y-%H:%M:%S")
        gamefile.update(filename)
            
        log.debug(f"Game closed successfully. Game name: [{filename}] - Next redirect [{next}]")
        flash("Le jeu s'est terminé avec succès.", "success")
        return redirect(url_for("game_pages.load_game", filename=next))
        
    log.debug(f"Failed to close game (Invalid game name). Game name: [{filename}]")
    flash("Impossible de fermer le jeu (nom de jeu invalide).", "danger")
    return redirect(url_for("index"))

