import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client  # Make sure you have installed instagrapi
from add_startup import add_startup


def validate_credentials(username, password):

    client = Client()
    try:
        client.login(username, password)  # Attempt to log in
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
            root.deiconify()  # Re-show the window if validation fails
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
            messagebox.showerror("Error", f"An error has occurred: {e}")

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

