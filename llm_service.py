
from config import settings
from tools import tools, tool_functions, tool_argument_models
import json
import logging
logger = logging.getLogger(__name__)
from openai import OpenAI
from openai import AuthenticationError, APITimeoutError, APIConnectionError
from exceptions import (
    AIServiceError,
    AIServiceTimeoutError,
    AIServiceConnectionError,
    ToolExecutionError,
)

client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url
        )
extra_body = None
if settings.thinking_enabled:
    extra_body = {"thinking": {"type": "enabled"}}
def ask_question(messages):
    try:
        step = 0
        while True:
            step += 1
            if step > 5:
                raise RuntimeError("Agent exceeded max steps")

            response = client.chat.completions.create(
                model=settings.model,
                messages=messages,
                tools=tools,
                stream=False,
                reasoning_effort=settings.reasoning_effort,
                extra_body=extra_body
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                #Json 字符串转dict
                arguments = json.loads(tool_call.function.arguments)

                logger.info(
                    "Tool call:%s arguments:%s",
                    tool_name,
                    arguments
                )

                func = tool_functions.get(tool_name)
                if func is None:
                    raise ValueError("Unknown tool")

                argument_model = tool_argument_models.get(tool_name)

                if argument_model is None:
                    raise ValueError("Unknown tool argument model")

                validated = argument_model.model_validate(arguments)
                validated_arguments = validated.model_dump()

                try:
                    result = func(**validated_arguments)
                    tool_content = str(result)

                    logger.info(
                        "Tool result: %s -> %s",
                        tool_name,
                        result
                    )
                except ToolExecutionError as e:
                    logger.warning(
                        "Tool execution failed: %s - %s",
                        tool_name,
                        e
                    )
                    tool_content = f"Tool execution failed: {e}"

                messages.append({
                    "role":"tool",
                    "tool_call_id":tool_call.id,
                    "content":tool_content
                })

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
        logger.exception("AI service error")
        raise AIServiceError("AI service error") from e
