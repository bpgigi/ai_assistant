from fastapi import APIRouter, HTTPException

import assistant
from Conversation import Conversation
from schemas import MessageCreate
from database import Database
from Conversation import Conversation
from assistant import Assistant

db = Database()
router = APIRouter()
@router.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    #先检查conversation是否存在
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    #conversation不存在—-》404 ，存在没东西-》[]
    messages = db.get_messages(conversation_id)
    return messages
@router.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, message: MessageCreate):
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation = Conversation(conversation_id)
    assistant = Assistant(conversation)
    answer = assistant.ask_ai(message.content)
    if answer is None:
        raise HTTPException(status_code=500, detail="AI连接失败")
    return {
        "answer": answer
    }