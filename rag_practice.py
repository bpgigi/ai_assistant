import json
import chromadb
import llm_service
from pathlib import Path
from pydantic import BaseModel,Field
from sentence_transformers import SentenceTransformer

class JudgeResult(BaseModel):
    faithfulness: int = Field(ge=0, le=2)
    correctness: int = Field(ge=0, le=2)
    relevancy: int = Field(ge=0, le=2)
    reason: str

def build_judge_prompt(question, context, expected, actual):
    return f"""
你是一名严格的 RAG 质量评估员。

请分别评估以下三个指标，每项 0～2 分。

1. faithfulness（忠实度）
检查实际回答中的每个事实性陈述是否有参考资料支持。
不能使用你自己的知识替回答补充依据。

2. correctness（正确性）
比较实际回答和预期答案的核心事实是否一致。
允许不同的语言表达方式。

3. relevancy（相关性）
检查实际回答是否直接回应用户问题。

评分标准：
0 = 不满足
1 = 部分满足
2 = 完全满足

如果某项无法充分判断，请保守评分，并在理由中说明。

用户问题：
{question}

参考资料：
{context}

预期答案：
{expected}

实际回答：
{actual}

只返回 JSON：
{{
    "faithfulness": 0,
    "correctness": 0,
    "relevancy": 0,
    "reason": "解释三个维度的评分依据"
}}
"""

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

    ids = results["ids"][0]
    docs = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    retrieved = []

    for id_,doc, distance, metadata in zip(ids,docs, distances, metadatas):
        if distance <= max_distance:
            retrieved.append({
                "id":id_,
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

    contexts = [doc["text"] for doc in docs]

    return {
        "answer": answer,
        "sources": sources,
        "contexts": contexts
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

#评估函数
def evaluate_retrieval(retrieved_ids, relevant_ids):
    retrieved = set(retrieved_ids)
    relevant = set(relevant_ids)

    correct = len(retrieved & relevant)

    precision = correct / len(retrieved) if retrieved else 0
    recall = correct / len(relevant) if relevant else 0

    return {
        "precision": precision,
        "recall": recall
    }

def evaluate_hit(retrieved_ids, relevant_ids):
    retrieved = set(retrieved_ids)
    relevant = set(relevant_ids)

    return int(bool(retrieved & relevant))

def evaluate_dataset(test_cases,max_distance=0.5):
    total_precision = 0
    total_recall = 0
    total_hit = 0

    for case in test_cases:
        docs = retrieve(
            case["query"],
            k=3,
            max_distance=max_distance
        )

        retrieved_ids = [
            doc["id"] for doc in docs
        ]

        scores = evaluate_retrieval(
            retrieved_ids,
            case["relevant_ids"]
        )

        hit = evaluate_hit(
            retrieved_ids,
            case["relevant_ids"]
        )

        total_precision += scores["precision"]
        total_recall += scores["recall"]
        total_hit += hit

    n = len(test_cases)

    print("平均 Precision:", total_precision / n)
    print("平均 Recall:", total_recall / n)
    print("Hit Rate:", total_hit / n)

def evaluate_generation(test_cases):
    total_faithfulness = 0
    total_correctness = 0
    total_relevancy = 0

    if not test_cases:
        return None

    for case in test_cases:
        # RAG 生成回答
        result = rag_answer(case["query"])

        # 获取参考资料
        context = "\n\n".join(result["contexts"])

        # Judge 评分
        judge_result = judge_answer(
            question=case["query"],
            context=context,
            expected=case["expected_answer"],
            actual=result["answer"]
        )

        # 分别累计三个指标
        total_faithfulness += judge_result.faithfulness
        total_correctness += judge_result.correctness
        total_relevancy += judge_result.relevancy

        print("问题:", case["query"])
        print("Faithfulness:", judge_result.faithfulness)
        print("Correctness:", judge_result.correctness)
        print("Relevancy:", judge_result.relevancy)
        print("评分理由:", judge_result.reason)
        print("-" * 40)

    n = len(test_cases)

    print("平均 Faithfulness:", total_faithfulness / n)
    print("平均 Correctness:", total_correctness / n)
    print("平均 Relevancy:", total_relevancy / n)

def judge_answer(question,context,expected,actual):
    prompt = build_judge_prompt(
        question,context,expected,actual
    )

    message = [
        {
            "role": "system",
            "content": "你是RAG评估员。只返回合法JSON，不要输出其他内容。"
        },
        {
            "role": "user",
            "content":prompt
        }
    ]

    response = llm_service.ask_question(message)
    data = json.loads(response)
    result = JudgeResult.model_validate(data)
    return result

if __name__ == "__main__":
    # test_cases = [
    #     {
    #         "query": "FastAPI 的 Depends 有什么作用？",
    #         "relevant_ids": ["study_notes_0"]
    #     },
    #     {
    #         "query": "SQLite 如何开启外键约束？",
    #         "relevant_ids": ["study_notes_1"]
    #     },
    #     {
    #         "query": "git fetch 有什么作用？",
    #         "relevant_ids": ["study_notes_2"]
    #     }
    # ]
    #
    generation_test_cases = [
        {
            "query": "FastAPI 的 Depends 有什么作用？",
            "expected_answer": "Depends 用于实现依赖注入，复用数据库依赖、权限验证等公共逻辑。"
        },
        {
            "query": "SQLite 如何开启外键约束？",
            "expected_answer": "执行 PRAGMA foreign_keys = ON。"
        },
        {
            "query": "git fetch 有什么作用？",
            "expected_answer": "获取远程仓库的更新，但不会自动合并到当前分支。"
        }
    ]

    evaluate_generation(generation_test_cases)

    