from pydantic import BaseModel
from exceptions import ToolExecutionError

from datetime import datetime
from zoneinfo import ZoneInfo

class NumbersArguments(BaseModel):
    a: float
    b: float
class TimeArguments(BaseModel):
    timezone: str

def add_numbers(a:float, b:float) -> float:
    return a+b
def multiply_numbers(a:float, b:float) -> float:
    return a*b
def get_current_time(timezone:str) -> str:
    try:
        now = datetime.now(ZoneInfo(timezone))
        return now.isoformat()
    except Exception as e:
        raise ToolExecutionError("Invalid timezone") from e

#tool schema
tools = [
    {
        "type":"function",
        "function":{
            "name":"add_numbers",
            "description":"计算两个数字之和",
            "parameters":NumbersArguments.model_json_schema()
        }
    },
    {
        "type":"function",
        "function":{
            "name":"multiply_numbers",
            "description":"计算两个数的乘积",
            "parameters":NumbersArguments.model_json_schema()
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_current_time",
            "description":"获取指定IANA时区的当前时间，例如Asia/Tokyo、America/New_York",
            "parameters":TimeArguments.model_json_schema()
        }
    }
]

#参数检验模型映射
tool_argument_models = {
    "add_numbers":NumbersArguments,
    "multiply_numbers":NumbersArguments,
    "get_current_time":TimeArguments
}

#工具名—->Python函数映射
tool_functions = {
    "add_numbers":add_numbers,
    "multiply_numbers":multiply_numbers,
    "get_current_time":get_current_time,
}