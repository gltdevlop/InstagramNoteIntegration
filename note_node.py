import os
from tkinter import messagebox

from instagrapi import Client

if not os.path.exists("creds.txt"):
    messagebox.showerror("Error", f"The credits file was not found. Please create a creds.txt file in the same folder with your instagram credits.")
    exit()

with open("creds.txt", "r", encoding="utf-8") as f:
    creds = f.readlines()
    username = creds[0].strip()
    password = creds[1].strip()

cl = Client()
cl.login(username, password)

user_id = cl.user_id_from_username(username)
medias = cl.user_medias(user_id, 20)

def send_note(note, audience):
    cl.create_note(note, audience)

def del_note():
    note = cl.create_note("note", 1)
    cl.delete_note(int(note.id))


