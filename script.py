import pyautogui
import pyperclip
import time
import pygetwindow as gw
import psutil
import subprocess

def copy_paste(username, password):
    window = gw.getWindowsWithTitle("Riot Client")[0]
    window.activate()
    time.sleep(1)
    pyautogui.PAUSE=0.01
    pyperclip.copy(username)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl','v')
    pyautogui.hotkey('tab')
    pyperclip.copy(password)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl','v')
    pyautogui.hotkey('enter')

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

def launch(username, password, app):
    if not is_process_running("LeagueClient.exe"):
        window = gw.getWindowsWithTitle("Riot Client")
        if not window:
            try:
                subprocess.Popen(app)
                while not window:
                    window = gw.getWindowsWithTitle("Riot Client")
                time.sleep(1)
                copy_paste(username, password)
            except FileNotFoundError:
                print(f"Error: The file {app} was not found.")
            except Exception as e:
                print(f"An error has occurred: {e}")
        else:
            subprocess.run(["taskkill", "/F", "/IM", "RiotClientServices.exe"])
            time.sleep(1)
            subprocess.Popen(app)
            window = gw.getWindowsWithTitle("Riot Client")
            while not window:
                window = gw.getWindowsWithTitle("Riot Client")
            time.sleep(1)
            copy_paste(username, password)
    else:
        print("League of Legends is already running.")