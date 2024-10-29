import streamlit as st
from spark_chat_ai import SparkChatAI
import requests
import json
import os
import uuid

# Streamlit 页面配置
st.set_page_config(page_title="映月", page_icon="🌙", layout="wide")
st.title("映月 🌙")
st.write("月出皎兮，佼人僚兮。舒窈纠兮，劳心悄兮。")

# API 凭据输入框
st.sidebar.title("设置API凭据")
app_id = st.sidebar.text_input("SPARKAI_APP_ID")
api_secret = st.sidebar.text_input("SPARKAI_API_SECRET", type="password")
api_key = st.sidebar.text_input("SPARKAI_API_KEY", type="password")
fish_api_key = st.sidebar.text_input("Fish Audio API Key", type="password")

# 定义模型选项和对应的 ID
model_options = {
    "雷军": "738d0cc1a3e9430a9de2b544a466a7fc",
    "学姐": "7f92f8afb8ec43bf81429cc1c9199cb1",
    "央视配音": "59cb5986671546eaa6ca8ae6f29f6d22",
    "蔡徐坤": "e4642e5edccd4d9ab61a69e82d4f8a14",
    "丁真": "54a5170264694bfc8e9ad98df7bd89c3"
}

# 文本到语音转换函数
def text_to_speech(text, reference_id, model_name, fish_api_key):
    url = "https://api.fish.audio/v1/tts"
    headers = {
        "Authorization": f"Bearer {fish_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "reference_id": reference_id,
        "chunk_length": 200,
        "normalize": True,
        "format": "mp3",
        "mp3_bitrate": 64,
        "latency": "normal"
    }

    # 发送 POST 请求到 Fish Audio API
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # 创建模型对应的音频文件夹
        audio_folder = f"audios/{model_name}"
        os.makedirs(audio_folder, exist_ok=True)
        # 生成唯一的音频文件名，使用 UUID
        unique_id = uuid.uuid4().hex
        audio_filename = f"{unique_id}.mp3"
        audio_path = os.path.join(audio_folder, audio_filename)
        # 保存生成的语音文件
        with open(audio_path, "wb") as output_file:
            output_file.write(response.content)
        return audio_path
    else:
        st.error(f"生成语音时出错: {response.status_code}, {response.content}")
        return None

# 检查是否填入了 API 凭据
if all([app_id, api_secret, api_key, fish_api_key]):
    # 用户通过下拉选项选择模型
    model_name = st.sidebar.selectbox("请选择一个聊天对象", options=list(model_options.keys()))
    selected_model_id = model_options[model_name]
    st.sidebar.write(f"已选择: {model_name}")

    # 使用 st.session_state 来保持每个模型的 chat_ai 实例
    if 'chat_ai_dict' not in st.session_state:
        st.session_state.chat_ai_dict = {}
    if 'chat_history_dict' not in st.session_state:
        st.session_state.chat_history_dict = {}
    chat_ai_dict = st.session_state.chat_ai_dict
    chat_history_dict = st.session_state.chat_history_dict

    # 初始化星火大模型
    if model_name not in chat_ai_dict:
        chat_ai_dict[model_name] = SparkChatAI(app_id, api_secret, api_key, model_name)
    chat_ai = chat_ai_dict[model_name]

    # 初始化聊天历史
    if model_name not in chat_history_dict:
        chat_history_dict[model_name] = []
    chat_history = chat_history_dict[model_name]

    # 新增：重置对话按钮
    if st.sidebar.button("重置对话"):
        chat_ai.reset_memory()
        chat_history.clear()
        # 删除模型对应的聊天记录文件
        history_file = f"history_{model_name}.json"
        if os.path.exists(history_file):
            os.remove(history_file)
        # 删除模型对应的音频文件夹
        audio_folder = f"audios/{model_name}"
        if os.path.exists(audio_folder):
            for file in os.listdir(audio_folder):
                os.remove(os.path.join(audio_folder, file))
            os.rmdir(audio_folder)
        st.sidebar.success(f"{model_name} 的对话已重置！")

    # 加载历史聊天记录
    history_file = f"history_{model_name}.json"
    if os.path.exists(history_file) and not chat_history:
        with open(history_file, "r", encoding="utf-8") as f:
            chat_history.extend(json.load(f))

    # 定义头像路径
    user_avatar_path = "avatars/user.png"  # 用户头像
    assistant_avatar_path = f"avatars/{model_name}.png"  # 模型对应的头像

    # 显示聊天历史
    st.write(f"与 {model_name} 的聊天记录：")
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            with st.chat_message("user", avatar=user_avatar_path):
                st.write(content)
        else:
            with st.chat_message("assistant", avatar=assistant_avatar_path):
                st.write(content)
                # 显示对应的音频
                audio_path = msg.get("audio_path")
                if audio_path and os.path.exists(audio_path):
                    st.audio(audio_path, format='audio/mp3')

    # 固定输入框在页面底部
    prompt = st.chat_input("在这里输入消息...")  # 移除 avatar 参数

    if prompt:
        # 添加用户输入到聊天历史并保存
        message = {"role": "user", "content": prompt}
        chat_history.append(message)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)

        # 在界面上显示用户消息
        with st.chat_message("user", avatar=user_avatar_path):
            st.write(prompt)

        # 调用星火大模型获取回复
        with st.chat_message("assistant", avatar=assistant_avatar_path):
            # 添加加载动画
            with st.spinner("正在生成回复，请稍候..."):
                response = chat_ai.get_response(prompt)
                # 更新助手消息
                st.write(response)

            # 使用星火大模型的回答调用 Fish Audio 进行文本到语音转换
            with st.spinner("正在生成语音，请稍候..."):
                audio_path = text_to_speech(response, selected_model_id, model_name, fish_api_key)
                if audio_path:
                    # 播放生成的语音
                    st.audio(audio_path, format='audio/mp3')
                else:
                    st.error("语音生成失败")

        # 添加模型回复到聊天历史并保存，包括音频文件路径
        message = {"role": "assistant", "content": response, "audio_path": audio_path}
        chat_history.append(message)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)

else:
    st.warning("请在侧边栏填写完整的 API 凭据！")