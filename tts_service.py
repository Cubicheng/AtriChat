import os
from gradio_client import Client, handle_file
from playsound import playsound
import threading  # 用于异步播放语音

# 初始化 TTS 客户端
client = Client("http://127.0.0.1:7860/")
# 文本生成语音（异步播放）
def text2speech_async(jp_text, status_queue):

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

        status_queue.put("⏳ Atri酱正在说话！")

        # play_audio(filepath)  # 播放生成的语音
        playsound(filepath)

        print("语音播放完毕")

        os.remove(filepath)

        status_queue.put(None)

    # 启动异步线程播放语音
    threading.Thread(target=run_tts).start()
