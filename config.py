# Please install OpenAI SDK first: `pip3 install openai`
import os
import json
from openai import OpenAI

#不是接受question而是messages，只需要接收数据，config.py 根本不用知道：history.json 在哪里，User 是什么，历史怎么保存
def ask_question(messages):
    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")
    with open("prompt.json", "r", encoding="utf-8") as f:
        prompt = json.load(f)
    # with open("history.json", "r", encoding="utf-8") as f:
    #     messages = json.load(f)
    all_messages =  [
        {"role": "system", "content": prompt},
    ] + messages
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=all_messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    print(response.choices[0].message.content) #-----><class 'str'>
    # print(type(response.choices[0].message.content))
    # answer = response.choices[0].message.content
    return response.choices[0].message.content
