import time
from tkinter import messagebox
import atexit
import psutil
from threading import Thread
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node

# Global variables
last_game = None
start_time = None
last_ide = None
start_time_ide = None
icon = None


def on_exit():
    note_node.del_note()


atexit.register(on_exit)

# load game list func
def load_game_list(file_path):
    games = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if " - " in line:  # Good formatting check
                    exe, name = map(str.strip, line.split(" - ", 1))
                    games[exe.lower()] = name
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    return games

def load_ide_list(file_path):
    ides = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if " - " in line:  # Good formatting check
                    exe, name = map(str.strip, line.split(" - ", 1))
                    ides[exe.lower()] = name
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    return ides

# Detech a running game
def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]  # return the game name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def detect_running_ides(ide_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in ide_dict:
                return ide_dict[process_name]  # return the game name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

# Main monitoring func
def game_monitor():
    global last_game, start_time

    while True:
        game_dict = load_game_list('games.txt')

        if game_dict:
            running_game = detect_running_game(game_dict)

            if running_game:
                if last_game != running_game:
                    start_time = time.perf_counter()
                    # print(f"Game changed to {running_game}")
                    note_node.send_note(f"Playing {running_game} since 0 sec", 0)
                    last_game = running_game

                else:
                    end_time = time.perf_counter()
                    run_time = end_time - start_time
                    run_time_min = int(run_time / 60)
                    # print(f"Still playing {running_game}")

                    # Check if time played > 60mn
                    if run_time_min >= 60:
                        run_time_hr = round(run_time_min / 60, 0)
                        note_node.send_note(f"Playing {running_game} since {run_time_hr}h", 0)
                    else:
                        # If not showing in min
                        note_node.send_note(f"Playing {running_game} since {run_time_min} min", 0)

                    last_game = running_game
            else:
                if last_game != "nogame":
                    # Removing note if game's been closed
                    note_node.del_note()
                    last_game = "nogame"
                    # print("Game closed")
                else:
                    print("No game is currently running")

        else:
            # If error
            messagebox.showerror("Error",
                                 f"Game list is empty or failed to load.")
            # print("Game list is empty or failed to load.")
            exit()

        time.sleep(120)

def ide_monitor():
    global last_ide, start_time_ide

    while True:
        game_dict = load_game_list('ides.txt')

        if game_dict:
            running_ide = detect_running_ides(game_dict)

            if running_ide:
                if last_ide != running_ide:
                    start_time_ide = time.perf_counter()
                    # print(f"Game changed to {running_game}")
                    note_node.send_note(f"Coding on {running_ide} since 0 sec", 0)
                    last_ide = running_ide

                else:
                    end_time = time.perf_counter()
                    run_time = end_time - start_time_ide
                    run_time_min = int(run_time / 60)
                    # print(f"Still playing {running_game}")

                    # Check if time played > 60mn
                    if run_time_min >= 60:
                        run_time_hr = round(run_time_min / 60, 0)
                        note_node.send_note(f"Coding on {running_ide} since {run_time_hr}h", 0)
                    else:
                        # If not showing in min
                        note_node.send_note(f"Coding on {running_ide} since {run_time_min} min", 0)

                    last_ide = running_ide
            else:
                if last_ide != "noide":
                    # Removing note if game's been closed
                    note_node.del_note()
                    last_ide = "noide"
                    # print("Game closed")
                else:
                    print("No IDE is currently running")

        else:
            # If error
            messagebox.showerror("Error",
                                 f"IDE list is empty or failed to load.")
            # print("Game list is empty or failed to load.")
            exit()

        time.sleep(120)

# Systray
def create_image():
    return Image.open("icon.ico")

# App exit
def quit_application(icon):
    note_node.del_note()
    icon.stop()
    # print("Application terminated.")

def actual_game():
    return None

# Main func to launch the app
def main():
    global icon

    # Context menu
    menu = Menu(
        MenuItem(f"Jeu actuel : (système d'affichage pas fonctionnel)",actual_game),  # New button
        MenuItem("Quitter l'app", quit_application)
    )

    # Open icon
    icon = Icon("IGNoteIntegration", create_image(), "IGNoteIntegration", menu)

    # Start monitoring games
    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()

    monitor_thread_ide = Thread(target=ide_monitor, daemon=True)
    monitor_thread_ide.start()

    # Start in the systray
    icon.run()

if __name__ == "__main__":
    main()