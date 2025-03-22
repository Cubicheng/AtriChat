import os
import gradio as gr
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_community.chat_models import ChatZhipuAI
from gradio_client import Client, handle_file
from playsound import playsound
import threading  # 用于异步播放语音

# 初始化 ChatGLM
with open('API_KEY.txt', 'r', encoding='utf-8') as file:
    os.environ["ZHIPUAI_API_KEY"] = file.read()
chatglm = ChatZhipuAI(model="glm-4", temperature=0.5)

# 读取模板文件
with open('atri_chinese_prompt.txt', 'r', encoding='utf-8') as file:
    atri_chinese_prompt = file.read()

# 创建 PromptTemplate
prompt = PromptTemplate(
    template=atri_chinese_prompt,
    input_variables=["current_scene", "user_input"]
)

# 使用 RunnableSequence 替代 LLMChain
chat_llm = RunnableSequence(prompt | chatglm)

# 定义生成回复的函数
def generate_atri_response(user_input, current_scene="日常对话"):
    # 调用 RunnableSequence 生成回复
    response = chat_llm.invoke({
        "current_scene": current_scene,
        "user_input": user_input
    }).content
    print(f"ATRI: {response}")
    return response

# 初始化 TTS 客户端
client = Client("http://127.0.0.1:7860/")

# 文本生成语音（异步播放）
def text2speech_async(jp_text):

    def run_tts():

        _, filepath = client.predict(
            text=jp_text,
            speaker="ATRI",  # 使用 ATRI 的声音
            sdp_ratio=0.5,
            noise_scale=0.6,
            noise_scale_w=0.9,
            length_scale=1,
            language="JP",  # 日语
            reference_audio=handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav'),
            prompt_mode="Text prompt",
            style_text=None,
            style_weight=0.7,
            api_name="/tts_fn"
        )
        print(f"合成的语音文件路径：{filepath}")
        # play_audio(filepath)  # 播放生成的语音
        playsound(filepath)
        print("语音播放完毕")

    # 启动异步线程播放语音，并设置为守护线程
    threading.Thread(target=run_tts).start()

# 定义 Gradio 界面
def chat_with_atri(user_input, chat_history=None):
    if chat_history is None:
        chat_history = []  # 确保初始值为空列表

    # 生成 ATRI 的回复
    atri_response = generate_atri_response(user_input)
    # 本地调试时使用
    # atri_response = "我是高性能的！"

    # 获取日文翻译
    jp_text = client.predict(
        Sentence=atri_response,
        api_name="/translate"
    )

    # 构造合规消息对象
    user_msg = {"role": "user", "content": user_input}
    bot_msg = {
        "role": "assistant",
        "content": f"{atri_response} \n {jp_text}"
    }

    # 更新聊天记录
    chat_history = chat_history + [user_msg, bot_msg]

    # 启动异步任务进行语音合成和播放
    text2speech_async(jp_text)

    # 返回更新后的聊天记录
    return chat_history

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## 与 ATRI 聊天")
    
    # 纵向排列组件
    with gr.Column():
        chatbot = gr.Chatbot(label="聊天记录", height=400, type="messages")  # 聊天记录
        user_input = gr.Textbox(label="输入你的消息", placeholder="输入消息并按回车...")  # 输入框
        submit_button = gr.Button("发送", variant="primary")  # 发送按钮

    # 设置交互逻辑
    submit_button.click(
        fn=chat_with_atri,
        inputs=[user_input, chatbot],
        outputs=[chatbot]
    )
    user_input.submit(
        fn=chat_with_atri,
        inputs=[user_input, chatbot],
        outputs=[chatbot]
    )

# 启动 Gradio 应用
demo.queue(default_concurrency_limit=3)
demo.launch(debug=True)