import datetime
import os
import mysql.connector
import creds_create
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client
import gh_update
from db_credentials import DB_CONFIG

gh_update.update_application()

if not os.path.exists("creds.txt"):
    creds_create.window()

with open("creds.txt", "r", encoding="utf-8") as f:
    creds = f.readlines()
    username = creds[0].strip()
    password = creds[1].strip()

cl = Client()

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
        print(f"New user added: {username} with ID {next_id}")
        conn.commit()

    # Commit les changements
    conn.commit()

except mysql.connector.Error as e:
    print(f"Error logging session to database: {e}")
finally:
    cursor.close()
    conn.close()

def otp_prompt():
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

    label = tk.Label(root, text="Enter the 6-digit OTP code:")
    label.pack(pady=10)

    code_entry = tk.Entry(root)
    code_entry.pack(pady=5)

    send_button = tk.Button(root, text="Send", command=send_code)
    send_button.pack(pady=10)

    root.mainloop()
    return code

# Surcharge de la méthode d'entrée pour gérer les demandes OTP
original_input = cl.challenge_code_handler

def custom_challenge_handler(username, choice=None):
    print("OTP requested for authentication.")
    code = otp_prompt()
    if not code:
        raise Exception("OTP code was not provided.")
    return code

cl.challenge_code_handler = custom_challenge_handler

# Connexion avec gestion du challenge
try:
    cl.login(username, password)
except Exception as e:
    messagebox.showerror("Login Error", f"Failed to log in: {e}")
    exit(1)

user_id = cl.user_id_from_username(username)
medias = cl.user_medias(user_id, 20)

def send_note(note, audience):
    try:
        cl.create_note(note, audience)
    except Exception as e:
        print(f"Error sending note: {e}")

def del_note():
    try:

        note = cl.create_note(f"{username} is not currently playing", 1)
        # cl.delete_note(int(note.id))
    except Exception as e:
        print(f"Error deleting note: {e}")

