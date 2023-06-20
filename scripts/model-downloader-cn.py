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

def resp_to_components(resp):
    if resp == None:
        return ["", "", "", "", "", "", "", "", ""]

    return [
        resp["name"],
        resp["type"],
        ", ".join(resp["version"]["trainedWords"]),
        resp["creator"]["username"],
        ", ".join(resp["tags"]),
        resp["version"]["updatedAt"],
        resp["description"],
        resp["version"]["file"]["name"],
        resp["version"]["file"]["downloadUrl"],
    ]


def preview(url):
    ok, resp = request_civitai_detail(url)
    if not ok:
        return [resp] + resp_to_components(None) + [gr.update(interactive=False)]

    has_download_file = False
    if resp["version"]["file"]["downloadUrl"]:
        has_download_file = True

    return ["预览成功"] + resp_to_components(resp) + \
            [gr.update(value=f'下载模型\n{resp["version"]["file"]["name"]}', interactive=has_download_file)]


def trigger_download(filename, url, target_path):
    cmd = f'curl -o {os.path.join(target_path, filename)} "{url}"'
    if check_aria2c():
        cmd = f'aria2c -c -x 16 -s 16 -k 1M -d {target_path} -o {filename} "{url}"'
    print(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    outputs = ""
    while True:
        line = p.stdout.readline()
        if not line:
            break

        outputs = "\n".join([outputs, line.decode('utf-8').strip()])

    return outputs


def download(model_type, filename, url):
    if not (model_type and url and filename):
        return "下载信息缺失"

    target_path = get_model_path(model_type)
    if not target_path:
        return f"暂不支持这种类型：{model_type}"

    return trigger_download(filename, url, target_path)


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
            filename = gr.Textbox(
                visible=False,
                label="model_filename",
                interactive=False,
            )
            download_url = gr.Textbox(
                visible=False,
                label="model_download_url",
                interactive=False,
            )
        with gr.Row():
            gr.Markdown("test")


        def preview_components():
            return [
                name,
                model_type,
                trained_words,
                creator,
                tags,
                updated_at,
                description,
            ]

        def file_info_components():
            return [
                filename,
                download_url,
            ]

        preview_btn.click(
            fn=preview,
            inputs=[inp_url],
            outputs=[result] + preview_components() + \
                file_info_components() + [download_btn]
        )
        download_btn.click(
            fn=download,
            inputs=[model_type] + file_info_components(),
            outputs=[result]
        )

    return [(ui_component, "模型下载", "model_downloader_cn_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
