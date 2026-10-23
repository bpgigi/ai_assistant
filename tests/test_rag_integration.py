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

import numpy as np


class FakeModel:
    def encode(self, text):
        return np.array([0.1, 0.2, 0.3])


class FakeCollection:
    def __init__(self, count=1):
        self.last_k = None
        self.last_include = None
        self._count = count

    def count(self):
        return self._count

    # query() 保留你之前已经测试通过的实现
    def query(self, query_embeddings, n_results, include=None):
        self.last_k = n_results
        self.last_include = include

        return {
            "ids": [["doc_1"]],
            "documents": [["FastAPI 使用 Depends"]],
            "distances": [[0.6]],
            "metadatas": [[{"source": "test.md"}]]
        }

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
    assert fake_collection.last_k == 1

def test_retrieve_k_override(monkeypatch):
    fake_collection = FakeCollection(count=5)

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

    # 使用默认 k
    rag_service.retrieve("FastAPI")
    assert fake_collection.last_k == 3

    # 显式覆盖 k
    rag_service.retrieve("FastAPI", k=2)
    assert fake_collection.last_k == 2

    # 超过知识库文档数量
    rag_service.retrieve("FastAPI", k=10)

    # TODO：你来补充最后一个断言
    assert fake_collection.last_k == 5

def test_index_embedding_failure(monkeypatch):
    fake_collection = FakeCollection()
    fake_collection.delete_count = 0

    monkeypatch.setattr(
        rag_service, "collection", fake_collection
    )
    monkeypatch.setattr(
        rag_service, "get_model", lambda: FakeModel()
    )

    def fail_encode(self,chunks):
        raise RuntimeError("Embedding failed")

    monkeypatch.setattr(
        FakeModel,
        "encode",
        fail_encode
    )
    def fake_delete(where):
        fake_collection.delete_count += 1

    monkeypatch.setattr(
        fake_collection,
        "delete",
        fake_delete,
        raising=False
    )
    with pytest.raises(RuntimeError):
        rag_service.index_documents(
            ["FastAPI 使用 Depends 实现依赖注入"],
            "knowledge/fastapi.md"
        )

    assert fake_collection.delete_count == 0

class FakeIndexCollection:
    def __init__(self):
        self.saved_ids = []

    def delete(self, where):
        pass

    def upsert(self, ids, documents, embeddings, metadatas):
        self.saved_ids.append(ids.copy())
def test_index_ids_unique(monkeypatch):
    fake_collection = FakeIndexCollection()

    monkeypatch.setattr(
        rag_service, "collection", fake_collection
    )
    monkeypatch.setattr(
        rag_service, "get_model", lambda: FakeModel()
    )

    rag_service.index_documents(
        ["Python 基础"],
        "knowledge/python/notes.md"
    )

    rag_service.index_documents(
        ["FastAPI 基础"],
        "knowledge/fastapi/notes.md"
    )

    # ③ 断言两次 upsert 的 ID 不相同
    assert len(fake_collection.saved_ids) == 2
    assert fake_collection.saved_ids[0]!=fake_collection.saved_ids[1]

#=====================================相同来源重复索引时，ID 是否稳定。
    rag_service.index_documents(
        ["Python 基础更新版"],
        "knowledge/python/notes.md"
    )
    assert fake_collection.saved_ids[0] == fake_collection.saved_ids[2]

def test_tmp_path_example(tmp_path):
    folder = tmp_path / "knowledge"

    folder.mkdir()

    file = folder / "fastapi.md"

    file.write_text(
        "# FastAPI\nDepends 实现依赖注入",
        encoding="utf-8"
    )

    assert file.exists()

def test_index_directory(monkeypatch, tmp_path):
    folder = tmp_path / "knowledge"
    folder.mkdir()

    (folder / "fastapi.md").write_text(
        "# FastAPI\nDepends 实现依赖注入",
        encoding="utf-8"
    )

    (folder / "sqlite.md").write_text(
        "# SQLite\n使用 PRAGMA 启用外键",
        encoding="utf-8"
    )

    (folder / "git.md").write_text(
        "# Git\nmerge用于合并分支",
        encoding="utf-8"
    )

    saved_sources = []

    def fake_index(chunks,source):
        saved_sources.append(source)
        return len(chunks)

    monkeypatch.setattr(
        rag_service, "index_documents", fake_index
    )

    total = rag_service.index_directory(
        "knowledge",
        project_root = tmp_path
    )

    # ① 总共索引了 3 个 Chunk
    assert total == 3

    # ② 索引函数调用了 3 次
    assert len(saved_sources) == 3

    # ③ 三个文件的来源路径都正确
    assert set(saved_sources) == {
        "knowledge/fastapi.md",
        "knowledge/sqlite.md",
        "knowledge/git.md"
    }

def test_list_documents(monkeypatch):

    class FakeListCollection:
        def get(self, include):
            return {
                "metadatas": [
                    {"source": "fastapi.md"},
                    {"source": "fastapi.md"},
                    {"source": "git.md"},
                    None
                ]
            }

    fake_collection = FakeListCollection()

    monkeypatch.setattr(
        rag_service,
        "collection",
        fake_collection
    )

    documents = rag_service.list_documents()

    assert len(documents) == 3

    assert {"source": "fastapi.md", "chunk_count": 2} in documents
    assert {"source": "git.md", "chunk_count": 1} in documents
    assert {"source": "unknown", "chunk_count": 1} in documents

class FakeDeleteCollection:
    def __init__(self):
        self.deleted_source = None

    def get(self, where, include):
        return {
            "ids": ["chunk_0", "chunk_1"]
        }

    def delete(self, where):
        self.deleted_source = where["source"]
def test_delete_document(monkeypatch):
    fake_collection = FakeDeleteCollection()

    monkeypatch.setattr(
        rag_service,
        "collection",
        fake_collection
    )

    count = rag_service.delete_document(
        "knowledge/fastapi.md"
    )

    assert count == 2
    assert fake_collection.deleted_source == "knowledge/fastapi.md"