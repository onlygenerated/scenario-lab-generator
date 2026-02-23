"""
Generate the getting_started.ipynb notebook dynamically from a blueprint.

The notebook has:
  1. Setup section (markdown + connection code + quick tests)
  2. One code cell per transformation step from the blueprint
"""

from __future__ import annotations

import json

from ..models.blueprint import ScenarioBlueprint


def generate_notebook(blueprint: ScenarioBlueprint) -> str:
    """Generate a Jupyter notebook JSON string from a blueprint."""
    cells: list[dict] = []

    # --- Setup section ---
    cells.append(_markdown_cell(
        "# Getting Started\n"
        "\n"
        "This notebook is pre-configured with connections to your lab databases.\n"
        "\n"
        "## Database Connections\n"
        "\n"
        "| Database | Host | Port | Database | User | Password |\n"
        "|----------|------|------|----------|------|----------|\n"
        "| Source | `source-db` | `5432` | `source_db` | `labuser` | `labpass` |\n"
        "| Target | `target-db` | `5432` | `target_db` | `labuser` | `labpass` |"
    ))

    cells.append(_code_cell(
        "import pandas as pd\n"
        "from sqlalchemy import create_engine\n"
        "\n"
        "# Connection strings\n"
        "source_engine = create_engine('postgresql://labuser:labpass@source-db:5432/source_db')\n"
        "target_engine = create_engine('postgresql://labuser:labpass@target-db:5432/target_db')\n"
        "\n"
        "print('Engines created successfully!')"
    ))

    cells.append(_code_cell(
        "# Quick test: list tables in source database\n"
        "source_tables = pd.read_sql_query(\n"
        "    \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\",\n"
        "    source_engine\n"
        ")\n"
        "print('Source tables:')\n"
        "source_tables"
    ))

    cells.append(_code_cell(
        "# Quick test: list tables in target database\n"
        "target_tables = pd.read_sql_query(\n"
        "    \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\",\n"
        "    target_engine\n"
        ")\n"
        "print('Target tables:')\n"
        "target_tables"
    ))

    # --- Work section ---
    cells.append(_markdown_cell(
        "## Your Work Starts Here\n"
        "\n"
        "Read the **INSTRUCTIONS.md** tab for the full scenario and business rules.\n"
        "\n"
        f"Complete the {len(blueprint.transformation_steps)} steps below. "
        "Each cell has a comment describing what to do and a hint to help you."
    ))

    # One cell per transformation step
    for step in blueprint.transformation_steps:
        lines = [f"# Step {step.step_number}: {step.title}"]
        lines.append(f"# {step.description}")
        if step.hint:
            lines.append(f"#")
            lines.append(f"# Hint: {step.hint}")
        lines.append("")

        cells.append(_code_cell("\n".join(lines)))

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    return json.dumps(notebook, indent=1, ensure_ascii=False)


def generate_solution_notebook(blueprint: ScenarioBlueprint) -> str:
    """Generate a solution notebook with pre-filled working code for each step."""
    cells: list[dict] = []

    # --- Header ---
    cells.append(_markdown_cell(
        "# Solution Notebook\n"
        "\n"
        "**For testing only** — this notebook contains the complete solution.\n"
        "\n"
        "Run all cells to populate the target database, then use **Check My Work** to validate."
    ))

    # --- Same setup section as getting_started ---
    cells.append(_code_cell(
        "import pandas as pd\n"
        "from sqlalchemy import create_engine\n"
        "\n"
        "# Connection strings\n"
        "source_engine = create_engine('postgresql://labuser:labpass@source-db:5432/source_db')\n"
        "target_engine = create_engine('postgresql://labuser:labpass@target-db:5432/target_db')\n"
        "\n"
        "print('Engines created successfully!')"
    ))

    cells.append(_code_cell(
        "# Quick test: list tables in source database\n"
        "source_tables = pd.read_sql_query(\n"
        "    \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\",\n"
        "    source_engine\n"
        ")\n"
        "print('Source tables:')\n"
        "source_tables"
    ))

    # --- Solution work section ---
    cells.append(_markdown_cell(
        "## Solution Steps\n"
        "\n"
        "Each cell below contains working code for the corresponding transformation step."
    ))

    # Build solution code from blueprint hints
    solution_cells = _build_solution_cells(blueprint)
    cells.extend(solution_cells)

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    return json.dumps(notebook, indent=1, ensure_ascii=False)


