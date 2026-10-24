from pydantic import BaseModel,Field
#定义HTTP请求的数据应该长什么样，什么样的请求是合法的
class ConversationCreate(BaseModel):
    title: str
class MessageCreate(BaseModel):
    content: str
    use_rag: bool = False

class ConversationResponse(BaseModel):
    id: int
    title: str

class SourceResponse(BaseModel):
    text: str
    distance: float
    source: str

class MessageResponse(BaseModel):
    role:str
    content: str
    sources: list[SourceResponse] = Field(default_factory=list)

class MessageAnswerResponse(BaseModel):
    answer: str
    sources:list[SourceResponse] = Field(default_factory=list)


