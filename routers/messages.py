from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_db,get_existing_conversation
from schemas import MessageCreate,MessageResponse,MessageAnswerResponse
from database import Database
from Conversation import Conversation
from assistant import Assistant

router = APIRouter(
    prefix="/conversations",
    tags=["messages"]
)
@router.get("/{conversation_id}/messages",response_model=list[MessageResponse])
def get_messages(
        conversation_id: int,
        conversation = Depends(get_existing_conversation),
        db: Database = Depends(get_db)
):
    messages = db.get_messages(conversation_id)
    return messages
@router.post(
    "/{conversation_id}/messages",
    response_model=MessageAnswerResponse
)
def send_message(
        conversation_id: int,
        message: MessageCreate,
        conversation_row = Depends(get_existing_conversation),
        db: Database = Depends(get_db)
):

    conversation = Conversation(conversation_id,db)
    assistant = Assistant(conversation)
    answer = assistant.ask_ai(message.content)

    return {
        "answer": answer
    }