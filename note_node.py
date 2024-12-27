import datetime
import os
import time
import mysql.connector
import creds_create
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client
from db_credentials import DB_CONFIG

# Vérifier si les creds.txt existent
if not os.path.exists("creds.txt"):
    creds_create.window()

with open("creds.txt", "r", encoding="utf-8") as f:
    creds = f.readlines()
    username = creds[0].strip()
    password = creds[1].strip()

cl = Client()

# Fonction pour afficher une fenêtre de notification
def notify_user(message, title="Notification"):
    """Affiche une boîte de dialogue Tkinter avec le message."""
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    messagebox.showinfo(title, message)
    root.destroy()

# Fonction pour afficher une fenêtre de saisie OTP
def otp_prompt(prompt_text="Enter the 6-digit OTP code:"):
    """Crée une fenêtre Tkinter pour entrer le code OTP."""
    code = None

    def send_code():
        nonlocal code
        code = code_entry.get()
        if code:
            root.destroy()

    root = tk.Tk()
    root.title("OTP Required")
    root.geometry("300x150")

    label = tk.Label(root, text=prompt_text)
    label.pack(pady=10)

    code_entry = tk.Entry(root)
    code_entry.pack(pady=5)

    send_button = tk.Button(root, text="Send", command=send_code)
    send_button.pack(pady=10)

    root.mainloop()
    return code

# Gestionnaire de défis personnalisé
def custom_challenge_handler(username, challenge):
    """Gestion des challenges Instagram."""
    if challenge.get("step_name") == "submit_phone":
        notify_user("Phone verification requested. Provide your phone number in the Instagram app.")
        raise Exception("Phone verification required.")
    elif challenge.get("step_name") == "select_verify_method":
        # Méthodes de vérification disponibles
        notify_user("Please check your Instagram app and approve the login attempt.")
        return False  # Laisser la bibliothèque gérer la logique de retry par défaut
    elif challenge.get("step_name") == "verify_code":
        # Demander le code OTP
        otp_code = otp_prompt("Enter the 6-digit code sent by Instagram:")
        if otp_code:
            return cl.challenge_resolve(challenge, code=otp_code)
    elif challenge.get("step_name") == "checkpoint":
        # Notify user to open the app and approve
        notify_user("Please open your Instagram app and accept the login request.")
        # Attendre que l'utilisateur confirme dans l'application
        while True:
            try:
                status = cl.challenge_resolve(challenge)
                if status:
                    notify_user("Login challenge successfully resolved!")
                    break
            except Exception as e:
                # Informer l'utilisateur de vérifier à nouveau
                notify_user("Waiting for confirmation in the Instagram app. Please try again.")
            time.sleep(5)  # Réessayer toutes les 5 secondes
    else:
        notify_user("Unknown challenge type encountered.", title="Error")
        raise Exception("Unknown challenge type encountered.")

# Assigner le gestionnaire personnalisé
cl.challenge_code_handler = custom_challenge_handler

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Vérifier si le user_name existe déjà dans unique_game_users
    check_query = "SELECT id FROM unique_game_users WHERE user_name = %s"
    cursor.execute(check_query, (username,))
    result = cursor.fetchone()

    if not result:
        # user_name n'existe pas, ajoutons-le
        next_id_query = "SELECT IFNULL(MAX(id), 0) + 1 FROM unique_game_users"
        cursor.execute(next_id_query)
        next_id = cursor.fetchone()[0]

        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_user_query = """
                INSERT INTO unique_game_users (id, user_name, created_at)
                VALUES (%s, %s, %s)
            """
        cursor.execute(insert_user_query, (next_id, username, created_at))
        conn.commit()

    # Commit les changements
    conn.commit()

except mysql.connector.Error as e:
    notify_user(f"Error logging session to database: {e}", title="Database Error")
finally:
    # Check if cursor and conn are initialized before using them
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()

# Connexion avec gestion du challenge
try:
    cl.login(username, password)
except Exception as e:
    notify_user(f"Login failed: {e}", title="Login Error")
    exit(1)

# Récupération des médias d'un utilisateur
try:
    user_id = cl.user_id_from_username(username)
    medias = cl.user_medias(user_id, 20)
except Exception as e:
    print(e)

# Fonctions pour gérer les notes
def send_note(note, audience):
    try:
        cl.create_note(note, audience)
    except Exception as e:
        print(e)

def del_note():
    try:
        note = cl.create_note(f"{username} is not currently playing", 1)
        # cl.delete_note(int(note.id))
    except Exception as e:
        print(e)