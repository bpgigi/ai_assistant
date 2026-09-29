import os
from unittest import result

import pytest
from database import Database

@pytest.fixture
def db():
    if os.path.exists('test.db'):
        os.remove('test.db')
    database = Database("test.db")
    yield database
    if os.path.exists('test.db'):
        os.remove('test.db')

def test_create_conversation(db):
    conversation_id = db.create_conversation("pytest test")
    result = db.get_conversation(conversation_id)

    assert result is not None
    assert result[1] == "pytest test"

def test_delete_conversation(db):
    conversation_id = db.create_conversation("pytest test delete")
    delete_count = db.delete_conversation(conversation_id)
    result = db.get_conversation(conversation_id)

    assert result is None
    assert delete_count == 1
def test_get_nonexistent_conversation(db):
    result = db.get_conversation(999)
    assert result is None
def test_add_and_get_messages(db):
    conversation_id = db.create_conversation("chat")

    db.add_message(
        conversation_id,
        "user",
        "hello"
    )
    messages = db.get_messages(conversation_id)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "hello"
def test_delete_messages(db):
    conversation_id = db.create_conversation("delete messages")

    db.add_message(
        conversation_id,
        "user",
        "hello1"
    )
    db.add_message(
        conversation_id,
        "user",
        "hello2"
    )
    delete_count = db.delete_messages(conversation_id)

    assert delete_count == 2
    assert db.get_messages(conversation_id) == []