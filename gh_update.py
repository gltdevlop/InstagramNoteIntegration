import requests
import zipfile
import os
import shutil
import subprocess
import sys
import time

# URL de l'API GitHub pour récupérer les informations de la dernière release
GITHUB_API_URL = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
CURRENT_VERSION_FILE = "_internal/config.txt"  # Fichier contenant la version actuelle
EXE_NAME = "IGNoteIntegration.exe"  # Nom de l'exécutable principal

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


def create_update_script():
    """Crée un script batch pour terminer la mise à jour après la fermeture."""
    script_name = "update.bat"
    with open(script_name, "w") as f:
        f.write(f"@echo off\n")
        f.write(f"echo Mise à jour en cours...\n")
        f.write(f"timeout /t 2 > nul\n")  # Attendre 2 secondes
        f.write(f"del {EXE_NAME}\n")  # Supprimer l'ancien .exe
        f.write(f"move update_temp\\{EXE_NAME} .\\{EXE_NAME}\n")  # Déplacer le nouveau .exe
        f.write(f"rmdir /s /q _internal\n")  # Supprimer le dossier internal
        f.write(f"rename internal _internal\n")
        f.write(f"rmdir /s /q update_temp\n")  # Supprimer le dossier temporaire
        f.write(f"start {EXE_NAME}\n")  # Relancer l'application
        f.write(f"del %~f0\n")  # Supprimer le script batch lui-même

    return script_name


def update_application():
    """Met à jour l'application."""
    current_version = get_current_version()
    latest_version, download_url = get_latest_release()

    if current_version != latest_version:
        print(f"Nouvelle version disponible: {latest_version} (actuelle: {current_version})")
        print("Téléchargement et préparation de la mise à jour...")
        download_and_extract_zip(download_url, "update_temp")

        shutil.copytree("update_temp/_internal", "internal")

        # Créer un script batch pour effectuer la mise à jour
        script_name = create_update_script()
        print("Redémarrage de l'application pour finaliser la mise à jour...")
        subprocess.Popen([script_name])  # Lancer le script batch
        time.sleep(1)
        os.system("taskkill /f /im IGNoteIntegration.exe") # Fermer le programme principal
    else:
        print("Aucune mise à jour disponible. Vous utilisez déjà la dernière version.")


if __name__ == "__main__":
    update_application()
