from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import Database
from Conversation import Conversation
from assistant import Assistant

app = FastAPI()
db = Database()

class ConversationCreate(BaseModel):
    title: str
class MessageCreate(BaseModel):
    content: str

@app.post("/conversation")
def create_conversation(conversation: ConversationCreate):
    conversation_id = db.create_conversation(conversation.title)
    return {
        "id": conversation_id,
        "title": conversation.title,
    }
@app.get("/conversations")
def get_conversations():
    rows = db.get_conversations()
    return [
        {
            "id":row[0],
            "title":row[1]
        }
        for row in rows
    ]
@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404,
                            detail="Conversation not found")
    messages = db.get_messages(conversation_id)
    return messages
@app.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, message: MessageCreate):
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404,detail="Conversation not found")
    conversation = Conversation(conversation_id)
    assistant = Assistant(conversation)

    answer = assistant.ask_ai(message.content)
    if answer is None:
        raise HTTPException(status_code=500,detail="AI request failed")
    return {
        "answer": answer
    }
@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    delete_count = db.delete_conversation(conversation_id)
    if delete_count == 0:
        raise HTTPException(status_code=404,detail="Conversation not found")
    return{
        "message": "Conversation deleted",
        "id": conversation_id
    }