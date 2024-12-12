import requests

# Remplace par ton token d'accès
ACCESS_TOKEN = "token"

# Endpoint pour récupérer des statistiques liées au compte Instagram
url = "https://graph.instagram.com/me"
params = {
    "fields": "id,username",
    "access_token": ACCESS_TOKEN
}

# Requête GET
response = requests.get(url, params=params)

# Afficher la réponse
if response.status_code == 200:
    print("Requête réussie !")
    print("ID :", response.json().get("id"))
    print("Nom d'utilisateur :", response.json().get("username"))
else:
    print("Erreur avec la requête :", response.status_code)
    print(response.text)