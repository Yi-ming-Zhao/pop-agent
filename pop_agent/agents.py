from __future__ import annotations

from .llm import LLMClient, parse_json_object
from .memory import MemoryUpdate
from .models import (
    AggregatedFeedback,
    ArticleDraft,
    FactCheckReport,
    FeedbackIssue,
    StudentFeedback,
)


class TeacherAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def draft(
        self,
        *,
        topic: str,
        audience: str,
        style: str,
        memory_context: str,
        source_text: str | None,
        feedback: AggregatedFeedback | None = None,
    ) -> ArticleDraft:
        feedback_text = feedback.model_dump_json(ensure_ascii=False) if feedback else "无"
        text = await self.llm.complete(
            system="TASK:teacher\n你是科普教师 Agent。只输出 JSON: title, synopsis, content。",
            user=(
                f"主题: {topic}\n目标读者: {audience}\n风格: {style}\n"
                f"用户记忆:\n{memory_context or '无'}\n"
                f"参考材料:\n{source_text or '无'}\n"
                f"待修复反馈:\n{feedback_text}\n"
                "请生成或修订一篇准确、易懂、有层次的文字科普。"
            ),
        )
        data = parse_json_object(
            text,
            {
                "title": topic,
                "synopsis": f"面向{audience}解释{topic}",
                "content": fallback_article(topic, audience),
            },
        )
        return ArticleDraft(**data)


class StudentAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def evaluate(
        self,
        *,
        draft: ArticleDraft,
        topic: str,
        audience: str,
        memory_context: str,
    ) -> StudentFeedback:
        text = await self.llm.complete(
            system=(
                "TASK:student\n你是学生 Agent。根据目标读者和用户记忆评估文章。"
                "只输出 JSON: comprehension_score, interest_score, restatement, "
                "confusion_points, recommendation。"
            ),
            user=(
                f"主题: {topic}\n目标读者: {audience}\n用户记忆:\n{memory_context or '无'}\n"
                f"文章标题: {draft.title}\n文章:\n{draft.content}\n"
                "请列出 impact 1-10 的困惑点。"
            ),
        )
        data = parse_json_object(text, heuristic_student_feedback(draft, topic))
        return StudentFeedback(**data)


class AggregatorAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def aggregate(self, feedbacks: list[StudentFeedback]) -> AggregatedFeedback:
        text = await self.llm.complete(
            system=(
                "TASK:aggregator\n你是反馈聚合 Agent。只输出 JSON: "
                "common_issues, must_fix, nice_to_have, summary。"
            ),
            user="\n".join(item.model_dump_json(ensure_ascii=False) for item in feedbacks),
        )
        fallback = aggregate_feedbacks(feedbacks).model_dump(mode="json")
        data = parse_json_object(text, fallback)
        return AggregatedFeedback(**data)


class FactCheckerAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def check(self, draft: ArticleDraft, topic: str) -> FactCheckReport:
        text = await self.llm.complete(
            system=(
                "TASK:fact_checker\n你是事实检查 Agent。只输出 JSON: "
                "blocking_issues, warnings, summary。"
            ),
            user=f"主题: {topic}\n文章:\n{draft.content}\n检查过度简化、明显事实风险和未限定类比。",
        )
        data = parse_json_object(
            text,
            {"blocking_issues": [], "warnings": [], "summary": "未发现阻断问题。"},
        )
        return FactCheckReport(**data)


class EditorAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def edit(self, draft: ArticleDraft, fact_check: FactCheckReport) -> ArticleDraft:
        text = await self.llm.complete(
            system="TASK:editor\n你是最终编辑 Agent。只输出 JSON: title, synopsis, content。",
            user=(
                f"事实检查:\n{fact_check.model_dump_json(ensure_ascii=False)}\n"
                f"文章:\n{draft.model_dump_json(ensure_ascii=False)}\n"
                "在不改变事实含义的前提下润色结构和表达。"
            ),
        )
        data = parse_json_object(text, draft.model_dump(mode="json"))
        return ArticleDraft(**data)


def fallback_article(topic: str, audience: str) -> str:
    return (
        f"这篇文章要向{audience}解释“{topic}”。我们会先从熟悉的现象开始，"
        "再一步步引出新概念。每遇到一个术语，都先给出简短定义，"
        "最后用一个例子说明它为什么重要。"
    )


def heuristic_student_feedback(draft: ArticleDraft, topic: str) -> dict:
    issues: list[dict] = []
    content = draft.content
    if len(content) < 120:
        issues.append(
            {
                "issue": "解释过短，缺少铺垫和例子",
                "impact": 8,
                "evidence": "正文长度不足，读者难以建立完整理解路径。",
                "suggestion": "增加一个生活例子和术语解释。",
            }
        )
    technical_markers = ["机制", "量子", "转录", "算法", "代谢", "事件视界"]
    if any(marker in content for marker in technical_markers) and "比如" not in content:
        issues.append(
            {
                "issue": "抽象概念缺少类比",
                "impact": 7,
                "evidence": "文章出现技术词，但没有用类比或例子降低理解门槛。",
                "suggestion": "加入一个熟悉场景类比，并说明类比边界。",
            }
        )
    score = 8 if not issues else 6
    return {
        "comprehension_score": score,
        "interest_score": 7,
        "restatement": f"我理解这篇文章是在解释{topic}的基本意思。",
        "confusion_points": issues,
        "recommendation": "stop" if score >= 8 else "continue",
    }


def aggregate_feedbacks(feedbacks: list[StudentFeedback]) -> AggregatedFeedback:
    all_issues = [issue for feedback in feedbacks for issue in feedback.confusion_points]
    must_fix = [issue for issue in all_issues if issue.impact >= 7]
    nice = [issue for issue in all_issues if issue.impact < 7]
    return AggregatedFeedback(
        common_issues=all_issues,
        must_fix=must_fix,
        nice_to_have=nice,
        summary=f"共发现 {len(all_issues)} 个问题，其中 {len(must_fix)} 个需要优先修复。",
    )


def derive_memory_updates(
    *,
    user_id: str,
    topic: str,
    run_id: str,
    feedback: StudentFeedback,
) -> list[MemoryUpdate]:
    updates = [
        MemoryUpdate(
            section="knowledge",
            title=f"关于 {topic} 的理解水平",
            summary=(
                f"最近一次生成中，用户画像对应学生 Agent 的理解评分为 "
                f"{feedback.comprehension_score}/10。复述：{feedback.restatement}"
            ),
            tags=[topic, "comprehension", user_id],
            confidence=0.7,
            source_run=run_id,
        )
    ]
    for issue in feedback.confusion_points:
        if issue.impact >= 7:
            updates.append(
                MemoryUpdate(
                    section="misconceptions",
                    title=f"{topic} 的高影响困惑",
                    summary=f"{issue.issue}。证据：{issue.evidence}。建议：{issue.suggestion}",
                    tags=[topic, "confusion", "impact-high"],
                    confidence=0.75,
                    source_run=run_id,
                )
            )
    return updates
