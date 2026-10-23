import chromadb
import llm_service
import hashlib
from sentence_transformers import SentenceTransformer
from pathlib import Path
from config import settings

_model = None

collection = None
def get_collection():
    global collection

    if collection is None:
        client = chromadb.PersistentClient(
            path="./chroma_data"
        )

        collection = client.get_or_create_collection(
            name="rag_study_notes",
            configuration={"hnsw": {"space": "cosine"}}
        )

    return collection

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
    collection = get_collection()

    if not chunks:
        collection.delete(
            where={"source": source}
        )
        return 0

    model = get_model()

    file_id = hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()[:16]
    ids = [f"{file_id}_{i}" for i in range(len(chunks))]

    embeddings = model.encode(chunks).tolist()
    metadatas = [
        {"source": source}
        for _ in chunks
    ]

    collection.delete(
        where={"source": source}
    )

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(chunks)


def retrieve(query, k=None, threshold=None):
    collection = get_collection()
    if k is None:
        k = settings.rag_top_k

    if threshold is None:
        threshold = settings.rag_threshold

    if k < 1:
        raise ValueError("k must be >= 1")
    if threshold < 0 or threshold > 2:
        raise ValueError("threshold must be between 0 and 2")

    # 下面保留原有检索逻辑
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

#先把传来的相对路径改为绝对路径，再把改路径下的所有md切块存入embedding返回切了几个md文件
def index_directory(folder_path, project_root=None):
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    project_root = Path(project_root).resolve()
    folder = (project_root / folder_path).resolve()

    if not folder.is_relative_to(project_root):
        raise ValueError("知识库目录必须位于项目根目录内")

    total = 0

    for file in sorted(folder.rglob("*.md")):
        text = load_markdown(file)
        chunks = split_markdown(text)

        source = file.resolve().relative_to(project_root).as_posix()

        count = index_documents(chunks, source)
        total += count

    return total


def list_documents():
    collection = get_collection()
    data = collection.get(include=["metadatas"])

    counts: dict[str, int] = {}

    for metadata in data["metadatas"]:
        source = (metadata or {}).get("source", "unknown")

        if not isinstance(source, str):
            source = "unknown"

        counts[source] = counts.get(source, 0) + 1

    documents = []

    for source, count in counts.items():
        documents.append({
            "source": source,
            "chunk_count": count
        })

    return documents


def delete_document(source):
    collection = get_collection()

    # ① 获取指定 source 对应的记录
    data = collection.get(
        where= {"source": source},
        include=[]
    )

    # ② 统计记录数量
    count = len(data["ids"])

    # ③ 如果没有记录，直接返回 0
    if not count:
        return 0

    # ④ 删除指定 source 的记录
    collection.delete(where={"source": source})

    # ⑤ 返回删除数量
    return count
if __name__ == "__main__":
    print(list_documents())