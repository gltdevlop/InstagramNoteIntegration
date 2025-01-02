import time
import psutil

from managers.list_manager import load_game_data
from nodes.logger_node import log_game_session

running_games = {}  # Dictionnaire pour suivre les minuteries des jeux {jeu: start_time}

def detect_running_games(game_dict):
    """Détecte toutes les applications en cours d'exécution correspondant à game_dict."""
    detected_games = []
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                detected_games.append(game_dict[process_name])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return detected_games


def game_monitor(username):
    global running_games

    while True:
        try:
            game_dict, dev_apps = load_game_data()
            if game_dict or dev_apps:
                combined_game_dict = {**game_dict, **dev_apps}
                detected_games = detect_running_games(combined_game_dict)

                for game in detected_games:
                    if game not in running_games:
                        running_games[game] = time.perf_counter()
                        print(f"New game started: {game}")

                for game in list(running_games.keys()):
                    if game not in detected_games:
                        end_time = time.perf_counter()
                        start_time = running_games.pop(game, None)
                        if start_time:
                            try:
                                log_game_session(game, username, start_time, end_time)
                                print(f"Game session logged: {game}")
                            except Exception as e:
                                print(f"Error logging game session: {e}")

            else:
                print("Game list is empty or failed to load.")

        except Exception as e:
            print(f"Error in game monitor: {e}")

        time.sleep(1)

