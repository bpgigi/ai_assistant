from pydantic import BaseModel
#定义HTTP请求的数据应该长什么样，什么样的请求是合法的
class ConversationCreate(BaseModel):
    title: str
class MessageCreate(BaseModel):
    content: str

class ConversationResponse(BaseModel):
    id: int
    title: str
class MessageResponse(BaseModel):
    role:str
    content: str
class MessageAnswerResponse(BaseModel):
    answer: str