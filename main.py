import time
import psutil
from threading import Thread
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node

# Variables globales
last_game = None
start_time = None
icon = None

# Fonction pour charger la liste des jeux
def load_game_list(file_path):
    games = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if " - " in line:  # S'assurer que la ligne contient le bon format
                    exe, name = map(str.strip, line.split(" - ", 1))
                    games[exe.lower()] = name
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    return games

# Fonction pour détecter un jeu en cours d'exécution
def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]  # Retourner le nom du jeu correspondant
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

# Fonction principale de surveillance
def game_monitor():
    global last_game, start_time

    while True:

        game_dict = load_game_list('games.txt')

        if game_dict:
            running_game = detect_running_game(game_dict)

            if running_game:
                if last_game != running_game:
                    start_time = time.perf_counter()
                    print(f"Game changed to {running_game}")
                    note_node.send_note(f"Playing {running_game} since 0 sec", 0)
                    last_game = running_game

                else:
                    end_time = time.perf_counter()
                    run_time = end_time - start_time
                    run_time_min = int(run_time / 60)
                    print(f"Still playing {running_game}")

                    if run_time_min >= 60:
                        run_time_hr = round(run_time_min / 60, 0)
                        note_node.send_note(f"Playing {running_game} since {run_time_hr}h", 0)
                    else:
                        note_node.send_note(f"Playing {running_game} since {run_time_min} min", 0)

                    last_game = running_game
            else:
                if last_game != "nogame":
                    note_node.del_note()
                    last_game = "nogame"
                    print("Game closed")
                else:
                    print("No game is currently running")

        else:
            print("Game list is empty or failed to load.")

        time.sleep(120)

# Fonction pour créer une icône pour la barre système
def create_image():
    # Charger une icône depuis un fichier ico
    return Image.open("icon.ico")

# Fonction pour quitter l'application
def quit_application(icon, item):
    icon.stop()
    print("Application terminated.")

# Fonction principale pour lancer l'application
def main():
    global icon

    # Créer un menu contextuel
    menu = Menu(MenuItem("Quitter l'app", quit_application))

    # Créer une icône
    icon = Icon("IGNoteIntegration", create_image(), "IGNoteIntegration", menu)

    # Lancer la surveillance des jeux dans un thread séparé
    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()

    # Démarrer l'icône de la barre système
    icon.run()

if __name__ == "__main__":
    main()