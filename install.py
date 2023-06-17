import os
import launch
import platform
import subprocess

def checking():
    try:
        subprocess.run("aria2c", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

has_aria2c = checking()


if platform.system() == "Linux":
    if not has_aria2c:
        launch.run("apt -y install -qq aria2", "Installing requirements for Model Downloader")
