import os
import launch
import platform
import subprocess
import importlib  
mdc = importlib.import_module("scripts.model-downloader-cn")

has_aria2c = mdc.check_aria2c()

if platform.system() == "Linux":
    if not has_aria2c:
        launch.run("apt -y install -qq aria2", "正在安装 aria2 加速模型下载")
