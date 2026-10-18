import assistant as assistant_module
import rag.service as rag_service

def fake_retrieve(query,k = 3,threshold = 0.5):
    return []
def fake_retrieve_success(query,k = 3,threshold = 0.5):

    return [
        {
            "text": "FastAPI 使用 Depends 实现依赖注入。",
            "distance": 0.12
        }
    ]
def fake_retrieve_forbidden(query, k=3, threshold=0.5):
    raise AssertionError("普通聊天不应该执行 RAG 检索")
#单轮测试简单假函数
def fake_rewrite_single(question, history):
    assert history == []
    return question

def fake_llm(message):
    raise AssertionError("不应该调用LLM")
def fake_llm_success(messages):
    assert "FastAPI 使用 Depends 实现依赖注入。" in messages[-1]["content"]
    return "Depends 用于依赖注入。"
def fake_llm_normal(messages):
    assert messages[-1]["content"] == "你好"
    return "你好！"

def fake_rewrite_query(question, history):
    assert question == "那它还能依赖其他依赖吗？"

    assert history[0]["content"] == "FastAPI 的 Depends 是什么？"

    return "FastAPI 的 Depends 可以依赖其他依赖吗？"

class FakeConversation:
    def __init__(self):
        self.history = []

    def add_user_message(self, content):
        self.history.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content):
        self.history.append({
            "role": "assistant",
            "content": content
        })

def test_rag_no_results(monkeypatch):
    monkeypatch.setattr(
        assistant_module,
        'retrieve',
        fake_retrieve
    )

    monkeypatch.setattr(
        assistant_module.llm_service,
        "ask_question",
        fake_llm
    )

    monkeypatch.setattr(
        assistant_module.Assistant,
        "load_prompt",
        lambda self: None
    )

    conversation = FakeConversation()
    assistant = assistant_module.Assistant(conversation)
    question = "FastAPI Depends 是什么？"

    answer = assistant.ask_ai(question, use_rag=True)
    assert answer == "知识库中没有找到相关内容"

    assert len(conversation.history) == 2

    assert conversation.history == [
        {
            "role": "user",
            "content": question
        },
        {
            "role": "assistant",
            "content": answer
        }
    ]

def test_rag_with_results(monkeypatch):
    monkeypatch.setattr(
        assistant_module,
        "retrieve",
        fake_retrieve_success
    )

    monkeypatch.setattr(
        assistant_module.llm_service,
        "ask_question",
        fake_llm_success
    )

    monkeypatch.setattr(
        assistant_module.Assistant,
        "load_prompt",
        lambda self: None
    )

    monkeypatch.setattr(
        assistant_module,
        "rewrite_query",
        fake_rewrite_single
    )

    conversation = FakeConversation()
    assistant = assistant_module.Assistant(conversation)

    question = "FastAPI Depends 是什么？"

    # 下面由你补全
    answer = assistant.ask_ai(question, use_rag=True)
    assert answer == "Depends 用于依赖注入。"
    assert len(conversation.history) == 2
    assert conversation.history[0]["content"] == question

def test_normal_chat(monkeypatch):
    monkeypatch.setattr(
        assistant_module,
        "retrieve",
        fake_retrieve_forbidden
    )

    monkeypatch.setattr(
        assistant_module.llm_service,
        "ask_question",
        fake_llm_normal
    )

    monkeypatch.setattr(
        assistant_module.Assistant,
        "load_prompt",
        lambda self: None
    )

    conversation = FakeConversation()
    assistant = assistant_module.Assistant(conversation)

    question = "你好"

    # 下面由你完成
    answer = assistant.ask_ai(question, use_rag=False)
    assert answer == "你好！"
    assert len(conversation.history) == 2

def test_rag_multi_turn(monkeypatch):
    monkeypatch.setattr(
        assistant_module.Assistant,
        "load_prompt",
        lambda self: None
    )

    monkeypatch.setattr(
        assistant_module,
        "rewrite_query",
        fake_rewrite_query
    )

    # 继续替换 retrieve 和 llm_service.ask_question
    monkeypatch.setattr(
        assistant_module,
        "retrieve",
        fake_retrieve_success
    )
    monkeypatch.setattr(
        assistant_module.llm_service,
        "ask_question",
        fake_llm_success
    )

    # 创建 FakeConversation
    conversation = FakeConversation()

    # 模拟第一轮历史
    conversation.add_user_message("FastAPI 的 Depends 是什么？")
    conversation.add_assistant_message("Depends 用于实现依赖注入。")

    # 创建 Assistant
    assistant = assistant_module.Assistant(conversation)

    # 调用第二轮 ask_ai()
    question = "那它还能依赖其他依赖吗？"
    answer = assistant.ask_ai(question, use_rag=True)
    # 验证历史中保存了原始问题
    assert len(conversation.history) == 4

    assert conversation.history[2]["content"] == question
    assert conversation.history[3]["content"] == answer

import pytest
from rag.service import retrieve


def test_retrieve_invalid_k():
    with pytest.raises(ValueError, match="k must be"):
        retrieve("FastAPI", k=0)


def test_retrieve_invalid_threshold():
    with pytest.raises(ValueError, match="threshold must be"):
        retrieve("FastAPI", threshold=-0.1)

class FakeCollection:
    def __init__(self):
        self.last_k = None

    def query(self, query_embeddings, n_results):
        self.last_k = n_results

        return {
            "ids": [["doc_1"]],
            "documents": [["FastAPI 使用 Depends"]],
            "distances": [[0.6]],
            "metadatas": [[{"source": "test.md"}]]
        }
class FakeModel:
    def encode(self, text):
        return [0.1, 0.2, 0.3]

def test_retrieve_threshold_override(monkeypatch):
    fake_collection = FakeCollection()

    monkeypatch.setattr(
        rag_service, "collection", fake_collection
    )
    monkeypatch.setattr(
        rag_service, "get_model", lambda: FakeModel()
    )

    monkeypatch.setattr(
        rag_service.settings, "rag_top_k", 3
    )
    monkeypatch.setattr(
        rag_service.settings, "rag_threshold", 0.5
    )

    # 使用默认阈值
    default_results = rag_service.retrieve("FastAPI")

    # 显式覆盖阈值
    override_results = rag_service.retrieve(
        "FastAPI",
        threshold=0.7
    )

    # TODO 1：验证默认阈值
    assert default_results == []

    # TODO 2：验证覆盖阈值
    assert len(override_results) == 1

    # TODO 3：验证文档 ID
    assert override_results[0]["id"] == "doc_1"

    # TODO 4：验证默认 k
    assert fake_collection.last_k == 3