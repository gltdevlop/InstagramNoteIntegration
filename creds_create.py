import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from add_startup import add_startup
from instagrapi import Client

def save_credentials_and_login(username, password, root):
    """Sauvegarde les informations d'identification et tente de se connecter."""
    try:
        # Test de connexion avec instagrapi
        cl = Client()
        cl.login(username, password)  # Tente de se connecter avec Instagram

        # Si la connexion réussit, sauvegarde les informations d'identification
        with open("creds.txt", "w") as f:
            f.write(f"{username}\n")
            f.write(f"{password}\n")
            f.flush()
            cl.dump_settings("_internal/session.json")

        # Création d'un script pour redémarrer l'application
        with open("save_reboot.bat", "w") as f:
            f.write(f"@echo off\n")
            f.write(f"taskkill /f /im IGNoteIntegration.exe\n")
            f.write(f"start IGNoteIntegration.exe\n")
            f.write(f"del %~f0\n")

        add_startup()
        root.destroy()
        subprocess.Popen("save_reboot.bat")
    except Exception as e:
        # Afficher une erreur et permettre à l'utilisateur de réessayer
        messagebox.showerror("Login Error", f"Failed to log in: {e}")
        return

def window():
    """Fenêtre principale de configuration."""
    def save_credentials():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill all the forms.")
            return
        # Tenter de sauvegarder et de se connecter
        save_credentials_and_login(username, password, root)

    root = tk.Tk()
    root.title("Configuration")
    root.geometry("300x260")
    root.resizable(False, False)

    username_label = tk.Label(root, text="Username :")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    reboot_label = tk.Label(root,
                            text="The app will start after you'll click 'Go !'.\nYou'll find it in the system tray"
                                 "after it connected \nto your instagram account.")
    reboot_label.pack(pady=22)

    save_button = tk.Button(root, text="Go !", command=save_credentials)
    save_button.pack(pady=3)

    root.mainloop()

# Lancement de la fenêtre si les informations n'existent pas
if not os.path.exists("creds.txt"):
    window()
