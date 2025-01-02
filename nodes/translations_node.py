import os
import sys
import json
from tkinter import messagebox
import mysql.connector
from db_credentials import TRANSLATION_DB

from managers.config_manager import ConfigManager
import nodes.variables_node as vn

config_manager = ConfigManager()
translations_cache = vn.translations_cache


def download_translations():
    global translations_cache
    try:
        conn = mysql.connector.connect(**TRANSLATION_DB)
    except mysql.connector.Error as e:
        messagebox.showerror("Connexion Error", f"Unable to connect to database. Error: {e}")
        sys.exit(1)

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT language, `key`, `value` FROM translations')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        translations = {}
        for lang, key, value in rows:
            if lang not in translations:
                translations[lang] = {}
            translations[lang][key] = value

        with open(vn.translation_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)

        translations_cache = translations
        print("Translations successfully downloaded and cached.")

    except Exception as e:
        print(f"Error downloading translations: {e}")
        if os.path.exists(vn.translation_file):
            with open(vn.translation_file, 'r', encoding='utf-8') as f:
                translations_cache = json.load(f)


def load_translations_from_file():
    global translations_cache
    download_translations()
    try:
        with open(vn.translation_file, 'r', encoding='utf-8') as f:
            translations_cache = json.load(f)
        print("Translations loaded from file.")
    except FileNotFoundError:
        print("Translation file not found. Downloading translations...")
        download_translations()
    except Exception as e:
        print(f"Error loading translations from file: {e}")


def t(key):
    lang = config_manager.get('language', 'EN').upper()
    if lang not in translations_cache:
        print(f"Warning: Language '{lang}' not found in translations. Falling back to key.")
        return key
    return translations_cache.get(lang, {}).get(key, key)