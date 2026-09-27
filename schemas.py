from pydantic import BaseModel
#定义HTTP请求的数据应该长什么样，什么样的请求是合法的
class ConversationCreate(BaseModel):
    title: str
class MessageCreate(BaseModel):
    content: str