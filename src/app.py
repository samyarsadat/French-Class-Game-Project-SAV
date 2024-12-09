#  French Class Project Game Website main application file.
#  Copyright 2022 Samyar Projects
#  Written by Samyar Sadat Akhavi, 2023.


# ------- Libraries, utils, and modules -------
from init import log
import pymsgbox._native_win as pymsgbox


def main():
    # ------- Libraries, utils, and modules -------
    from config import AppConfig
    import jinja2
    import werkzeug
    import datetime
    from flask import redirect, render_template, request
    from init import app
    from utils.models import GameDataQuestion, GameQuestion, GamePlayer
    from modules.game import game_pages
    from modules.data import data, list_saved_games, GameDataFile, GameQuestions
    from random import randint
    from flask import abort, flash, url_for
    from flaskwebgui import FlaskUI


    # ------- Jinja env global objects -------
    app.jinja_env.globals["GAME_MAX_PLAYERS"] = AppConfig.GAME_MAX_PLAYERS
    app.jinja_env.globals["abort"] = abort
    app.jinja_env.globals["QUESTION_MAX_TIME"] = AppConfig.GAME_QUESTION_TIME
    app.jinja_env.globals["QUESTION_MAX_ANSWER_TIME"] = AppConfig.GAME_ANSWER_TIME


    # ------- Blueprint registry -------
    app.register_blueprint(game_pages, url_prefix="/game")
    app.register_blueprint(data)


    # ------- Error handlers -------
    @app.errorhandler(werkzeug.exceptions.NotFound)
    def error404(error):
        log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [404 Error]")
        return render_template("errors/error_404.html"), 404


    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def error500(error):
        log.error(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [500 Error]")
        return render_template("errors/error_500.html"), 500


    @app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
    def error405(error):
        log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [405 Error]")
        return render_template("errors/error_405.html"), 405


    @app.errorhandler(jinja2.exceptions.TemplateNotFound)
    def template_error(error):
        log.critical(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [500 Template Error]")
        return render_template("errors/error_500.html"), 500
    
    
    # ------- Before and after request -------
    @app.before_request
    def remove_www():
        if "://www." in request.url.lower():
            log.info(f"[{request.remote_addr}] Sent a request with [www.]")

            request_url = request.url.lower()
            return redirect(request_url.replace("www.", ""))


    @app.before_request
    def log_request():
        log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}]")
        
        
    @app.after_request
    def add_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Cache-Control"] = "public, max-age=0"
        return response
        

    # ------- Page routes -------
    @app.route("/")
    def index():
        return render_template("index.html")


    @app.route("/load-game-from-file")
    def load_game():
        return render_template("load_game.html", files=list_saved_games(False))


    @app.route("/start-new-game", methods=["POST", "GET"])
    def start_new_game():
        if request.method == "POST":
            set_game_name = request.form.get("game_name")
            log.debug(f"Creating new game with name: {set_game_name}")
            
            if set_game_name in list_saved_games(False):
                log.debug("New game creation failed because a gamedata file with the same name exists!")
                flash("Un jeu portant ce nom existe déjà!", "danger")
                return redirect(url_for("start_new_game"))
            
            else:
                log.debug("New game creation primary checks passed.")
                date_time = datetime.datetime.now()
                questions = GameQuestions.read(f"{AppConfig.QUESTION_PACK}/{AppConfig.QUESTION_PACK}")
                selected_questions = []
                multi_sel_l1 = randint(0, len(questions.categories))
                multi_sel_l2 = randint(0, AppConfig.MAX_QUESTIONS_PER_CAT)
                
                if len(questions.categories) >= AppConfig.GAME_MIN_CATEGORIES:
                    for cat_id in range(len(questions.categories)):
                        for q_id in range(AppConfig.MAX_QUESTIONS_PER_CAT):
                            rand_id = randint(0, len(questions.questions) - 1) 
                            question = GameQuestion.from_json(questions.questions[rand_id])
                            loop_counter = 0
                            
                            while question.category_id != cat_id or question.points != ((q_id + 1) * questions.points_increment) or question.question_html in (GameDataQuestion.from_json(selected_questions[i]).question_html for i in range(0, len(selected_questions))):
                                rand_id = randint(0, len(questions.questions) - 1)
                                question = GameQuestion.from_json(questions.questions[rand_id])
                                loop_counter += 1
                                
                                if loop_counter >= AppConfig.FIND_QUESTION_RETRY_COUNT:
                                    log.error("New game creation failed because FIND_QUESTION_RETRY_COUNT was exceeded!")
                                    flash("Erreur du pack de questions!", "danger")
                                    abort(500)
                            
                            selected_questions.append(GameDataQuestion(question.question_html, question.correct_answer_id, question.answer_opts_html, question.category_id, question.points, (multi_sel_l1 == cat_id and multi_sel_l2 == q_id), None, True, None, False, [], [], None).as_json())
                        
                    rand_id = randint(0, len(questions.tiebreaker_questions) - 1) 
                    question = GameQuestion.from_json(questions.tiebreaker_questions[rand_id])
                    tiebreaker = GameDataQuestion(question.question_html, question.correct_answer_id, question.answer_opts_html, question.category_id, question.points, False, None, True, None, False, [], [], None).as_json()
                        
                    if GameDataFile(None, date_time.strftime("%d/%m/%Y-%H:%M:%S"), questions.categories, selected_questions, tiebreaker, None, None, AppConfig.MAX_QUESTIONS_PER_CAT, questions.points_increment).create_new(set_game_name):
                        log.info("Successfully created new gamedata file. Redirecting to player name setter.")
                        return redirect(url_for("set_game_names", filename=set_game_name))
                    
                    else:
                        flash("Une erreur fatale s'est produite lors de la tentative de création d'un nouveau fichier de jeu.", "danger")
                        abort(500)
                        
                else:
                    flash("Erreur du pack de questions!", "danger")
                    abort(500)
        
        else:
            date_time = datetime.datetime.now()
            datetime_fmtd = date_time.strftime(AppConfig.FILE_NAME_DATETIME_AUTO_FORMAT)
            game_name = f"GAME_{datetime_fmtd}"
            
            while game_name in list_saved_games(False):
                game_name = f"GAME_{datetime_fmtd}_{randint(0, 99)}"
            
            return render_template("start_new_game.html", default_gn=game_name)
        
        
    @app.route("/set-game-names/<filename>", methods=["POST", "GET"])
    def set_game_names(filename):
        if request.method == "POST":
            players = []
            filedata = GameDataFile.read(filename)
            
            if filedata and not filedata.players:
                log.debug(f"Setting player names for playerless game [{filename}]")
                    
                for player in range(1, AppConfig.GAME_MAX_PLAYERS + 1):
                    if request.form.get(f"player{player}"):
                        players.append(GamePlayer(request.form.get(f"player{player}"), 0).as_json())
                            
                if len(players) < AppConfig.GAME_MIN_PLAYERS:
                    log.debug("Player name config failed because there were not enough players!")
                    flash("Il doit y avoir au moins deux joueurs!", "warning")
                    return redirect(url_for("set_game_names", filename=filename))
                
                filedata.players = players
                
                if filedata.update(filename):
                    log.debug(f"Successfully set player names for game [{filename}]")
                    return redirect(url_for("game_pages.load_game", filename=filename))
            
            log.debug(f"Failed to set player names for game [{filename}]")
            flash("Impossible de définir les noms des joueurs pour le jeu!", "danger")
            return redirect(url_for("set_game_names", filename=filename))
        
        else:
            return render_template("set_game_names.html", filename=filename)


    # ------- Running the app -------
    if __name__ == "__main__":    
        FlaskUI(app=app, server="flask").run()
        log.info("Program TERMINATED successfully")


try:
    main()
 
except Exception:
    log.critical("An exception was thrown when attepting to start the program", exc_info=1)
    print("DYSFONCTIONNEMENT MORTEL DU SYSTÈME")
    pymsgbox.alert("DYSFONCTIONNEMENT MORTEL DU SYSTÈME!", "Erreur", icon=pymsgbox.MB_ICONERRPR)