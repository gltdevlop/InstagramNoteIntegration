from tkinter import messagebox
from instagrapi import Client
from add_startup import add_startup

import subprocess
import tkinter as tk
import note_node

client = Client()

def validate_credentials(username, password):
    client.challenge_code_handler = note_node.custom_challenge_handler  # Attach custom handler
    try:
        client.login(username, password)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Login failed: {e}")
        return False

def window():
    def save_credentials():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill all the forms.")
            return

        if not validate_credentials(username, password):
            root.deiconify()
            return

        try:
            # Save credentials locally
            with open("creds.txt", "w") as f:
                f.write(f"{username}\n")
                f.write(f"{password}\n")
                f.flush()

            # Create a batch script for restart
            with open("save_reboot.bat", "w") as f:
                f.write(f"@echo off\n")
                f.write(f"taskkill /f /im IGNoteIntegration.exe\n")
                f.write(f"start IGNoteIntegration.exe\n")
                f.write(f"del %~f0\n")

            add_startup()
            subprocess.Popen("save_reboot.bat", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

        except Exception as e:
            messagebox.showerror("Error", f"An error has occurred while updating: {e}")

    root = tk.Tk()
    root.title("Configuration")
    root.geometry("300x260")
    root.resizable(False, False)

    username_label = tk.Label(root, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    reboot_label = tk.Label(root,
                            text="The app will start after you'll click 'Go!'.\nYou'll find it in the system tray"
                                 " after it connects \nto your Instagram account.")
    reboot_label.pack(pady=22)

    save_button = tk.Button(root, text="Go!", command=lambda: [root.withdraw(), save_credentials()])
    save_button.pack(pady=3)

    root.mainloop()
