import streamlit as st
import os
from openai import OpenAI
#设置网页配置
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
if "messages" not in st.session_state:
    st.session_state["messages"] = []
st.title("AI小助手")

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("ai").write(message["content"])

client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")

question = st.chat_input("Say anything")
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
            {"role": "system", "content": "你是大笨猪，一个ai高手"}
        ]+all_messages,

        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    st.chat_message("ai").write(response.choices[0].message.content)
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

