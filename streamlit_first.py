import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

#设置网页配置
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

def save_session():
    if st.session_state["messages"]:
        session_data = {
            "nick_name": st.session_state["nick_name"],
            "nature": st.session_state["nature"],
            "current_session": st.session_state["current_session"],
            "messages": st.session_state["messages"]
        }
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as file:
            json.dump(session_data, file, ensure_ascii=False, indent=4)


def generate_session_name():
    return datetime.now().strftime("%y-%m-%d_%H-%M-%S")

def load_sessions():
    session_list = []
    if os.path.exists(f"sessions"):
        file_list = os.listdir("sessions")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    return session_list

def load_session(session_file):
    try:
        if os.path.exists(f"sessions/{session_file}.json"):
            with open(f"sessions/{session_file}.json", "r", encoding="utf-8") as file:
                session_data = json.load(file)
                st.session_state.messages = session_data["messages"]
                st.session_state.current_session = session_file
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
    except Exception :
        st.error("加载会话失败")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "nick_name" not in st.session_state:
    st.session_state["nick_name"] = "大笨猪"
if "nature" not in st.session_state:
    st.session_state["nature"] = "AI"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()
st.title("笨猪帮你导")

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("ai").write(message["content"])

client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")


with st.sidebar:
    st.subheader("助手信息")
    if st.button("新建",width="stretch"):
        #保存新会话
        save_session()
        #创建新会话
        st.session_state["messages"] = []
        st.session_state["current_session"] = generate_session_name()
        save_session()

    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(session,width="stretch",icon="🗒️",key=f"load_{session}"):
                load_session(session)
                st.rerun()
        with col2:
            st.button("",width="stretch",icon="❌️",key=f"delete_{session}")

    nick_name = st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
    # st.sidebar.subheader("伴侣信息")
    # nick_name = st.sidebar.text_input


question = st.chat_input("Say anything")
system_prompt = "你是%s，一个%s高手"
if question:
    st.chat_message("user").write(question)
    st.session_state.messages.append({"role":"user","content":question})
    all_messages = st.session_state.messages
    #print([{"role":"system","content":"你是大笨猪，一个ai高手"}]+all_messages)
    response = client.chat.completions.create(
        model="deepseek-flash",
        # messages=[
        #     {"role":"system","content":"你是大笨猪，一个ai高手"},
        #     *st.session_state.messages
        # ]
        messages=[
            {"role": "system", "content": system_prompt % (nick_name, nature)}
        ]+all_messages,

        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    response_messages = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_messages.chat_message("assistant").write(full_response)
    # st.chat_message("ai").write(response.choices[0].message.content)
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

