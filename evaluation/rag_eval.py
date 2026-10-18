import llm_service
from rag.service import retrieve
from pydantic import BaseModel, Field
from pydantic import ValidationError
from exceptions import (
    AIServiceError,
    AIServiceTimeoutError,
    AIServiceConnectionError
)

class JudgeResult(BaseModel):
    faithfulness: int = Field(ge=0, le=2)
    correctness: int = Field(ge=0, le=2)
    relevancy: int = Field(ge=0, le=2)

def evaluate_retrieval(retrieved_ids, relevant_ids):
    retrieved_set = set(retrieved_ids)
    relevant_set = set(relevant_ids)

    correct = len(retrieved_set & relevant_set)

    # 表示集合不为空时才执行除法。
    precision = correct / len(retrieved_set) if retrieved_set else 0.0
    recall = correct / len(relevant_set) if relevant_set else 0.0

    return {
        "precision": precision,
        "recall": recall
    }

def evaluate_hit(retrieved_ids, relevant_ids):
    retrieved_set = set(retrieved_ids)
    relevant_set = set(relevant_ids)

    # 你来补充
    hit = int(bool(retrieved_set & relevant_set))

    return hit

def evaluate_dataset(dataset, k=3, threshold=0.5):
    precisions = []
    recalls = []
    hits = []

    for item in dataset:
        question = item["question"]
        relevant_ids = item["relevant_ids"]

        results = retrieve(
            question,
            k=k,
            threshold=threshold
        )

        # TODO 1：提取检索结果中的所有文档 ID
        retrieved_ids = [item["id"] for item in results]

        # TODO 2：计算 Precision 和 Recall
        metrics = evaluate_retrieval(retrieved_ids, relevant_ids)

        # TODO 3：计算 Hit
        hit = evaluate_hit(retrieved_ids, relevant_ids)

        precisions.append(metrics["precision"])
        recalls.append(metrics["recall"])
        hits.append(hit)

    # TODO 4：计算三个指标的平均值
    return {
        "precision": sum(precisions) / len(precisions) if precisions else 0.0,
        "recall": sum(recalls) / len(recalls) if recalls else 0.0,
        "hit_rate": sum(hits) / len(hits) if hits else 0.0
    }


def build_judge_messages(question, context, answer, reference):
    system_prompt = """
你是一名严格的 RAG 评估员。

请根据以下标准评分，每项为 0、1、2 分：

Faithfulness：
0 = 回答明显违背资料
1 = 回答部分得到资料支持
2 = 回答完全得到资料支持

Correctness：
0 = 与参考答案明显不符
1 = 部分正确
2 = 与参考答案一致

Relevancy：
0 = 没有回答用户问题
1 = 部分回答
2 = 切题且完整

只输出 JSON，不要输出 Markdown 或额外解释。
格式：
{
    "faithfulness": 0,
    "correctness": 0,
    "relevancy": 0
}
"""

    user_prompt = f"""
问题：
{question}

检索资料：
{context}

模型回答：
{answer}

参考答案：
{reference}
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def judge_answer(question, context, answer, reference):
    messages = build_judge_messages(
        question,
        context,
        answer,
        reference
    )

    response = llm_service.ask_question(messages)

    result = JudgeResult.model_validate_json(response)

    return result

def evaluate_generation(dataset):
    #失败次数
    failed_count = 0
    #具体哪些题目失败及原因
    failures = []

    faithfulness_scores = []
    correctness_scores = []
    relevancy_scores = []

    for index, item in enumerate(dataset):
        try:
            result = judge_answer(
                question=item["question"],
                context=item["context"],
                answer=item["answer"],
                reference=item["reference"]
            )

        except (ValidationError, AIServiceError) as e:
            failed_count += 1

            failures.append({
                "index": index,
                "question": item["question"],
                "error": str(e)
            })

            continue

        faithfulness_scores.append(result.faithfulness)
        correctness_scores.append(result.correctness)
        relevancy_scores.append(result.relevancy)
    # TODO 2：计算三项平均分
    return {
        "faithfulness": sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0,
        "correctness": sum(correctness_scores) / len(correctness_scores) if correctness_scores else 0.0,
        "relevancy":sum(relevancy_scores) / len(relevancy_scores) if relevancy_scores else 0.0,
        "total": len(dataset),
        "success_count": len(faithfulness_scores),
        "failed_count": failed_count,
        "failures": failures
    }
if __name__ == "__main__":
    dataset = [
        {
            "question": "FastAPI 如何实现依赖注入？",
            "relevant_ids": ["study_notes_0"]
        },
        {
            "question": "SQLite 如何启用外键？",
            "relevant_ids": ["study_notes_1"]
        },
        {
            "question": "Git merge 有什么作用？",
            "relevant_ids": ["study_notes_2"]
        }
    ]

    thresholds = [0.3, 0.5, 0.7, 0.9]

    for threshold in thresholds:
        metrics = evaluate_dataset(
            dataset,
            k=3,
            threshold=threshold
        )

        print(f"threshold={threshold}: {metrics}")