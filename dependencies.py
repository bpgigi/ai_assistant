from fastapi import Depends, HTTPException
from database import Database

def get_db():
    return Database()
def get_existing_conversation(
        conversation_id: int,
        db: Database = Depends(get_db)
):
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation