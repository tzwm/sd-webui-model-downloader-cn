import os
import launch
import platform
import subprocess
from scripts.util import check_aria2c

has_aria2c = check_aria2c()

if platform.system() == "Linux":
    if not has_aria2c:
        launch.run("apt -y install -qq aria2", "正在安装 aria2 加速模型下载")
