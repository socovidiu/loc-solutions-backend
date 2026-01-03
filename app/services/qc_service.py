from __future__ import annotations

from dataclasses import dataclass

from app.models.qc import QcReport


@dataclass
class QCService:
    """Quality checks for localized content.

    Clean seam to swap in:
    - deterministic checks (placeholders/tags/numbers)
    - LLM evaluation
    - prompt/versioning and logging
    """

    model_name: str = "stub"

    def run(self, *, source_content: dict, translated_content: dict) -> QcReport:
        return self._run_stub(source_content=source_content, translated_content=translated_content)

    def _run_stub(self, *, source_content: dict, translated_content: dict) -> QcReport:
        return QcReport(
            passed=True,
            score=95,
            issues=[],
            model=self.model_name,
        )


def run_qc_stub(source_content: dict, translated_content: dict) -> QcReport:
    return QCService().run(source_content=source_content, translated_content=translated_content)
