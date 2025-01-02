import nodes.variables_node as vn

host = vn.db_host
passwd = vn.db_pwd

DB_CONFIG = {
    'host': host,  # Remplacez par l'adresse de votre serveur
    'user': 'root',  # Votre utilisateur MySQL
    'password': passwd,  # Mot de passe MySQL
    'database': 'game_sessions_db'
}

GAME_LIST_DB_CONFIG = {
    'host': host,  # Meme serveur
    'user': 'root',  # Meme utilisateur
    'password': passwd,  # Meme mot de passe
    'database': 'game_list'  # Base de données différente
}

TRANSLATION_DB = {
    'host': host,  # Meme serveur
    'user': 'root',  # Meme utilisateur
    'password': passwd,  # Meme mot de passe
    'database': 'translations_db'  # Base de données différente
}
