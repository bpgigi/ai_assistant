from fastapi import APIRouter, HTTPException, Depends

from database import Database
from dependencies import get_db,get_existing_conversation
from schemas import ConversationCreate,ConversationResponse

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)

@router.get("/",response_model=list[ConversationResponse])
def get_conversations(db:Database=Depends(get_db)):
    rows = db.get_conversations()
    return [
        {
            "id":row[0],
            "title":row[1]
        }
        for row in rows
    ]
@router.get("/{conversation_id}",response_model=ConversationResponse)
def get_conversation(
        conversation = Depends(get_existing_conversation)
):

    return {
        "id":conversation[0],
        "title":conversation[1]
    }

@router.post("/",response_model=ConversationResponse,status_code=201)
def create_conversation(conversation: ConversationCreate, db:Database=Depends(get_db)):
    conversation_id = db.create_conversation(conversation.title)
    return {
        "id":conversation_id,
        "title":conversation.title,
    }
@router.delete("/{conversation_id}",status_code=200)
def delete_conversation(
        conversation_id:int,
        conversation = Depends(get_existing_conversation),
        db:Database=Depends(get_db)
):
    db.delete_conversation(conversation_id)
    return {
        "content":"Conversation deleted",
        "id":conversation_id
    }
#缺update