from tkinter import messagebox, Tk, Toplevel, Label
import requests
import zipfile
import os
import shutil
import subprocess
import time
import threading

GITHUB_API_URL = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
CURRENT_VERSION_FILE = "_internal/infos.txt"
EXE_NAME = "IGNoteIntegration.exe"


def get_current_version():
    try:
        if not os.path.exists(CURRENT_VERSION_FILE):
            raise FileNotFoundError(f"Le fichier {CURRENT_VERSION_FILE} est introuvable.")

        with open(CURRENT_VERSION_FILE, "r") as f:
            for line in f:
                if line.strip().startswith("version:"):
                    return line.split(":")[1].strip()
    except Exception as e:
        print(f"Erreur lors de la lecture de la version actuelle : {e}")
    return None


def get_latest_release():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        data = response.json()
        tag_name = data["tag_name"]
        download_url = data["assets"][0]["browser_download_url"]
        return tag_name, download_url
    else:
        raise Exception(f"Cant get releases (HTTP Request error): {response.status_code}")


def download_and_extract_zip(url, target_folder):
    zip_path = "latest_release.zip"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_folder)
    os.remove(zip_path)


def create_update_script():
    script_name = "update.bat"
    with open(script_name, "w") as f:
        f.write(f"@echo off\n")
        f.write(f"echo Mise à jour en cours...\n")
        f.write(f"timeout /t 2 > nul\n")
        f.write(f"del {EXE_NAME}\n")
        f.write(f"move update_temp\\{EXE_NAME} .\\{EXE_NAME}\n")
        f.write(f"rmdir /s /q _internal\n")
        f.write(f"rename internal _internal\n")
        f.write(f"copy _internal\\config.json config.json\n")
        f.write(f"del _internal\\config.json\n")
        f.write(f"copy config.json _internal\\config.json\n")
        f.write(f"del config.json\n")
        f.write(f"rmdir /s /q update_temp\n")
        f.write(f"start {EXE_NAME}\n")
        f.write(f"del %~f0\n")
    return script_name


def get_latest_release_notes():
    url = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("body", "No available release notes.")


def show_wait_window():
    wait_window = Toplevel()
    wait_window.title("Veuillez patienter")
    Label(wait_window, text="Chargement...").pack(pady=20, padx=20)
    wait_window.geometry("200x100")
    return wait_window


def threaded_askyesno(title, message, callback):
    def task():
        response = messagebox.askyesno(title, message)
        callback(response)

    thread = threading.Thread(target=task)
    thread.start()
    return thread


def handle_update_response(response, latest_version, download_url, up_notes):
    if response:
        download_and_extract_zip(download_url, "update_temp")
        shutil.copytree("update_temp/_internal", "internal")
        script_name = create_update_script()
        subprocess.Popen([script_name])
        time.sleep(1)
        os.system("taskkill /f /im IGNoteIntegration.exe")
    else:
        messagebox.showinfo("Declined", "You declined the update. It'll re-ask you at next app-startup.")


def update_application():
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()
    notes = get_latest_release_notes()
    up_notes = notes.replace("#", "").replace("*", "")

    if current_version != latest_version:
        root = Tk()
        root.withdraw()  # Hide the main root window

        wait_window = show_wait_window()

        def on_response(response):
            wait_window.destroy()
            handle_update_response(response, latest_version, download_url, up_notes)

        threaded_askyesno(
            "Update - IGNoteIntegration",
            f"Version {latest_version} available (actual: {current_version}). Changes : {up_notes} Update ?",
            on_response,
        )
        root.mainloop()

def update_application_wanted():
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()
    notes = get_latest_release_notes()
    up_notes = notes.replace("#", "").replace("*", "")

    if current_version != latest_version:
        root = Tk()
        root.withdraw()  # Hide the main root window

        wait_window = show_wait_window()

        def on_response(response):
            wait_window.destroy()
            handle_update_response(response, latest_version, download_url, up_notes)

        threaded_askyesno(
            "Update - IGNoteIntegration",
            f"Version {latest_version} available (actual: {current_version}). Changes : {up_notes} Update ?",
            on_response,
        )
        root.mainloop()
    else:
        messagebox.showinfo("No update", "No update is currently available.")