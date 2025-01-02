import subprocess

from PIL import Image
from pystray import Icon, Menu, MenuItem
import nodes.variables_node as vn
from nodes.translations_node import t

tray_menu = vn.tray_menu
website = vn.website

def create_image():
    return Image.open("../_internal/icon.ico")

def web_open():
    subprocess.run(f"start \"\" {website}", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

def quit_application(tr_menu):
    tr_menu.stop()

def create_menu():
    #current_game_display = last_game if last_game else t("XXX")

    return Menu(
        #MenuItem(f"{t('Current Game/IDE')}: {current_game_display}", lambda: None),
        MenuItem(t("Access the IGN Website"), web_open),
        Menu.SEPARATOR,
        MenuItem(t("Quit the app"), quit_application)
    )

def run_menu():
    global tray_menu

    menu = create_menu()
    tr_menu = Icon(vn.app_name, create_image(), vn.app_name, menu)

    tr_menu.run()

run_menu()


