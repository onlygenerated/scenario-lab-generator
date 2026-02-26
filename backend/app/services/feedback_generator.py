"""
AI feedback generator for failed validation checks.

Reads the student's notebook, diagnoses mistakes, and returns short per-check
feedback via Claude API tool-based structured output.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import anthropic
import httpx

from ..config import settings
from ..models.lab import FeedbackItem, LabSession, ValidationResult
from ..prompts.feedback import (
    FEEDBACK_SYSTEM_PROMPT,
    FEEDBACK_TOOL_SCHEMA,
    build_feedback_prompt,
)

logger = logging.getLogger(__name__)

# Max chars of student code to include in prompt (keeps costs ~$0.01/call)
_MAX_CODE_CHARS = 4000


def _extract_student_code(lab_dir: str) -> str:
    """
    Read the student's notebook from the host filesystem and extract code cells.

    Checks getting_started.ipynb first. If its work cells are empty stubs
    (no pipeline code like .to_sql or .merge), falls back to
    4_incorrect_solution.ipynb — the student likely ran that notebook instead.
    """
    workspace = Path(lab_dir) / "workspace"

    # Try getting_started first (the primary student notebook)
    code = _read_notebook_code(workspace / "2_getting_started.ipynb")
    if code and _has_pipeline_code(code):
        return _truncate(code)

    # getting_started is empty/stubs — try incorrect_solution
    alt_code = _read_notebook_code(workspace / "4_incorrect_solution.ipynb")
    if alt_code and _has_pipeline_code(alt_code):
        logger.debug("Using 4_incorrect_solution.ipynb for feedback (getting_started is empty)")
        return _truncate(alt_code)

    # Fall back to whatever we got (even if it's stubs)
    return _truncate(code or "# (notebook not found)")


def _read_notebook_code(notebook_path: Path) -> str | None:
    """Read a .ipynb file and return concatenated code cells, or None."""
    if not notebook_path.exists():
        return None
    try:
        nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    code_parts: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = cell.get("source", [])
            if isinstance(source, list):
                code_parts.append("".join(source))
            elif isinstance(source, str):
                code_parts.append(source)

    return "\n\n".join(code_parts)


def _has_pipeline_code(code: str) -> bool:
    """Check if the code contains substantive ETL work (not just setup/stubs).

    Only counts markers on executable lines — ignores comments (which contain
    hints like ``# Hint: Use pd.merge(...)`` in the getting_started notebook).
    """
    markers = (".to_sql(", ".merge(", "pd.merge(", ".groupby(")
    for line in code.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if any(m in stripped for m in markers):
            return True
    return False


def _truncate(code: str) -> str:
    if len(code) > _MAX_CODE_CHARS:
        return code[:_MAX_CODE_CHARS] + "\n# ... (truncated)"
    return code


def _demo_feedback(failed_results: list[ValidationResult]) -> list[FeedbackItem]:
    """Return hardcoded feedback for demo mode (no AI call)."""
    demo_feedback: dict[str, tuple[str, str]] = {
        "Row count check": (
            "The target table has the wrong number of rows. This typically happens when "
            "the join type includes extra rows (e.g., a LEFT JOIN instead of INNER JOIN) "
            "or when discontinued products are not filtered out before aggregation.",
            "Double-check that you are using an INNER JOIN to combine transactions with "
            "products, and verify that you filter out rows where is_active is False before "
            "grouping. The expected result has 6 date-category combinations.",
        ),
        "Electronics Jan 15 revenue": (
            "The revenue calculation for Electronics on January 15 does not match. This "
            "could mean the line_revenue column is computed incorrectly or the date "
            "extraction is not truncating timestamps to dates properly.",
            "Make sure you compute line_revenue as quantity multiplied by unit_price "
            "before aggregating. Also confirm that you extract just the date portion "
            "from the transaction_date timestamp so that grouping works correctly.",
        ),
        "Discontinued products excluded": (
            "Discontinued products appear to be included in the output. The business rule "
            "requires filtering out products where is_active is False before any aggregation.",
            "After joining transactions with products, add a filtering step that keeps only "
            "rows where is_active is True. This should be done before the groupby operation.",
        ),
        "No NULL categories": (
            "There are rows with NULL category values in the target table. This usually "
            "happens when using a LEFT JOIN instead of an INNER JOIN — transactions without "
            "a matching product get NULL values for product columns.",
            "Switch to an INNER JOIN when merging transactions with products. An INNER JOIN "
            "automatically drops transactions that do not have a matching product_id, "
            "preventing NULL categories from entering the pipeline.",
        ),
    }

    items: list[FeedbackItem] = []
    for r in failed_results:
        if r.query_name in demo_feedback:
            diagnosis, suggestion = demo_feedback[r.query_name]
        else:
            diagnosis = (
                "This validation check did not produce the expected result. "
                "Review the corresponding transformation step in your notebook."
            )
            suggestion = (
                "Compare the expected row count with what your pipeline produces. "
                "Trace through each transformation step to find where rows are "
                "being added or lost."
            )
        items.append(FeedbackItem(
            query_name=r.query_name,
            diagnosis=diagnosis,
            suggestion=suggestion,
        ))
    return items


def generate_feedback(
    session: LabSession,
    failed_results: list[ValidationResult],
) -> list[FeedbackItem]:
    """
    Generate AI feedback for failed validation checks.

    Reads the student's notebook, builds a compact prompt, and calls Claude
    with tool-based structured output to get per-check feedback.
    """
    if settings.demo_mode:
        return _demo_feedback(failed_results)

    if not settings.anthropic_api_key:
        logger.warning("No API key configured — skipping feedback generation")
        return []

    if not session.lab_dir:
        logger.warning("No lab_dir on session — skipping feedback generation")
        return []

    student_code = _extract_student_code(session.lab_dir)

    prompt = build_feedback_prompt(
        failed_results=failed_results,
        student_code=student_code,
        blueprint=session.blueprint,
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2048,
            system=FEEDBACK_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            tools=[FEEDBACK_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "provide_feedback"},
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
    except Exception:
        logger.exception("Claude API call failed for feedback generation")
        return []

    # Parse tool response into FeedbackItem list
    for block in response.content:
        if block.type == "tool_use" and block.name == "provide_feedback":
            raw_items = block.input.get("feedback_items", [])
            items: list[FeedbackItem] = []
            for raw in raw_items:
                try:
                    items.append(FeedbackItem(
                        query_name=raw["query_name"],
                        diagnosis=raw["diagnosis"],
                        suggestion=raw["suggestion"],
                    ))
                except (KeyError, TypeError):
                    logger.warning("Skipping malformed feedback item: %s", raw)
            return items

    logger.warning("Claude did not return a tool use response for feedback")
    return []
