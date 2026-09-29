import os

import pytest
import llm_service
from fastapi.testclient import TestClient

from exceptions import (
    AIServiceError,
    AIServiceTimeoutError,
    AIServiceConnectionError
)
from api import app
from database import Database
from dependencies import get_db

@pytest.fixture
def client():
    if os.path.exists("test.db"):
        os.remove("test.db")
    def get_test_db():
        return Database("test.db")
    app.dependency_overrides[get_db] = get_test_db
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    if os.path.exists("test.db"):
        os.remove("test.db")

def test_get_conversations(client):
    response = client.get("/conversations")
    assert response.status_code == 200
def test_create_conversation(client):
    response = client.post(
        "/conversations",
        json={"title":"pytest conversation"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "pytest conversation"
    assert "id" in data
def test_get_nonexistent_conversation(client):
    response = client.get("/conversations/99999999")
    assert response.status_code == 404
    data = response.json()["detail"] == "Conversation not found"
def test_create_conversation_without_title(client):
    response = client.post(
        "/conversations",
        json={}
    )
    assert response.status_code == 422
def test_send_message(client,monkeypatch):
    def fake_ask_question(messages):
        return "fake answer"
    monkeypatch.setattr(
        llm_service,
        "ask_question",
        fake_ask_question
    )
    create_response = client.post(
        "/conversations",
        json={"title":"chat test"}
    )
    conversation_id = create_response.json()["id"]

    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content":"hello"}
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "fake answer"

    messages_response = client.get(
        f"/conversations/{conversation_id}/messages"
    )
    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "hello"
    assert messages[1]["content"] == "fake answer"
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

def test_send_messages_timeout(client,monkeypatch):
    def fake_ask_question(messages):
        raise AIServiceTimeoutError("timeout")
    monkeypatch.setattr(
        llm_service,
        "ask_question",
        fake_ask_question
    )
    create_response = client.post(
        "/conversations",
        json={"title":"timeout test"}
    )
    conversation_id = create_response.json()["id"]
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content":"hello"}
    )
    assert response.status_code == 504
    assert response.json()["detail"] == "AI service timeout"

def test_send_messages_connection_error(client,monkeypatch):
    def fake_ask_question(messages):
        raise AIServiceConnectionError("connection error")
    monkeypatch.setattr(
        llm_service,
        "ask_question",
        fake_ask_question
    )
    create_response = client.post(
        "/conversations",
        json={"title":"connection error"}
    )
    conversation_id = create_response.json()["id"]
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content":"hello"}
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "AI service unavailable"
def test_send_messages_ai_error(client,monkeypatch):
    def fake_ask_question(messages):
        raise AIServiceError("failed")
    monkeypatch.setattr(
        llm_service,
        "ask_question",
        fake_ask_question
    )
    create_response = client.post(
        "/conversations",
        json={"title":"error test"}
    )
    conversation_id = create_response.json()["id"]
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content":"hello"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "AI service failed"
