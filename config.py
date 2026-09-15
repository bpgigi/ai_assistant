# Please install OpenAI SDK first: `pip3 install openai`
import os
import json
from openai import OpenAI
def ask_question(question):
    # question = input("What is the question:")
    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")
    with open("prompt.json", "r", encoding="utf-8") as f:
        prompt = json.load(f)
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    print(response.choices[0].message.content) #-----><class 'str'>
    # print(type(response.choices[0].message.content))
    # answer = response.choices[0].message.content
    return response.choices[0].message.content
