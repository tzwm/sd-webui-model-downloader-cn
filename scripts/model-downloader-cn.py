from modules import script_callbacks, shared
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
import html
import os
import time

pre_path = "/model_downloader_cn"
current_path = os.path.dirname(os.path.abspath(__file__))

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as view:
        with gr.Row():
            path = f"{pre_path}/index.html?timestamp={int(time.time())}"
            gr.HTML(f"""
                <iframe id="model_downloader_cn_frame" src="{html.escape(path)}"
                  style="width: 100%; height: 640px;"></iframe>
            """)

    return [(view, "好捏模型", "model_downloader_cn_tab")]

def on_app_started(_: gr.Blocks, app: FastAPI):
    static_path = f"{current_path}/../good-to-nie/build"
    app.mount(
        pre_path,
        StaticFiles(directory=static_path),
        name="model_downloader_cn-fe-static")

script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_tabs(on_ui_tabs)
