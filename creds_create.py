import subprocess
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client  # Make sure you have installed instagrapi
from add_startup import add_startup
import time

client = Client()

def notify_user(message, title="Notification"):
    """Display a Tkinter message box."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo(title, message)
    root.destroy()

def otp_prompt(prompt_text="Enter the 6-digit OTP code:"):
    """Prompt the user for OTP via Tkinter GUI."""
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

def custom_challenge_handler(username, challenge):
    """Handle Instagram login challenges."""
    if challenge.get("step_name") == "submit_phone":
        notify_user("Phone verification required. Please update your phone number in the Instagram app.")
        raise Exception("Phone verification required.")
    elif challenge.get("step_name") == "select_verify_method":
        notify_user("Please check your Instagram app and approve the login attempt.")
        return False  # Let the library handle retry logic
    elif challenge.get("step_name") == "verify_code":
        otp_code = otp_prompt("Enter the 6-digit code sent by Instagram:")
        if otp_code:
            return client.challenge_resolve(challenge, code=otp_code)
    elif challenge.get("step_name") == "checkpoint":
        notify_user("Please open your Instagram app and accept the login request.")
        while True:
            try:
                status = client.challenge_resolve(challenge)
                if status:
                    notify_user("Login challenge successfully resolved!")
                    break
            except Exception as e:
                notify_user("Waiting for confirmation in the Instagram app. Please try again.")
            time.sleep(5)  # Retry every 5 seconds
    else:
        notify_user("Unknown challenge type encountered.", title="Error")
        raise Exception("Unknown challenge type encountered.")

def validate_credentials(username, password):
    client.challenge_code_handler = custom_challenge_handler  # Attach custom handler

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
