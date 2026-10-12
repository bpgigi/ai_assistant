import chromadb
import llm_service
from pathlib import Path

from dns import query
from sentence_transformers import SentenceTransformer


client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(
    name = "rag_study_notes",
    configuration={"hnsw":{"space":"cosine"}}
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    local_files_only=True
)

#读取Markdown文件
def load_markdown(file_path):
    return Path(file_path).read_text(encoding="utf-8")

#检索相关Chunk
def retrieve(query, k=3, max_distance=0.5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "distances", "metadatas"]
    )

    docs = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    retrieved = []

    for doc, distance, metadata in zip(docs, distances, metadatas):
        if distance <= max_distance:
            retrieved.append({
                "text": doc,
                "source": metadata.get("source", "unknown"),
                "distance": distance
            })

    return retrieved

#将资料与问题合成Prompt
def build_prompt(query, docs):
    context = "\n\n".join(
        f"[{i}] 来源：{doc['source']}\n内容：{doc['text']}"
        for i, doc in enumerate(docs, start=1)
    )

    return f"""
请仅根据参考资料回答问题。

规则：
1. 不要编造资料中不存在的信息。
2. 如果资料不足，请明确说明。
3. 回答时引用对应资料编号，例如 [1]。

参考资料：
{context}

用户问题：
{query}
"""

#串联检索、生成和来源展示
def rag_answer(query):
    docs = retrieve(query, k=3)

    if not docs:
        return {
            "answer": "知识库中没有找到相关资料",
            "sources": []
        }

    prompt = build_prompt(query, docs)

    messages = [
        {
            "role": "system",
            "content": "你是一个知识库问答助手。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    answer = llm_service.ask_question(messages)

#去重
    sources = list(set(
        doc["source"] for doc in docs
    ))

    return {
        "answer": answer,
        "sources": sources
    }

#文档分块
def split_text(text, chunk_size=5, chunk_overlap=2):
    if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Invalid chunk parameters")

    chunks = []
    step = chunk_size - chunk_overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks

#md生成Embedding并存入ChromaDB
def index_documents(file_path):
    text = load_markdown(file_path)

    chunks = split_markdown(text)

    if not chunks:
        return 0

    embeddings = model.encode(chunks).tolist()

    name = Path(file_path).stem

    ids = [
        f"{name}_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {"source": file_path, "chunk_index": i}
        for i in range(len(chunks))
    ]

    # 删除该文件的旧 Chunk
    collection.delete(
        where={"source": file_path}
    )

    # 写入新 Chunk
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)

#把一份 Markdown 学习笔记按照一级标题 #  分成多个 Chunk。
def split_markdown(text):
    sections = text.split("\n#")
    chunks = []

    for i, section in enumerate(sections):
        if i > 0:
            section = "#" + section

        section = section.strip()
        if section:
            chunks.append(section)

    return chunks


if __name__ == "__main__":
    query = "FastAPI 的 Depends 底层源码是如何实现依赖解析的？"

    docs = retrieve(
        query,
        k=3,
        max_distance=0.5
    )

    print("检索结果:", docs)

    result = rag_answer(query)

    print("AI 回答:", result["answer"])
    print("参考来源:", result["sources"])