def _build_solution_cells(blueprint: ScenarioBlueprint) -> list[dict]:
    """
    Build solution code cells from blueprint transformation steps.

    Uses skill_tags to identify what each step does, then generates working
    Python code based on the blueprint's table/column metadata and hints.
    """
    cells: list[dict] = []
    source_names = [t.table_name for t in blueprint.source_tables]
    target_name = blueprint.target_tables[0].table_name if blueprint.target_tables else "result"

    # Track the "current dataframe" variable name through the pipeline
    df_var = "df"

    for step in blueprint.transformation_steps:
        tags = set(step.skill_tags)

        cells.append(_markdown_cell(
            f"### Step {step.step_number}: {step.title}\n"
            f"\n"
            f"{step.description}"
        ))

        # Prefer explicit solution_code when available; fall back to heuristic
        if step.solution_code.strip():
            code = step.solution_code.strip()
        else:
            code = _generate_step_code(step, tags, source_names, target_name, blueprint, df_var)

        # Update df_var based on what the step produces
        if "EXTRACTION" in tags:
            df_var = source_names[0] if source_names else "df"
        elif "JOIN" in tags:
            df_var = "merged"
        elif "FILTERING" in tags or "CLEANING" in tags:
            df_var = "active"
        elif "AGGREGATION" in tags or "GROUPBY" in tags:
            df_var = "summary"

        cells.append(_code_cell(code))

    # Verification cell
    cells.append(_markdown_cell("### Verify Results"))
    cells.append(_code_cell(
        f"# Check what we loaded\n"
        f"result = pd.read_sql_table('{target_name}', target_engine)\n"
        f"print(f'Loaded {{len(result)}} rows into {target_name}')\n"
        f"result"
    ))

    return cells


def _generate_step_code(
    step: object,
    tags: set[str],
    source_names: list[str],
    target_name: str,
    blueprint: ScenarioBlueprint,
    current_df: str,
) -> str:
    """Generate working Python code for a single transformation step."""

    # CONNECTION steps — already handled by setup cells
    if "DATABASE_CONNECTION" in tags:
        return (
            "# Already done in setup cells above\n"
            "print(f'Source engine: {source_engine}')\n"
            "print(f'Target engine: {target_engine}')"
        )

    # EXTRACTION steps — read each source table
    if "EXTRACTION" in tags:
        lines = []
        for name in source_names:
            lines.append(f"{name} = pd.read_sql_table('{name}', source_engine)")
            lines.append(f"print(f'{name}: {{len({name})}} rows')")
        lines.append("")
        lines.append(f"{source_names[0]}.head()" if source_names else "")
        return "\n".join(lines)

    # JOIN steps — merge source tables
    if "JOIN" in tags:
        # Find the join key from the hint or infer from foreign keys
        join_key = _extract_join_key(step.hint, blueprint)
        if len(source_names) >= 2:
            return (
                f"merged = pd.merge({source_names[0]}, {source_names[1]}, "
                f"on='{join_key}', how='inner')\n"
                f"print(f'Merged: {{len(merged)}} rows')\n"
                f"merged.head()"
            )
        return f"# JOIN: {step.hint}"

    # FILTERING / CLEANING steps
    if "FILTERING" in tags or "CLEANING" in tags:
        # Extract filter condition from hint
        filter_col, filter_val = _extract_filter(step.hint, blueprint)
        return (
            f"active = {current_df}[{current_df}['{filter_col}'] == {filter_val}].copy()\n"
            f"print(f'After filtering: {{len(active)}} rows')"
        )

    # TRANSFORMATION / DATE_HANDLING steps
    if "TRANSFORMATION" in tags or "DATE_HANDLING" in tags:
        return _generate_transform_code(step, current_df, blueprint)

    # AGGREGATION / GROUPBY steps
    if "AGGREGATION" in tags or "GROUPBY" in tags:
        return _generate_aggregation_code(step, current_df, blueprint)

    # LOADING steps — write to target (use 'replace' in solution for idempotency)
    if "LOADING" in tags:
        return (
            f"# Using 'replace' so re-running this notebook won't create duplicates\n"
            f"{current_df}.to_sql('{target_name}', target_engine, "
            f"if_exists='replace', index=False)\n"
            f"print(f'Loaded {{len({current_df})}} rows into {target_name}')"
        )

    # Fallback: use hint as comment
    return (
        f"# {step.title}\n"
        f"# Hint: {step.hint}\n"
        f"\n"
        f"# TODO: implement this step"
    )


