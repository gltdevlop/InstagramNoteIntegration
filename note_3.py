from instagrapi import Client

ACCOUNT_USERNAME = "gbrt.ee"
ACCOUNT_PASSWORD = "xxx"

cl = Client()
cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)

user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
medias = cl.user_medias(user_id, 20)

def send_note(note, audience):
   cr_note = cl.create_note(note, audience)

def del_note():
    note = cl.create_note("note", 1)
    cl.delete_note(int(note.id))


