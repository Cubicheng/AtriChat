import os
import gradio as gr
from pathlib import Path

# 初始化 ChatGLM
with open('API_KEY.txt', 'r', encoding='utf-8') as file:
    os.environ["ZHIPUAI_API_KEY"] = file.read()

# 读取模板文件
with open('atri_chinese_prompt.txt', 'r', encoding='utf-8') as file:
    atri_chinese_prompt = file.read()

gr.set_static_paths(paths=[Path.cwd().absolute()/"assets"])

with open('css.css', 'r', encoding='utf-8') as file:
    custom_css = file.read()