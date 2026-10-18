import llm_service
from evaluation.rag_eval import judge_answer
import pytest
from pydantic import ValidationError
from exceptions import AIServiceTimeoutError


def test_judge_answer(monkeypatch):

    def fake_llm(messages):
        return '{"faithfulness": 2, "correctness": 1, "relevancy": 2}'

    # TODO：用 monkeypatch 替换真实的 LLM 函数
    monkeypatch.setattr(llm_service, "ask_question", fake_llm)

    result = judge_answer(
        question="SQLite 如何启用外键？",
        context="SQLite 使用 PRAGMA foreign_keys = ON 启用外键。",
        answer="使用 PRAGMA foreign_keys = ON。",
        reference="使用 PRAGMA foreign_keys = ON 启用外键。"
    )

    assert result.faithfulness == 2
    assert result.correctness == 1
    assert result.relevancy == 2


def test_judge_answer_invalid_score(monkeypatch):

    def fake_llm(messages):
        return '{"faithfulness": 3, "correctness": 1, "relevancy": 2}'

    monkeypatch.setattr(llm_service, "ask_question", fake_llm)

    with pytest.raises(ValidationError):
        judge_answer(
            question="SQLite 如何启用外键？",
            context="SQLite 使用 PRAGMA foreign_keys = ON。",
            answer="执行 PRAGMA foreign_keys = ON。",
            reference="使用 PRAGMA foreign_keys = ON。"
        )

import evaluation.rag_eval as rag_eval

def test_evaluate_generation(monkeypatch):
    scores = iter([
        rag_eval.JudgeResult(
            faithfulness=2,
            correctness=1,
            relevancy=2
        ),
        rag_eval.JudgeResult(
            faithfulness=0,
            correctness=2,
            relevancy=1
        )
    ])

    def fake_judge_answer(question, context, answer, reference):
        return next(scores)

    monkeypatch.setattr(
        rag_eval,
        "judge_answer",
        fake_judge_answer
    )

    dataset = [
        {
            "question": "SQLite 如何启用外键？",
            "context": "SQLite 使用 PRAGMA foreign_keys = ON。",
            "answer": "执行 PRAGMA foreign_keys = ON。",
            "reference": "使用 PRAGMA foreign_keys = ON。"
        },
        {
            "question": "FastAPI Depends 有什么作用？",
            "context": "FastAPI 使用 Depends 实现依赖注入。",
            "answer": "Depends 用于依赖注入。",
            "reference": "Depends 实现依赖注入。"
        }
    ]

    result = rag_eval.evaluate_generation(dataset)

    # TODO：你来写三个断言
    assert result["faithfulness"] == 1
    assert result["correctness"] == 1.5
    assert result["relevancy"] == 1.5

def test_evaluate_generation_empty(monkeypatch):
    def fake_judge_answer(*args, **kwargs):
        raise AssertionError("空数据集不应该调用 LLM")

    monkeypatch.setattr(rag_eval, "judge_answer", fake_judge_answer)

    result = rag_eval.evaluate_generation([])

    assert result == {
        "faithfulness": 0.0,
        "correctness": 0.0,
        "relevancy": 0.0,
        "total": 0,
        "success_count": 0,
        "failed_count": 0,
        "failures": []
    }

def test_evaluate_generation_partial_failure(monkeypatch):
    scores = iter([
        rag_eval.JudgeResult(
            faithfulness=2,
            correctness=1,
            relevancy=2
        ),
        "invalid",
        rag_eval.JudgeResult(
            faithfulness=1,
            correctness=2,
            relevancy=1
        )
    ])

    def fake_judge_answer(question, context, answer, reference):
        result = next(scores)

        if result == "invalid":
            return rag_eval.JudgeResult(
                faithfulness=3,
                correctness=1,
                relevancy=2
            )

        return result

    monkeypatch.setattr(
        rag_eval,
        "judge_answer",
        fake_judge_answer
    )

    dataset = [
        {
            "question": f"question_{i}",
            "context": "context",
            "answer": "answer",
            "reference": "reference"
        }
        for i in range(3)
    ]

    result = rag_eval.evaluate_generation(dataset)

    # TODO：你来写断言
    assert result["total"] == 3
    assert result["success_count"] == 2
    assert result["failed_count"] == 1

    assert result["faithfulness"] == 1.5
    assert result["correctness"] == 1.5
    assert result["relevancy"] == 1.5

    assert len(result["failures"]) == 1
    assert result["failures"][0]["index"] == 1

def test_evaluate_generation_timeout(monkeypatch):
    call_count = 0

    def fake_judge_answer(question, context, answer, reference):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            raise AIServiceTimeoutError("LLM 请求超时")

        return rag_eval.JudgeResult(
            faithfulness=2,
            correctness=1,
            relevancy=2
        )

    monkeypatch.setattr(
        rag_eval,
        "judge_answer",
        fake_judge_answer
    )

    dataset = [
        {
            "question": f"question_{i}",
            "context": "context",
            "answer": "answer",
            "reference": "reference"
        }
        for i in range(2)
    ]

    result = rag_eval.evaluate_generation(dataset)

    # TODO：你来写断言
    assert call_count == 2

    assert result["total"] == 2
    assert result["success_count"] == 1
    assert result["failed_count"] == 1

    assert result["faithfulness"] == 2
    assert result["correctness"] == 1
    assert result["relevancy"] == 2

    assert len(result["failures"]) == 1
    assert result["failures"][0]["index"] == 0