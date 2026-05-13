from __future__ import annotations

from pathlib import Path

from .agents import (
    AggregatorAgent,
    EditorAgent,
    FactCheckerAgent,
    StudentAgent,
    TeacherAgent,
    derive_memory_updates,
)
from .config import Settings, load_settings
from .llm import make_llm
from .memory import MemoryStore
from .models import (
    Artifact,
    GenerationRequest,
    GenerationResult,
    IterationState,
)
from .storage import create_run_paths, write_json, write_text


class GenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.memory = MemoryStore(self.settings.data_dir)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        settings = self._settings_for_request(request)
        llm = make_llm(settings)
        teacher = TeacherAgent(llm)
        student = StudentAgent(llm)
        aggregator = AggregatorAgent(llm)
        fact_checker = FactCheckerAgent(llm)
        editor = EditorAgent(llm)

        paths = create_run_paths(settings.data_dir)
        write_json(paths.run_dir / "input.json", request)
        memory_context = self._memory_context(request.user_id, request.topic)

        iterations: list[IterationState] = []
        aggregate = None
        draft = None
        last_feedback = None
        max_iterations = request.max_iterations or settings.max_iterations

        for iteration in range(1, max_iterations + 1):
            draft = await teacher.draft(
                topic=request.topic,
                audience=request.audience,
                style=request.style,
                memory_context=memory_context,
                source_text=request.source_text,
                feedback=aggregate,
            )
            draft_path = paths.drafts_dir / f"iter-{iteration}-teacher.md"
            write_text(draft_path, render_article(draft.title, draft.synopsis, draft.content))

            feedback = await student.evaluate(
                draft=draft,
                topic=request.topic,
                audience=request.audience,
                memory_context=memory_context,
            )
            last_feedback = feedback
            feedback_path = paths.feedback_dir / f"iter-{iteration}-student.json"
            write_json(feedback_path, feedback)

            aggregate = await aggregator.aggregate([feedback])
            aggregate_path = paths.feedback_dir / f"iter-{iteration}-aggregate.json"
            write_json(aggregate_path, aggregate)

            high_impact = len([issue for issue in aggregate.must_fix if issue.impact >= 7])
            iterations.append(
                IterationState(
                    iteration=iteration,
                    draft_path=str(draft_path),
                    feedback_path=str(feedback_path),
                    aggregate_path=str(aggregate_path),
                    clarity_score=feedback.comprehension_score,
                    high_impact_issue_count=high_impact,
                )
            )
            if feedback.comprehension_score >= settings.clarity_threshold and high_impact == 0:
                break

        assert draft is not None
        fact_check = await fact_checker.check(draft, request.topic)
        if fact_check.blocking_issues:
            draft = await teacher.draft(
                topic=request.topic,
                audience=request.audience,
                style=request.style,
                memory_context=memory_context,
                source_text=request.source_text,
                feedback=aggregate,
            )
        final_article = await editor.edit(draft, fact_check)
        final_path = paths.final_dir / "article.md"
        write_text(
            final_path,
            render_article(
                final_article.title,
                final_article.synopsis,
                final_article.content,
            ),
        )

        memory_updates = []
        if last_feedback:
            updates = derive_memory_updates(
                user_id=request.user_id,
                topic=request.topic,
                run_id=paths.run_id,
                feedback=last_feedback,
            )
            memory_updates = self.memory.apply_updates(request.user_id, updates)

        artifact = Artifact(
            modality="text",
            title=final_article.title,
            path=str(final_path),
            mime_type="text/markdown",
            metadata={"topic": request.topic, "audience": request.audience},
        )
        result = GenerationResult(
            run_id=paths.run_id,
            user_id=request.user_id,
            topic=request.topic,
            audience=request.audience,
            final_article=final_article,
            artifacts=[artifact],
            iterations=iterations,
            fact_check=fact_check,
            memory_updates=memory_updates,
            run_dir=str(paths.run_dir),
        )
        write_json(paths.run_dir / "state.json", result)
        write_text(paths.run_dir / "report.md", render_report(result))
        return result

    def _settings_for_request(self, request: GenerationRequest) -> Settings:
        if not request.llm_backend:
            return self.settings
        return load_settings(
            data_dir=self.settings.data_dir,
            llm_backend=request.llm_backend,
            max_iterations=request.max_iterations or self.settings.max_iterations,
        )

    def _memory_context(self, user_id: str, topic: str) -> str:
        results = self.memory.search(user_id, topic, limit=6)
        if not results:
            return ""
        return "\n".join(
            f"- {item.title}: {item.summary} (tags={', '.join(item.tags)}, confidence={item.confidence})"
            for item in results
        )


def render_article(title: str, synopsis: str, content: str) -> str:
    return f"# {title}\n\n> {synopsis}\n\n{content}\n"


def render_report(result: GenerationResult) -> str:
    lines = [
        f"# Run {result.run_id}",
        "",
        f"- Topic: {result.topic}",
        f"- Audience: {result.audience}",
        f"- Iterations: {len(result.iterations)}",
        f"- Final article: {result.artifacts[0].path}",
        "",
        "## Iterations",
    ]
    for item in result.iterations:
        lines.append(
            f"- Iteration {item.iteration}: clarity={item.clarity_score}, "
            f"high_impact={item.high_impact_issue_count}, draft={item.draft_path}"
        )
    lines.extend(
        [
            "",
            "## Fact Check",
            result.fact_check.summary,
            "",
            "## Memory Updates",
        ]
    )
    lines.extend(f"- {item}" for item in result.memory_updates)
    return "\n".join(lines) + "\n"
