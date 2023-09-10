import uuid
from modules import script_callbacks, shared
from modules.paths_internal import models_path, data_path
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Annotated
import gradio as gr
import html
import os
import time
from PIL import Image
import numpy as np
import subprocess
import json

pre_path = "/model_downloader_cn"
current_path = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = "tmp/model-downloader-cn"

TASK_STATUS = {
    "downloading": "downloading",
    "success": "success",
    "failure": "failure",
}

def check_aria2c():
    try:
        subprocess.run("aria2c", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def get_model_path(model_type):
    co = shared.cmd_opts
    pj = os.path.join
    MODEL_TYPE_DIR = {
        "Checkpoint": ["ckpt_dir", pj(models_path, 'Stable-diffusion')],
        "LORA": ["lora_dir", pj(models_path, 'Lora')],
        "TextualInversion": ["embeddings_dir", pj(data_path, 'embeddings')],
        "Hypernetwork": ["hypernetwork_dir", pj(models_path, 'hypernetworks')],
        # "AestheticGradient": "",
        # "Controlnet": "", #controlnet-dir
        "LoCon": ["lyco_dir", pj(models_path, 'LyCORIS')],
        "VAE": ["vae_dir", pj(models_path, 'VAE')],
    }

    dir_list = MODEL_TYPE_DIR.get(model_type)
    if dir_list == None:
        return None

    if hasattr(co, dir_list[0]) and getattr(co, dir_list[0]):
        return getattr(co, dir_list[0])
    else:
        return dir_list[1]

def download_model(model_type, filename, url, output_path):
    if not (model_type and url and filename):
        return False, "下载信息缺失"

    target_path = get_model_path(model_type)
    if not target_path:
        return False, f"暂不支持这种类型：{model_type}"

    target_file = os.path.join(target_path, filename)
    if os.path.exists(target_file):
        return False, f"已经存在了，不重复下载：\n{target_file}"

    cmd = f'curl -o "{target_file}" "{url}" 2>&1 > {output_path}'
    if check_aria2c():
        cmd = f'aria2c -c -x 16 -s 16 -k 1M -d "{target_path}" -o "{filename}" "{url}" 2>&1 > {output_path}'

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="UTF-8"
    )
    status_output = ""
    if result.returncode == 0:
        status_output = True, f"下载成功，保存到：\n{target_file}\n{result.stdout}"
    else:
        status_output = False, f"下载失败了，错误信息：\n{result.stdout}"

    return status_output


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as view:
        with gr.Row():
            path = f"{pre_path}/index.html?inwebui=true&timestamp={int(time.time())}"
            gr.HTML(f"""
                <iframe id="model_downloader_cn_frame" src="{html.escape(path)}"
                  style="width: 100%; height: 640px;"></iframe>
            """)

    return [(view, "好捏模型", "model_downloader_cn_tab")]

def on_app_started(_: gr.Blocks, app: FastAPI):
    os.makedirs(RESULT_PATH, exist_ok=True)

    @app.post(pre_path + "/download_tasks/")
    def create_download_task(
        model_type: str,
        filename: str,
        url: str,
        md5: str | None = None,
        ref: str | None = None,
    ):
        task_id = str(uuid.uuid4())
        task_info = {
            "id": task_id,
            "model_type": model_type,
            "filename": filename,
            "url": url,
            "md5": md5,
            "ref": ref,
            "status": TASK_STATUS["downloading"],
            "status_text": "",
        }

        with open(f"{RESULT_PATH}/{task_id}.json", 'w') as json_file:
            json.dump(task_info, json_file)

        status, ret = download_model(
            model_type,
            filename,
            url,
            f"{RESULT_PATH}/{task_id}.out",
        )

        if status:
            task_info["status"] = TASK_STATUS["success"]
        else:
            task_info["status"] = TASK_STATUS["failure"]
        task_info["status_text"] = ret

        with open(f"{RESULT_PATH}/{task_id}.json", 'w') as json_file:
            json.dump(task_info, json_file)

        return task_id


    @app.get(pre_path + "/download_tasks/{task_id}")
    def get_download_task(task_id):
        info_path = f"{RESULT_PATH}/{task_id}.json"
        output_path = f"{RESULT_PATH}/{task_id}.out"
        if not (os.path.exists(info_path) and os.path.exists(output_path)):
            raise HTTPException(status_code=404, detail="task not found")

        with open(info_path, "r") as file:
            info = json.loads(file.read())

        with open(output_path, "r") as file:
            output = file.read()

        info.update({
            "output": output,
        })

        return info

    @app.post(pre_path + "/download_tasks")
    def get_download_tasks():
        return "TODO"

    static_path = f"{current_path}/../good-to-nie/build"
    app.mount(
        pre_path,
        StaticFiles(directory=static_path),
        name="model_downloader_cn-fe-static")


script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_tabs(on_ui_tabs)
