from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

USERNAME = "gbrt.ee"
PASSWORD = "xxx"

# Initialiser le WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # Ouvrir Instagram
    driver.get("https://www.instagram.com/")

    # Accepter les cookies
    try:
        time.sleep(5)
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Autoriser tous les cookies']"))
        )
        accept_cookies_button.click()
    except Exception as e:
        print("Bouton d'acceptation des cookies non trouvé :", e)

    # Attendre que la page charge
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

    time.sleep(5)

    # Entrer les identifiants
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(USERNAME)
    time.sleep(5)
    password_input.send_keys(PASSWORD)

    # Soumettre le formulaire
    time.sleep(5)

    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Naviguer vers la section des messages privés
    time.sleep(10)

    try:
        prlf= WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Profil']"))
        )
        prlf.click()
    except Exception as e:
        print("Bouton profil pas la :", e)

    try:
        add_note_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//div[contains(@id, 'button') and starts-with(text(), 'Note')] "
            ))
        )
        add_note_btn.click()
        print("Ouverture add note")

    except Exception as e:
        print("Ouverture add note raté :", e)

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    try:
        # Fermer le navigateur
        print("e")
    except Exception as e:
        print("Erreur lors de la fermeture du navigateur :", e)
