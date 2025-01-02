import json
import os
import nodes.variables_node as vn
import requests

def login_to_server(url, username, password, verify_ssl=False):
    # Préparer les données de connexion
    data = {
        "username": username,
        "password": password
    }

    try:
        # Effectuer la requête POST
        response = requests.post(url, json=data, verify=verify_ssl)

        # Gérer les réponses
        if response.status_code == 200:
            print("Response JSON:", response.json())
            return {"success": True, "data": response.json()}
        elif response.status_code == 401:
            return {"success": False, "error": "Identifiants invalides"}
        else:
            return {"success": False, "error": f"Erreur {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erreur lors de la requête: {e}"}

def create_account(url, username, password, verify_ssl=False):
    data = {
        "gameUsername": username,
        "password": password
    }

    try:
        # Effectuer la requête POST
        response = requests.post(url, json=data, verify=verify_ssl)
        # Gérer les réponses
        if response.status_code == 200:
            print("Response JSON:", response.json())
            return {"success": True, "data": response.json()}
        elif response.status_code == 401:
            return {"success": False, "error": "Identifiants invalides"}
        else:
            return {"success": False, "error": f"Erreur {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erreur lors de la requête: {e}"}





def check_existing_session(self):
    if os.path.exists(vn.cookie_connect):
        with open(vn.cookie_connect, "r") as file:
            session_data = json.load(file)
            if session_data.get("session_token"):
                return True  # Session exists
    return False
