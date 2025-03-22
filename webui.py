import queue
import threading
import gradio as gr
from llm_service import generate_atri_response
from tts_service import text2speech_async,client
from config_init import custom_css

# 定义 Gradio 界面
def chat_with_atri(user_input, chat_history):
    yield chat_history, gr.update(value="⏳ Atri酱正在思考...", visible=True)

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

    # 第一次返回：聊天记录 + 初始状态
    yield chat_history, gr.update(value="⏳Atri酱的语音模块正在飞速运转...", visible=True)

    status_queue = queue.Queue()

    # 启动异步任务（传入队列）
    threading.Thread(target=text2speech_async, args=(jp_text, status_queue)).start()

    # 持续监听队列状态
    while True:
        try:
            new_status = status_queue.get(timeout=0.1)
            if new_status is None:  # 结束信号
                yield chat_history, gr.update(visible=False)
                break
            yield chat_history, gr.update(value=new_status, visible=True)
        except queue.Empty:
            continue

# 创建 Gradio 界面
with gr.Blocks(title="AtriChat", css=custom_css) as demo:
    gr.Markdown("# 和 ATRI 酱聊天！")
    
    # 纵向排列组件
    with gr.Column():
        chatbot = gr.Chatbot(label="聊天记录", height=400, type="messages")  # 聊天记录
        status_label = gr.Label(label="系统状态", value="", visible=False)  # 状态标签
        user_input = gr.Textbox(label="输入你的消息", placeholder="输入消息并按回车...")  # 输入框
        submit_button = gr.Button("发送", variant="primary")  # 发送按钮
        temp_user_input = gr.State()

    # 设置交互逻辑
    submit_button.click(
        lambda x: ("", x),
        inputs=user_input,
        outputs=[user_input, temp_user_input]
    ).then(
        fn=chat_with_atri,
        inputs=[temp_user_input, chatbot],
        outputs=[chatbot, status_label]
    )
    user_input.submit(
        lambda x: ("", x),
        inputs=user_input,
        outputs=[user_input, temp_user_input]
    ).then(
        fn=chat_with_atri,
        inputs=[temp_user_input, chatbot],
        outputs=[chatbot, status_label]
    )

# 启动 Gradio 应用
demo.queue(default_concurrency_limit=3)
demo.launch(share=True)