from tkinter import messagebox

import psutil
import requests
import zipfile
import os
import shutil
import subprocess
import time
import variables_node as vn

GITHUB_API_URL = vn.github_api_url
CURRENT_VERSION_FILE = vn.infos_file
EXE_NAME = vn.exe

def get_current_version():
    try:
        if not os.path.exists(CURRENT_VERSION_FILE):
            messagebox.showerror("Error", f"Couldn't file the {CURRENT_VERSION_FILE} file.")

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
        messagebox.showerror("Error", f"Couldn't get releases : {response.status_code}")


def download_and_extract_zip(url, target_folder):
    latest_rl_zip_path = vn.latest_rl_zip_path
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(latest_rl_zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    try:
        with zipfile.ZipFile(latest_rl_zip_path, "r") as zip_ref:
            zip_ref.extractall(target_folder)
    except zipfile.BadZipFile as e:
        messagebox.showerror("Error", f"Failed to extract zip: {e}")

    os.remove(latest_rl_zip_path)


def create_update_script():
    update_script_name = vn.update_script_name
    with open(update_script_name, "w") as f:
        f.write(f"@echo off\n")
        f.write(f"echo Updating application...\n")
        f.write(f"timeout /t 2 > nul\n")
        f.write(f"taskkill /f /im {EXE_NAME} > nul 2>&1\n")  # Ensure the process is terminated
        f.write(f"if exist {EXE_NAME} del {EXE_NAME}\n")     # Delete old executable
        f.write(f"move update_temp\\{EXE_NAME} .\\{EXE_NAME}\n")
        f.write(f"rmdir /s /q _internal\n")
        f.write(f"rename internal _internal\n")
        f.write(f"copy _internal\\config.json config.json\n")
        f.write(f"del _internal\\config.json\n")
        f.write(f"copy config.json _internal\\config.json\n")
        f.write(f"del config.json\n")
        f.write(f"if exist update_temp rmdir /s /q update_temp\n")  # Cleanup
        f.write(f"start {EXE_NAME}\n")
        f.write(f"del %~f0\n")
    return update_script_name

def get_latest_release_notes():
    rl_url = vn.rl_url
    response = requests.get(rl_url)
    response.raise_for_status()
    return response.json().get("body", "No available release notes.")

def terminate_process_by_name(name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == name:
            process.terminate()
            process.wait()


def update_application():
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()

    if current_version != latest_version:
        try:
            print("Downloading update...")
            download_and_extract_zip(download_url, "update_temp")
            print("Extracting update...")
            shutil.copytree("update_temp/_internal", "internal", dirs_exist_ok=True)
            print("Creating update script...")
            script_name = create_update_script()
            print(f"Running update script: {script_name}")
            subprocess.Popen([script_name], creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
            time.sleep(1)
            terminate_process_by_name(EXE_NAME)
        except Exception as e:
            messagebox.showerror("Error", f"Error during update: {e}")
    else:
        print("Application is up to date.")

def update_application_wanted():
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()
    notes = get_latest_release_notes()
    up_notes = notes.replace("#", "").replace("*", "")

    if current_version != latest_version:
        update = messagebox.askyesno("Update - IGNoteIntegration", f"Version {latest_version} available (actual: {current_version}). Changes : {up_notes} Update ?")
        if update:
            try:
                print("Downloading update...")
                download_and_extract_zip(download_url, "update_temp")
                print("Extracting update...")
                shutil.copytree("update_temp/_internal", "internal", dirs_exist_ok=True)
                print("Creating update script...")
                script_name = create_update_script()
                print(f"Running update script: {script_name}")
                subprocess.Popen([script_name], creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
                time.sleep(1)
                terminate_process_by_name(EXE_NAME)
            except Exception as e:
                messagebox.showerror("Error", f"Error during update: {e}")
        else:
            messagebox.showinfo("Declined", "You declined the update. It'll re-ask you at next app-startup.")
    else:
        messagebox.showinfo("No update", "No update is currently available.")