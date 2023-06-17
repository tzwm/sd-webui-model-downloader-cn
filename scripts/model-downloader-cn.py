from numpy import mat
from pandas.core.indexes.base import F
from sqlalchemy import desc
import modules.scripts as scripts
import gradio as gr
import requests
import os
import re

from modules import script_callbacks

API_URL = "http://127.0.0.1:8787/"

def request_civitai_info(url):
    pattern = r'https://civitai\.com/(.+)'
    m = re.match(pattern, url)
    if not m:
        return False, "不是一个有效的 civitai 页面链接"

    req_url = API_URL + "civitai/" + m.group(1)
    res = requests.get(req_url)

    if res.ok:
        return True, res.json()
    else:
        return False, res.text

def preview(url):
    ok, d = request_civitai_info(url)
    if not ok:
        return d, "", "", "", "", "", "", ""

    return "成功", d["name"], d["type"], ", ".join(d["version"]["trainedWords"]), \
        d["creator"]["username"], ", ".join(d["tags"]), d["version"]["updatedAt"], d["description"]

def download(url):
    ok, d = request_civitai_info(url)
    if not ok:
        return d, "", "", "", "", "", "", ""

    return "成功", d["name"], d["type"], ", ".join(d["version"]["trainedWords"]), \
        d["creator"]["username"], ", ".join(d["tags"]), d["version"]["updatedAt"], d["description"]

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        gr.Markdown("Start typing below and then click **Run** to see the output.")
        with gr.Row():
            with gr.Column():
                inp_url = gr.Textbox(
                    label="Civitai 模型的页面地址，不是下载链接",
                    placeholder="https://civitai.com/models/9409"
                )
                with gr.Row():
                    btn_preview = gr.Button("预览")
                    btn_download = gr.Button("下载")
                with gr.Row():
                    result = gr.TextArea(interactive=False)
            with gr.Column():
                name = gr.Textbox(label="名称", interactive=False)
                model_type = gr.Textbox(label="类型", interactive=False)
                trained_words = gr.Textbox(label="触发词", interactive=False)
                creator = gr.Textbox(label="作者", interactive=False)
                tags = gr.Textbox(label="标签", interactive=False)
                updated_at = gr.Textbox(label="最近更新时间", interactive=False)
                with gr.Accordion("介绍", open=False):
                    description = gr.HTML()

        btn_preview.click(
            fn=preview,
            inputs=inp_url,
            outputs=[result, name, model_type, trained_words, creator, tags, updated_at, description]
        )
        btn_download.click(
            fn=download,
            inputs=inp_url,
            outputs=[result, name, model_type, trained_words, creator, tags, updated_at, description]
        )
        return [(ui_component, "模型下载", "model_downloader_cn_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
