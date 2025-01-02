import os

# Main Variables
last_game = None
start_time = None
icon = None
translations_cache = {}
shutdown_flag = False
translation_file = "_internal/trad.json"
website = "http://ign.edl360.fr"

# NoteNode Variables
session_file = "instagram_session.json"
creds = "creds.txt"

# GhUpdate Variables
github_api_url = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
infos_file = "../_internal/infos.txt"
exe = "IGNoteIntegration.exe"
rl_url = "https://api.github.com/repos/gltdevlop/InstagramNoteIntegration/releases/latest"
update_script_name = "update.bat"
latest_rl_zip_path = "latest_release.zip"

# ConfigMng Variables
def_cfg = {
        "language": "en",
        "time_update": False,
        "share_data": True
    }

# Others Variables :
if os.path.exists(infos_file):
    with open(infos_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("app-release-name:"):
                app_name = line.split(":")[1].strip()