def _extract_join_key(hint: str, blueprint: ScenarioBlueprint) -> str:
    """Extract the join key from a hint, or infer from table schemas."""
    if not hint:
        return "id"
    # Look for on='xxx' pattern in hint
    if "on='" in hint:
        start = hint.index("on='") + 4
        end = hint.index("'", start)
        return hint[start:end]
    # Infer: find column names that appear in multiple source tables
    if len(blueprint.source_tables) >= 2:
        cols_0 = {c.name for c in blueprint.source_tables[0].columns}
        cols_1 = {c.name for c in blueprint.source_tables[1].columns}
        shared = cols_0 & cols_1
        # Prefer columns with _id suffix
        id_cols = [c for c in shared if c.endswith("_id")]
        if id_cols:
            return id_cols[0]
        if shared:
            return next(iter(shared))
    return "id"


def _extract_filter(hint: str, blueprint: ScenarioBlueprint) -> tuple[str, str]:
    """Extract filter column and value from a hint."""
    if not hint:
        return "is_active", "True"
    # Look for df['xxx'] == yyy pattern
    if "'" in hint and "==" in hint:
        # e.g. "df['is_active'] == True"
        parts = hint.split("==")
        if len(parts) == 2:
            col_part = parts[0].strip()
            val_part = parts[1].strip().rstrip("]).copy( ")
            # Extract column name from ['col'] or ["col"]
            for q in ["'", '"']:
                if f"[{q}" in col_part and f"{q}]" in col_part:
                    start = col_part.index(f"[{q}") + 2
                    end = col_part.index(f"{q}]")
                    return col_part[start:end], val_part
    return "is_active", "True"


def _generate_transform_code(
    step: object,
    current_df: str,
    blueprint: ScenarioBlueprint,
) -> str:
    """Generate transformation code from hint (computed columns, date extraction)."""
    hint = step.hint or ""
    lines = []

    # Parse semicolon-separated statements from the hint
    statements = [s.strip() for s in hint.split(";") if s.strip()]

    for stmt in statements:
        # Clean up prefixes
        for prefix in ["Use ", "use "]:
            if stmt.startswith(prefix):
                stmt = stmt[len(prefix):]

        # Replace generic "df" with the actual variable name
        stmt = stmt.replace("df['", f"{current_df}['")
        stmt = stmt.replace("df[\"", f"{current_df}[\"")
        lines.append(stmt)

    if lines:
        lines.append(f"print(f'Transformed: {{len({current_df})}} rows')")
        return "\n".join(lines)

    return f"# {step.title}\n# Hint: {hint}"


def _generate_aggregation_code(
    step: object,
    current_df: str,
    blueprint: ScenarioBlueprint,
) -> str:
    """Generate aggregation code from target table schema."""
    target = blueprint.target_tables[0] if blueprint.target_tables else None
    if not target:
        return f"# {step.title}\n# Hint: {step.hint}"

    # Identify group-by columns vs aggregate columns from the target schema
    target_cols = {c.name: c for c in target.columns}

    # Group-by columns: those that appear in source tables or are date/category-like
    # Aggregate columns: those with SUM/COUNT descriptions
    group_cols = []
    agg_map: dict[str, tuple[str, str]] = {}  # target_col -> (source_col, agg_func)

    for col in target.columns:
        desc_lower = col.description.lower()
        if "sum" in desc_lower and "quantity" in desc_lower and "price" not in desc_lower:
            agg_map[col.name] = ("quantity", "sum")
        elif "sum" in desc_lower:
            agg_map[col.name] = ("line_revenue", "sum")
        elif "count" in desc_lower:
            agg_map[col.name] = ("transaction_id", "count")
        else:
            group_cols.append(col.name)

    if not group_cols or not agg_map:
        # Fallback to hint
        return f"# {step.title}\n# Hint: {step.hint}"

    group_str = ", ".join(f"'{c}'" for c in group_cols)
    agg_items = []
    renames = []
    for target_col, (src_col, func) in agg_map.items():
        agg_items.append(f"    {target_col}=('{src_col}', '{func}'),")
        if target_col != src_col:
            renames.append(f"# {src_col} -> {target_col} via {func}")

    agg_body = "\n".join(agg_items)

    return (
        f"summary = {current_df}.groupby([{group_str}]).agg(\n"
        f"{agg_body}\n"
        f").reset_index()\n"
        f"print(f'Aggregated: {{len(summary)}} rows')\n"
        f"summary.head()"
    )


def _markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def _code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }
