# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
def ask_question(question):
    # question = input("What is the question:")
    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
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
