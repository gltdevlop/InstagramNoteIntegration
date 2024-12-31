import datetime
import os
import sys
import time
import mysql.connector
import creds_create
import tkinter as tk

from tkinter import messagebox
from instagrapi import Client
from db_credentials import DB_CONFIG

SESSION_FILE = "instagram_session.json"

def save_session(client):
    client.dump_settings(SESSION_FILE)

def load_session(client):
    if os.path.exists(SESSION_FILE):
        client.load_settings(SESSION_FILE)

def notify_user(message, title="Notification"):
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    messagebox.showinfo(title, message)
    root.destroy()

def otp_prompt(prompt_text="Enter the 6-digit OTP code:"):
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
    if challenge.get("step_name") == "submit_phone":
        notify_user("Phone verification requested. Provide your phone number in the Instagram app.")
        raise Exception("Phone verification required.")
    elif challenge.get("step_name") == "select_verify_method":
        notify_user("Please check your Instagram app and approve the login attempt.")
        return False
    elif challenge.get("step_name") == "verify_code":
        otp_code = otp_prompt("Enter the 6-digit code sent by Instagram:")
        if otp_code:
            return cl.challenge_resolve(challenge, code=otp_code)
    elif challenge.get("step_name") == "checkpoint":
        notify_user("Please open your Instagram app and accept the login request.")
        while True:
            try:
                status = cl.challenge_resolve(challenge)
                if status:
                    notify_user("Login challenge successfully resolved!")
                    break
            except Exception as e:
                notify_user("Waiting for confirmation in the Instagram app. Please try again.")
            time.sleep(5)
    else:
        notify_user("Unknown challenge type encountered.", title="Error")
        raise Exception("Unknown challenge type encountered.")

cl = Client()
cl.challenge_code_handler = custom_challenge_handler

def main():
    if not os.path.exists("creds.txt"):
        creds_create.window()

    with open("creds.txt", "r", encoding="utf-8") as f:
        creds = f.readlines()
        username = creds[0].strip()
        password = creds[1].strip()

    try:
        load_session(cl)
        if not cl.get_settings().get("authorization"):
            cl.login(username, password)
            save_session(cl)
    except Exception as e:
        try:
            cl.login(username, password)
            save_session(cl)
        except Exception as e:
            notify_user(f"Login failed: {e}", title="Login Error")
            sys.exit(1)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror("Connexion Error", f"Unable to connect to database. Error: {e}")
        sys.exit(1)

    try:
        cursor = conn.cursor()

        check_query = "SELECT id FROM unique_game_users WHERE user_name = %s"
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()

        if not result:
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

        conn.commit()

    except mysql.connector.Error as e:
        notify_user(f"Error logging session to database: {e}", title="Database Error")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

    try:
        user_id = cl.user_id_from_username(username)
        medias = cl.user_medias(user_id, 20)
    except Exception as e:
        print(e)

def send_note(note, audience):
    try:
        cl.create_note(note, audience)
    except Exception as e:
        print(e)

def del_note():

    if os.path.exists("creds.txt"):
        with open("creds.txt", "r", encoding="utf-8") as f:
            creds = f.readlines()
            uname = creds[0].strip()
    else:
        creds_create.window()

    try:
        note = cl.create_note(f"{uname} is not currently playing", 1)
        # cl.delete_note(int(note.id))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
