import uuid
from modules import script_callbacks, shared
from modules.paths_internal import models_path, data_path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import html
import os
import time
import subprocess
import json

pre_path = "/model_downloader_cn"
current_path = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = os.path.join('tmp', 'model-downloader-cn')

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

def update_task_info(info):
    ret_path = os.path.join(RESULT_PATH, info['id'] + '.json')
    with open(ret_path, 'w') as file:
        json.dump(info, file)

def download_model(info):
    model_type = info['model_type']
    filename = info['filename']
    download_url = info['download_url']
    target_path = get_model_path(model_type)
    target_file = os.path.join(target_path, filename)
    output_path = os.path.join(RESULT_PATH, info['id'] + '.out')

    cmd = f'curl -o "{target_file}" "{download_url}" 2>&1 > {output_path}'
    if check_aria2c():
        cmd = f'aria2c -c -x 16 -s 16 -k 1M -d "{target_path}" -o "{filename}" "{download_url}" 2>&1 > {output_path}'

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="UTF-8"
    )

    status = ""
    status_output = ""
    if result.returncode == 0:
        status = TASK_STATUS['success']
        status_output = f"下载成功，保存到：\n{target_file}" #\n{result.stdout}"
    else:
        status = TASK_STATUS['failure']
        status_output = f"下载失败了，错误信息：\n{result.stdout}"

    info['status'] = status
    info['status_text'] = status_output
    update_task_info(info)


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

    #for local testing
    origins = [
        'http://localhost',
        'http://127.0.0.1',
        'http://127.0.0.1:5173',
        'http://localhost:5173',
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post(pre_path + "/download_tasks/")
    async def create_download_task(
        model_type: str,
        filename: str,
        download_url: str,
        md5: str | None,
        ref: str | None,
        background_tasks: BackgroundTasks,
    ):
        target_path = get_model_path(model_type)
        if not target_path:
            raise HTTPException(
                status_code=400,
                detail=f"暂不支持这种类型：{model_type}"
            )

        target_file = os.path.join(target_path, filename)
        if os.path.exists(target_file):
            raise HTTPException(
                status_code=400,
                detail=f"已经存在了，不重复下载：{target_file}"
            )

        task_id = str(uuid.uuid4())
        task_info = {
            "id": task_id,
            "model_type": model_type,
            "filename": filename,
            "download_url": download_url,
            "md5": md5,
            "ref": ref,
            "status": TASK_STATUS["downloading"],
            "status_text": "",
        }
        update_task_info(task_info)

        background_tasks.add_task(
            download_model,
            task_info,
        )

        return task_id


    @app.get(pre_path + "/download_tasks/{task_id}")
    def get_download_task(task_id):
        info_path = os.path.join(RESULT_PATH, task_id + '.json')
        output_path = os.path.join(RESULT_PATH, task_id + '.out')

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

    @app.get(pre_path + "/download_tasks")
    def get_download_tasks():
        cmd = ' | '.join([f"ls -lt {RESULT_PATH}", "grep '.json$'", "awk '{print $NF}'"])
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8"
        )

        ids = [s[:-5] for s in result.stdout.split('\n')]
        ids = [s for s in ids if s != '']

        return {
            'task_ids': ids
        }

    static_path = os.path.join(current_path, '..', 'good-to-nie', 'build')
    app.mount(
        pre_path,
        StaticFiles(directory=static_path),
        name="model_downloader_cn-fe-static")


script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_tabs(on_ui_tabs)
