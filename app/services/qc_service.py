from app.models.qc import QcReport

def run_qc_stub(source_content: dict, translated_content: dict) -> QcReport:
    """
    Temporary QC stub. Replace with real LLM call later.
    """
    return QcReport(
        passed=True,
        score=95,
        issues=[],
        model="stub",
    )
