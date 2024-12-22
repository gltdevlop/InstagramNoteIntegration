import mysql.connector

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="xxx",  # Remplacez par l'hôte de votre base de données
            user="root",  # Remplacez par votre nom d'utilisateur MySQL
            password="xxx",  # Remplacez par votre mot de passe MySQL
            database="game_list"  # Remplacez par le nom de votre base de données
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def load_game_data():
    games = {}
    dev_apps = {}

    connection = connect_to_database()
    if connection is None:
        return games, dev_apps

    try:
        cursor = connection.cursor(dictionary=True)

        # Charger la liste des jeux
        cursor.execute("SELECT executable, game_name FROM game_list")
        for row in cursor.fetchall():
            exe = row['executable'].strip().lower()  # Supprime les espaces/sauts de ligne et met en minuscule
            name = row['game_name'].strip()  # Supprime les espaces/sauts de ligne
            games[exe] = name

        # Charger la liste des IDEs
        cursor.execute("SELECT executable, ide_name FROM ide_list")
        for row in cursor.fetchall():
            exe = row['executable'].strip().lower()
            name = row['ide_name'].strip()
            dev_apps[exe] = name

    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
    finally:
        cursor.close()
        connection.close()


    return games, dev_apps
