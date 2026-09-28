from config import settings
import logging
logger = logging.getLogger(__name__)
from openai import OpenAI
from openai import AuthenticationError, APITimeoutError, APIConnectionError
from exceptions import AIServiceError,AIServiceTimeoutError,AIServiceConnectionError

client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url
        )
extra_body = None
if settings.thinking_enabled:
    extra_body = {"thinking": {"type": "enabled"}}
def ask_question(messages):
    try:
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            stream=False,
            reasoning_effort=settings.reasoning_effort,
            extra_body=extra_body
        )
        return response.choices[0].message.content

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
