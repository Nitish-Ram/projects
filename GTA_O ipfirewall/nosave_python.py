import os
import sys
import subprocess
import keyboard
import time
from threading import Thread
import ctypes

ip = "192.81.241.171"
rule_name = "conductor_bypass"

def run(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def enable():
    cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=block remoteip={ip}'
    run(cmd)

def disable():
    cmd = f'netsh advfirewall firewall delete rule name="{rule_name}"'
    run(cmd)

def run_as_admin():
    if not is_admin():
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        subprocess.call(f'powershell Start-Process python -ArgumentList "{sys.argv[0]} {params}" -Verb RunAs', shell=True)
        sys.exit()

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def listen_hotkeys():
    keyboard.add_hotkey('ctrl+f9', enable)
    keyboard.add_hotkey('ctrl+f12', disable)
    keyboard.wait()

if __name__ == "__main__":
    run_as_admin()
    disable()
    Thread(target=listen_hotkeys, daemon=True).start()
    import atexit
    atexit.register(disable)
    while True:
        time.sleep(1)