import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",  # 布局
    initial_sidebar_state="expanded",  # 控制的是侧边栏的状态
    menu_items={}
)


# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果 sessions 目录不存在, 则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载sessions目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return sorted(session_list, reverse=True)  # 排序让最新会话排在前面


# 加载指定的会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")


# 补全：删除会话功能
def delete_session(session_name):
    try:
        file_path = f"sessions/{session_name}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
        # 如果删除的是当前正在聊天的会话，重置聊天状态
        if st.session_state.current_session == session_name:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")


# 初始化聊天信息（放在渲染逻辑最前面，确保变量已初始化）
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 大标题
st.title("AI智能伴侣")

# Logo (请确保项目目录下有 resources/logo.png 文件，否则可以先注释掉此行)
try:
    st.logo("resources/logo.png")
except Exception:
    pass

# 系统提示词
system_prompt = """
        你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """

# 展示聊天信息
st.caption(f"当前会话: {st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 创建与AI大模型交互的客户端对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# 左侧的侧边栏
with st.sidebar:
    st.subheader("AI控制面板")

    # 新建会话（修复了 width 报错，并优化了重置逻辑）
    if st.button("新建会话", use_container_width=True, icon="✏️"):
        # 1. 保存当前会话信息
        save_session()
        # 2. 无论当前消息是否为空，点击新建都应生成新会话ID并清空面板
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        save_session()
        st.rerun()

        # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 修复了 width 报错
            if st.button(session, use_container_width=True, icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):
                save_session()  # 切换前先自动保存当前会话
                load_session(session)
                st.rerun()
        with col2:
            # 修复：实现了删除会话信息功能
            if st.button("", use_container_width=True, icon="❌", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    # 伴侣信息
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# 消息输入框
prompt = st.chat_input("请输入您要问的问题")
if prompt:
    # 1. 渲染并保存用户输入的提示词
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 调用 AI 大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )

    # 3. 正确的流式输出展示架构
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # 在聊天框内部创建占位符
        full_response = ""

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                # 在占位符中动态刷新文本，末尾加上“▌”模拟光标效果
                response_placeholder.markdown(full_response + "▌")

        # 流式传输结束，渲染最终无光标版本
        response_placeholder.markdown(full_response)

    # 4. 保存大模型返回的结果并持久化
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()
