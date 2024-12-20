from tkinter import messagebox
import requests
import zipfile
import os
import shutil

# URL de l'API GitHub pour récupérer les informations de la dernière release
GITHUB_API_URL = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
CURRENT_VERSION_FILE = "_internal/config.txt"  # Fichier contenant la version actuelle
KEEP_FILES = ["creds.txt"]  # Fichiers à conserver


def get_current_version():
    """Récupère la version actuelle à partir du fichier config.txt."""
    try:
        if not os.path.exists(CURRENT_VERSION_FILE):
            raise FileNotFoundError(f"Le fichier {CURRENT_VERSION_FILE} est introuvable.")

        with open(CURRENT_VERSION_FILE, "r") as f:
            for line in f:
                if line.strip().startswith("version:"):
                    return line.split(":")[1].strip()  # Renvoie la version sous la forme `v1.x-r`
    except Exception as e:
        print(f"Erreur lors de la lecture de la version actuelle : {e}")
    return None


def get_latest_release():
    """Récupère les informations sur la dernière release depuis GitHub."""
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        data = response.json()
        tag_name = data["tag_name"]  # Version de la release, ex: `v1.4-r`
        download_url = data["assets"][0]["browser_download_url"]  # URL du fichier zip
        return tag_name, download_url
    else:
        raise Exception(f"Erreur lors de la récupération des releases: {response.status_code}")


def download_and_extract_zip(url, target_folder):
    """Télécharge et extrait un fichier ZIP."""
    zip_path = "latest_release.zip"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_folder)
    os.remove(zip_path)


def update_application():
    """Met à jour l'application."""
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()

    if current_version != latest_version:
        print(f"Nouvelle version disponible: {latest_version} (actuelle: {current_version})")
        print("Téléchargement et mise à jour en cours...")
        download_and_extract_zip(download_url, "update_temp")

        # Sauvegarder les fichiers à conserver
        for file in KEEP_FILES:
            if os.path.exists(file):
                shutil.copy(file, "update_temp")

        # Remplacer les fichiers actuels
        for item in os.listdir("update_temp"):
            s = os.path.join("update_temp", item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.move(s, d)
            else:
                shutil.move(s, d)

        # Nettoyer le dossier temporaire
        shutil.rmtree("update_temp")
        messagebox.showinfo("Mise à jour", "Une mise à jour à été effectuée. Redémarrez l'application.")
    else:
        print("Aucune mise à jour disponible. Vous utilisez déjà la dernière version.")


