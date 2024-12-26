import os
import creds_create
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client
import gh_update

gh_update.update_application()

if not os.path.exists("creds.txt"):
    creds_create.window()

with open("creds.txt", "r", encoding="utf-8") as f:
    creds = f.readlines()
    username = creds[0].strip()
    password = creds[1].strip()

cl = Client(request_timeout=2)
session_file = "_internal/session.json"

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

original_input = cl.challenge_code_handler

def custom_challenge_handler(username, choice=None):
    print("OTP requested for authentication.")
    code = otp_prompt()
    if not code:
        raise Exception("OTP code was not provided.")
    return code

cl.challenge_code_handler = custom_challenge_handler

# Gestion de la session
def load_or_create_session():
    """Charge ou crée une session Instagram."""
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            if not cl.login(username, password):
                raise Exception("Session invalide.")
            print("Session chargée avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement de la session : {e}. Nouvelle connexion nécessaire.")
            try:
                cl.login(username, password)
                cl.dump_settings(session_file)
            except Exception:
                messagebox.showerror("Password Changed", f"Your password had been changed, you have to re enter it.")
                creds_create.window()
    else:
        print("Aucune session trouvée. Connexion initiale en cours.")


# Charger ou créer la session
try:
    load_or_create_session()
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
