import os
import creds_create
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client

# Si les informations d'identification n'existent pas, les créer
if not os.path.exists("creds.txt"):
    creds_create.window()

with open("creds.txt", "r", encoding="utf-8") as f:
    creds = f.readlines()
    username = creds[0].strip()
    password = creds[1].strip()

cl = Client(request_timeout=2)

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
        note = cl.create_note("Is not currently playing", 1)
        cl.delete_note(int(note.id))
    except Exception as e:
        print(f"Error deleting note: {e}")
