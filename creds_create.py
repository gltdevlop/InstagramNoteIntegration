import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def window():
    if not os.path.exists("_internal/creds.txt"):
        def save_credentials():
            username = username_entry.get()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Please fill all the forms.")
                return

            try:
                with open("creds.txt", "w") as f:
                    f.write(f"{username}\n")
                    f.write(f"{password}\n")
                    f.flush()

                    with open("save_reboot.bat", "w") as f:
                        f.write(f"@echo off\n")
                        f.write(f"taskkill /f /im IGNoteIntegration.exe\n")
                        f.write(f"start IGNoteIntegration.exe\n")
                        f.write(f"del %~f0\n")

                subprocess.Popen("save_reboot.bat")

            except Exception as e:
                messagebox.showerror("Error", f"An error has occured : {e}")

        root = tk.Tk()
        root.title("Configuration")
        root.geometry("300x260")
        root.resizable(False, False)

        username_label = tk.Label(root, text="Username :")
        username_label.pack(pady=5)
        username_entry = tk.Entry(root)
        username_entry.pack(pady=5)

        # Champ pour le mot de passe
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


