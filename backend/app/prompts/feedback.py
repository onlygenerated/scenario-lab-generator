"""
Prompt templates for AI-generated feedback on failed validation checks.

Uses tool-based structured output (same pattern as generator.py) to return
per-check diagnosis and suggestions without revealing solution code.
"""

from __future__ import annotations

from ..models.blueprint import ScenarioBlueprint
from ..models.lab import ValidationResult

FEEDBACK_SYSTEM_PROMPT = """You are a supportive data engineering tutor reviewing a student's ETL pipeline work.

The student attempted a hands-on lab exercise and some validation checks failed. Your job is to
diagnose what went wrong and suggest how to fix it — without giving away the exact solution code.

Rules:
- Keep each diagnosis to 2-3 sentences. Be specific: reference actual table names, column names,
  and data characteristics from the scenario.
- Keep each suggestion to 2-3 sentences. Point the student in the right direction without writing
  code for them. For example, say "check which join type you used" not "use how='inner'".
- Use a direct, encouraging tone appropriate for capable adults learning new skills.
- Do not use emojis.
- Do not repeat the error message verbatim — add insight beyond what the student already sees.
- If the error indicates a missing table, focus on whether the student completed the loading step.
- If row counts are wrong, think about what transformations could produce too many or too few rows.
"""

FEEDBACK_TOOL_SCHEMA = {
    "name": "provide_feedback",
    "description": "Provide diagnostic feedback for each failed validation check",
    "input_schema": {
        "type": "object",
        "properties": {
            "feedback_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "query_name": {
                            "type": "string",
                            "description": "The name of the failed validation check (must match exactly)",
                        },
                        "diagnosis": {
                            "type": "string",
                            "description": "What went wrong (2-3 sentences, specific to the scenario)",
                        },
                        "suggestion": {
                            "type": "string",
                            "description": "How to fix it without giving exact code (2-3 sentences)",
                        },
                    },
                    "required": ["query_name", "diagnosis", "suggestion"],
                },
            },
        },
        "required": ["feedback_items"],
    },
}


def build_feedback_prompt(
    failed_results: list[ValidationResult],
    student_code: str,
    blueprint: ScenarioBlueprint,
) -> str:
    """Assemble the user message for the feedback Claude call."""
    lines: list[str] = []

    # Failed checks
    lines.append("## Failed Validation Checks\n")
    for r in failed_results:
        lines.append(f"- **{r.query_name}**")
        if r.error:
            lines.append(f"  Error: {r.error}")
        if r.actual_row_count is not None:
            lines.append(f"  Expected {r.expected_row_count} rows, got {r.actual_row_count}")
        lines.append("")

    # Student code
    lines.append("## Student's Notebook Code\n")
    lines.append("```python")
    lines.append(student_code)
    lines.append("```\n")

    # Transformation steps (descriptions only — NOT solution_code)
    lines.append("## Transformation Steps\n")
    for step in blueprint.transformation_steps:
        lines.append(f"### Step {step.step_number}: {step.title}")
        lines.append(step.description)
        if step.skill_tags:
            lines.append(f"Skills: {', '.join(step.skill_tags)}")
        lines.append("")

    # Table schemas (columns and types only, no sample data)
    lines.append("## Source Table Schemas\n")
    for table in blueprint.source_tables:
        lines.append(f"### {table.table_name}")
        for col in table.columns:
            lines.append(f"- {col.name} ({col.data_type.value}): {col.description}")
        lines.append("")

    lines.append("## Target Table Schemas\n")
    for table in blueprint.target_tables:
        lines.append(f"### {table.table_name}")
        for col in table.columns:
            lines.append(f"- {col.name} ({col.data_type.value}): {col.description}")
        lines.append("")

    lines.append(
        "Provide feedback for each failed check. Diagnose what likely went wrong "
        "based on the student's code and the expected transformations, then suggest "
        "how to fix it without revealing the exact solution."
    )

    return "\n".join(lines)
