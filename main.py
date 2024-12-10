import time
import psutil

last_game = None  # On initialise `last_game` à None

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

def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]  # Retourner le nom du jeu correspondant
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

while True:
    game_dict = load_game_list('games.txt')

    if game_dict:
        running_game = detect_running_game(game_dict)

        if running_game:
            if last_game != running_game:
                print(f"Game changed to: {running_game}")
                last_game = running_game 
            else:
                print(f"Still playing: {running_game}")
        else:
            print("No predefined games are currently running.")
    else:
        print("Game list is empty or failed to load.")

    time.sleep(15)
