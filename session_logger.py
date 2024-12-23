import datetime
import mysql.connector

# Configuration MySQL
DB_CONFIG = {
    'host': 'xxx',  # Remplacez par l'adresse de votre serveur
    'user': 'root',       # Votre utilisateur MySQL
    'password': 'xxx',       # Mot de passe MySQL
    'database': 'game_sessions_db'
}

def should_log_data():
    """Check if data logging is enabled based on the config file."""
    config_path = '_internal/config.txt'
    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('share_data:'):
                return line.strip().endswith('True')
    return False

def log_game_session(game_name, user_name, start_time, end_time):
    """Log a game session to the MySQL database."""

    if not should_log_data():
        print("Data logging is disabled.")
        return

    print(f"Logging session for game: {game_name}, user: {user_name}, start: {start_time}, end: {end_time}")
    duration = end_time - start_time
    duration_minutes = int(duration / 60)
    print(f"Session duration: {duration_minutes} minutes")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            INSERT INTO game_sessions (game_name, user_name, start_time, end_time, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (game_name, user_name, datetime.datetime.fromtimestamp(start_time),
                               datetime.datetime.fromtimestamp(end_time), duration_minutes))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Logged session: {game_name} ({duration_minutes} minutes)")
    except mysql.connector.Error as e:
        print(f"Error logging session to database: {e}")

def calculate_total_playtime():
    """Calculate total playtime from the MySQL database."""
    total_time = 0
    game_times = {}

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            SELECT game_name, SUM(duration_minutes)
            FROM game_sessions
            GROUP BY game_name
        """
        cursor.execute(query)
        for game_name, total_minutes in cursor.fetchall():
            game_times[game_name] = total_minutes
            total_time += total_minutes

        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error reading from database: {e}")

    return total_time, game_times
