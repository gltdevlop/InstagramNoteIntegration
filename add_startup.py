import os
import winshell
import variables_node as vn
from win32com.client import Dispatch

exe = vn.exe

def add_startup():
    if os.path.exists(exe):
        exe_path = os.getcwd() + "\\IGNoteIntegration.exe"
        shortcut_name = "IGNoteIntegration.lnk"
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, shortcut_name)
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_path  # Path to the .exe
        shortcut.WorkingDirectory = os.path.dirname(exe_path)  # Optional
        shortcut.IconLocation = exe_path  # Optional: Use the app's icon
        shortcut.save()

add_startup()