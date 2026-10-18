import chromadb
import llm_service
from sentence_transformers import SentenceTransformer
from pathlib import Path

_model = None

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(
    name="rag_study_notes",
    configuration={"hnsw":{"space":"cosine"}}
)

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            local_files_only=True
        )
    return _model

def load_markdown(file_path):
    return Path(file_path).read_text(encoding="utf-8")

def split_markdown(text):
    chunks = []
    current_chunk = []

    for line in text.splitlines():

        if line.startswith(("# ","## ","### ")):
            if current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
            current_chunk.append(line)
            continue

        current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks

def index_documents(chunks,source):
    collection.delete(
        where={"source": source}
    )

    if not chunks:
        return 0

    model = get_model()
    ids = [f"{Path(source).stem}_{i}" for i in range(len(chunks))]
    embeddings = model.encode(chunks).tolist()
    metadatas = [
        {"source": source}
        for _ in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(chunks)

def retrieve(query, k=3, threshold=0.5):
    if collection.count() == 0:
        return []

    model = get_model()
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
        include=["documents","distances","metadatas"]
    )

    ids = results["ids"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]


    retrieved = []

    for doc_id,document,distance,metadata in zip(ids,documents,distances,metadatas):
        if distance <= threshold:
            item = {
                "id": doc_id,
                "text": document,
                "distance": distance,
                "source": (metadata or {}).get("source", "unknown")
            }
            retrieved.append(item)

    return retrieved

def build_rag_context(results):
    return "\n\n".join(item["text"] for item in results)

def rag_answer(question):
    results = retrieve(question, k=3, threshold=0.5)

    if not results:
        return "知识库中没有找到相关内容"

    # 1. 从 results 提取文本，拼接为 context
    context = "\n\n".join(item["text"] for item in results)

    # 2. 构造 messages
    # system: 要求只能根据 context 回答
    # user: 提供 context 和 question
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个知识库问答助手。"
                "只能根据提供的参考资料回答问题。"
                "如果资料不足以回答，就说：知识库中没有足够的信息。"
                "不要编造答案。"
                )
        },
        {
            "role": "user",
            "content": f"参考资料：\n{context}\n\n问题：{question}"
        }
    ]

    # 3. 调用 llm_service.ask_question(messages)
    # 4. 返回回答
    return llm_service.ask_question(messages)

def rewrite_query(question,history):
    if not history:
        return question
    messages = [
                   {
                       "role": "system",
                       "content": (
                           "你是一个查询改写助手。"
                           "根据对话历史，将用户当前问题改写为一个独立、完整、适合知识库检索的问题。"
                           "保持原意，不要回答问题，不要编造信息。"
                           "只输出改写后的问题。"
                       )
                   }
               ] + history + [
                   {
                       "role": "user",
                       "content": question
                   }
               ]
    rewritten_question = llm_service.ask_question(messages)
    return rewritten_question

if __name__ == "__main__":
    text = load_markdown("study_notes.md")
    chunks = split_markdown(text)

    count = index_documents(chunks, "study_notes.md")
    print("索引数量：", count)

    results = retrieve("FastAPI Depends 是什么？")
    print(results)