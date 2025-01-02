import os
import sys

import psutil
import new_scripts.nodes.variables_node as vn

def is_process_already_running(process_name):
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower() and proc.pid != current_pid:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def detect_process():
    process_name = vn.exe
    if is_process_already_running(process_name):
        sys.exit(0)