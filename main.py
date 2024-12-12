import time
import psutil
import note_node

last_game = None  # On initialise `last_game` à None
start_time = None
end_time = None

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
                start_time = time.perf_counter()
                print(f"Game changed to: {running_game}")
                note_node.send_note(f"Joue à {running_game} depuis 0 sec", 0)
                last_game = running_game

            else:
                end_time = time.perf_counter()
                run_time = end_time - start_time
                run_time_min = int(run_time / 60)
                print(f"Still playing: {running_game}")

                if run_time_min >= 60:
                    run_time_hr = round(run_time_min /60,0)
                    note_node.send_note(f"Joue à {running_game} depuis {run_time_hr}h", 0)
                else:
                    note_node.send_note(f"Joue à {running_game} depuis {run_time_min} min", 0)

                last_game = running_game
        else:
            print("No game is currently running")
    else:
        print("Game list is empty or failed to load.")

    time.sleep(60)
