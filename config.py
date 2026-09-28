# Please install OpenAI SDK first: `pip3 install openai`
import os
import json
import logging
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
from openai import OpenAI
from openai import AuthenticationError, APITimeoutError, APIConnectionError
from exceptions import AIServiceError,AIServiceTimeoutError,AIServiceConnectionError
load_dotenv()
#不是接受question而是messages，只需要接收数据，config.py 根本不用知道：history.json 在哪里，User 是什么，历史怎么保存
def ask_question(messages):
    try:
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


        return response.choices[0].message.content
        # answer = ""
        # for chunk in response:
        #     if chunk.choices[0].delta.content is not None:
        #         # print(chunk.choices[0].delta.content,end="")
        #         content = chunk.choices[0].delta.content
        #         print(content,end="",flush=True)
        #         answer += content
        # return answer
    except AuthenticationError as e:
        logger.exception("API认证失败")
        raise AIServiceError("AI service error") from e
    except APITimeoutError as e:
        logger.exception("请求超时")
        raise AIServiceTimeoutError("AI service timeout") from e
    except APIConnectionError as e:
        logger.exception("无法连接服务器")
        raise AIServiceConnectionError("AI service connection failed") from e
    except Exception as e:
        logger.exception("未知AI调用异常")
        raise AIServiceError("AI service error") from e

if __name__ == "__main__":
    pass