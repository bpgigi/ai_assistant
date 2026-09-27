from fastapi import APIRouter, HTTPException

from database import Database
from schemas import ConversationCreate

router = APIRouter()
db = Database()
@router.get("/conversations")
def get_conversations():
    rows = db.get_conversations()
    return [
        {
            "id":row[0],
            "title":row[1]
        }
        for row in rows
    ]
@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id:int):
    row = db.get_conversation(conversation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id":row[0],
        "title":row[1]
    }

@router.post("/conversations")
def create_conversation(conversation: ConversationCreate):
    conversation_id = db.create_conversation(conversation.title)
    return {
        "id":conversation_id,
        "title":conversation.title
    }
@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id:int):
    rowcount = db.delete_conversation(conversation_id)
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "content":"Conversation deleted",
        "id":conversation_id
    }
#缺update