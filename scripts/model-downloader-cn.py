from scipy.optimize._lsq.least_squares import construct_loss_function
import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr
import requests
import os
import re
import subprocess
import threading

from scripts.util import check_aria2c, get_model_path

API_URL = "http://127.0.0.1:8787/"

def request_civitai_detail(url):
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

def resp_to_preview_component(resp):
    if resp == None:
        return ["", "", "", "", "", "", "", ""]

    return [
        resp["name"],
        resp["type"],
        ", ".join(resp["version"]["trainedWords"]),
        resp["creator"]["username"],
        ", ".join(resp["tags"]),
        resp["version"]["updatedAt"],
        resp["description"],
        resp["version"]["file"]["downloadUrl"],
    ]


def preview(url):
    ok, resp = request_civitai_detail(url)
    if not ok:
        return [resp] + resp_to_preview_component(None) + [gr.update(interactive=False)]


    has_download_file = False
    if resp["version"]["file"]["downloadUrl"]:
        has_download_file = True

    return ["预览成功"] + resp_to_preview_component(resp) + \
            [gr.update(value=f'下载模型\n{resp["version"]["file"]["name"]}', interactive=has_download_file)]


def trigger_download(file_info, target_path, result_text):
    cmd = f'curl -o {os.path.join(target_path, file_info["name"])} "{file_info["downloadUrl"]}"'
    if check_aria2c():
        cmd = f'aria2c -c -x 16 -s 16 -k 1M -d {target_path} -o {file_info["name"]} "{file_info["downloadUrl"]}"'
    print(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    outputs = ""
    while True:
        line = p.stdout.readline()
        if not line:
            break

        outputs = "\n".join([outputs, line.decode('utf-8').strip()])
        print(outputs)
        result_text.update(outputs)


def download(url, result_text):
    ok, info = request_civitai_info(url)
    if not ok:
        result_text.update(info)
        return

    update_model_info_to_ui(info)

    target_path = get_model_path(info["type"])
    if not target_path:
        result_text.update("暂不支持这种类型：")
        return

    trigger_download(info["version"]["file"], target_path, result_text)


def on_ui_tabs():
    with gr.Blocks() as ui_component:
        gr.Markdown("Start typing below and then click **Run** to see the output.")
        with gr.Row() as input_component:
            with gr.Column():
                inp_url = gr.Textbox(
                    label="Civitai 模型的页面地址，不是下载链接",
                    placeholder="https://civitai.com/models/9409"
                )
                with gr.Row():
                    preview_btn = gr.Button("预览")
                    download_btn = gr.Button("下载", interactive=False)
                with gr.Row():
                    result = gr.TextArea(
                        label="执行结果",
                        interactive=False
                    )
            with gr.Column() as preview_component:
                name = gr.Textbox(label="名称", interactive=False)
                model_type = gr.Textbox(label="类型", interactive=False)
                trained_words = gr.Textbox(label="触发词", interactive=False)
                creator = gr.Textbox(label="作者", interactive=False)
                tags = gr.Textbox(label="标签", interactive=False)
                updated_at = gr.Textbox(label="最近更新时间", interactive=False)
                with gr.Accordion("介绍", open=False):
                    description = gr.HTML()
        with gr.Row(visible=False):
            download_url = gr.Textbox(label="下载地址", interactive=False)
        with gr.Row():
            gr.Markdown("test")


        def preview_outputs():
            return [
                name,
                model_type,
                trained_words,
                creator,
                tags,
                updated_at,
                description,
                download_url,
            ]

        preview_btn.click(
            fn=preview,
            inputs=[inp_url],
            outputs=[result] + preview_outputs() + [download_btn],
        )
        download_btn.click(
            fn=download,
            inputs=[download_url],
            outputs=[result]
        )

    return [(ui_component, "模型下载", "model_downloader_cn_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
