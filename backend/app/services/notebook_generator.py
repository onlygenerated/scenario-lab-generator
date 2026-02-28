"""
Generate lab files dynamically from a blueprint.

The notebook has:
  1. Setup section (markdown + connection code + quick tests)
  2. One code cell per transformation step from the blueprint
"""

from __future__ import annotations

import json

from ..models.blueprint import ScenarioBlueprint


def generate_instructions_md(blueprint: ScenarioBlueprint) -> str:
    """Generate the student-facing INSTRUCTIONS.md from structured blueprint data.

    This ensures the Jupyter instructions match the frontend transformation steps
    exactly — both use the same blueprint fields as their single source of truth.
    """
    lines: list[str] = []

    # Title & description
    lines.append(f"# {blueprint.title}")
    lines.append("")
    lines.append(blueprint.description)
    lines.append("")

    # Business context (the story)
    lines.append("## Scenario")
    lines.append("")
    lines.append(blueprint.business_context)
    lines.append("")

    # Learning objectives
    lines.append("## Learning Objectives")
    lines.append("")
    for obj in blueprint.learning_objectives:
        lines.append(f"- {obj}")
    lines.append("")

    # Database connections
    lines.append("## Database Connections")
    lines.append("")
    lines.append("| Database | Host | Port | Database | User | Password |")
    lines.append("|----------|------|------|----------|------|----------|")
    lines.append("| Source | `source-db` | `5432` | `source_db` | `labuser` | `labpass` |")
    lines.append("| Target | `target-db` | `5432` | `target_db` | `labuser` | `labpass` |")
    lines.append("")

    # Source table schemas
    lines.append("## Source Tables")
    lines.append("")
    for table in blueprint.source_tables:
        lines.append(f"### `{table.table_name}`")
        lines.append("")
        lines.append(table.description)
        lines.append("")
        lines.append("| Column | Type | Description |")
        lines.append("|--------|------|-------------|")
        for col in table.columns:
            pk = " (PK)" if col.is_primary_key else ""
            lines.append(f"| `{col.name}` | {col.data_type.value}{pk} | {col.description} |")
        lines.append("")

    # Target table schemas
    lines.append("## Target Tables")
    lines.append("")
    for table in blueprint.target_tables:
        lines.append(f"### `{table.table_name}`")
        lines.append("")
        lines.append(table.description)
        lines.append("")
        lines.append("| Column | Type | Description |")
        lines.append("|--------|------|-------------|")
        for col in table.columns:
            lines.append(f"| `{col.name}` | {col.data_type.value} | {col.description} |")
        lines.append("")

    # Transformation steps
    lines.append("## Steps")
    lines.append("")
    for step in blueprint.transformation_steps:
        lines.append(f"### Step {step.step_number}: {step.title}")
        lines.append("")
        lines.append(step.description)
        if step.hint:
            lines.append("")
            lines.append(f"> **Hint:** {step.hint}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"**Difficulty:** {blueprint.difficulty.value.capitalize()} | "
                 f"**Estimated time:** {blueprint.estimated_minutes} minutes")
    lines.append("")
    lines.append("Use the **2_getting_started.ipynb** notebook to begin. "
                 "Click **Check My Work** in the app when you're done!")
    lines.append("")

    return "\n".join(lines)


def generate_notebook(blueprint: ScenarioBlueprint) -> str:
    """Generate a Jupyter notebook JSON string from a blueprint."""
    cells: list[dict] = []

    # --- Setup section (single compact block) ---
    cells.append(_markdown_cell(
        "# Getting Started\n"
        "\n"
        "Run the cell below to connect to your databases, then scroll down to **Your Work Starts Here**.\n"
        "See **1_INSTRUCTIONS.md** for the full scenario, table schemas, and business rules."
    ))

    cells.append(_code_cell(
        "import pandas as pd\n"
        "from sqlalchemy import create_engine, text\n"
        "\n"
        "source_engine = create_engine('postgresql://labuser:labpass@source-db:5432/source_db')\n"
        "target_engine = create_engine('postgresql://labuser:labpass@target-db:5432/target_db')\n"
        "\n"
        "q = \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\"\n"
        "print('Source tables:', pd.read_sql_query(q, source_engine)['table_name'].tolist())\n"
        "print('Target tables:', pd.read_sql_query(q, target_engine)['table_name'].tolist())\n"
        "print('Ready!')"
    ))

    # --- Work section ---
    cells.append(_markdown_cell(
        "## Your Work Starts Here\n"
        "\n"
        f"Complete the {len(blueprint.transformation_steps)} steps below. "
        "Each step has instructions above an empty code cell for your work."
    ))

    # One markdown + code cell pair per transformation step
    for step in blueprint.transformation_steps:
        md_lines = [f"### Step {step.step_number}: {step.title}"]
        md_lines.append("")
        md_lines.append(step.description)
        cells.append(_markdown_cell("\n".join(md_lines)))

        code_lines = []
        if step.hint:
            code_lines.append(f"# Hint: {step.hint}")
        code_lines.append("# Type your answer below")
        code_lines.append("")
        cells.append(_code_cell("\n".join(code_lines)))

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
        "from sqlalchemy import create_engine, text\n"
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


def generate_incorrect_notebook(
    blueprint: ScenarioBlueprint,
    escalation_level: int = 0,
) -> str:
    """
    Generate a notebook with deliberate plausible mistakes for testing the feedback loop.

    Same structure as generate_solution_notebook but with one mistake per step,
    chosen based on skill_tags.

    escalation_level controls mutation strength:
      0 — Semantic mutations (pedagogically ideal but data-dependent)
      1 — Row-affecting mutations (guaranteed to change row counts)
    """
    cells: list[dict] = []

    # --- Header ---
    cells.append(_markdown_cell(
        "# Incorrect Solution Notebook\n"
        "\n"
        "**For testing the feedback loop** — this notebook contains deliberate mistakes.\n"
        "\n"
        "Run all cells, then click **Check My Work** to see validation failures and AI feedback."
    ))

    # --- Same setup section ---
    cells.append(_code_cell(
        "import pandas as pd\n"
        "from sqlalchemy import create_engine, text\n"
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

    # --- Incorrect work section ---
    cells.append(_markdown_cell(
        "## Steps (with deliberate mistakes)\n"
        "\n"
        "Each cell below has a plausible but incorrect implementation."
    ))

    step_cells: list[dict] = []
    for step in blueprint.transformation_steps:
        step_cells.append(_markdown_cell(
            f"### Step {step.step_number}: {step.title}\n"
            f"\n"
            f"{step.description}"
        ))

        code = _inject_mistake(step, escalation_level)
        step_cells.append(_code_cell(code))

    cells.extend(step_cells)

    # Verification cell
    target_name = blueprint.target_tables[0].table_name if blueprint.target_tables else "result"
    cells.append(_markdown_cell("### Verify Results"))
    cells.append(_code_cell(
        f"# Check what we loaded\n"
        f"result = pd.read_sql_table('{target_name}', target_engine)\n"
        f"print(f'Loaded {{len(result)}} rows into {target_name}')\n"
        f"result"
    ))

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


def _classify_step(step: "TransformationStep") -> str:
    """
    Classify a step into a canonical category based on skill_tags, title, and code.

    AI-generated skill_tags vary widely (JOIN, INNER_JOIN, DATA_JOINING, etc.)
    so we normalize by checking for substring matches.
    """
    # Combine all signals into one searchable string
    tags_lower = " ".join(step.skill_tags).lower()
    title_lower = step.title.lower()
    code_lower = step.solution_code.lower()
    combined = f"{tags_lower} {title_lower}"

    # Data modeling: DDL steps (CREATE TABLE) — check code first for precision
    if "create table" in code_lower:
        return "DDL"

    # Data modeling: data migration steps (read source + write to learner-created tables)
    if any(kw in combined for kw in (
        "normaliz", "migrat", "populat", "primary_key", "foreign_key",
        "star_schema", "surrogate", "constraint", "scd",
    )):
        if ".to_sql(" in code_lower or "insert into" in code_lower:
            return "DATA_MIGRATION"
        # If it has CREATE TABLE in the code, it's DDL even with modeling tags
        return "DDL" if "create table" in code_lower else "DATA_MIGRATION"

    if any(kw in combined for kw in ("join", "merge", "merg")):
        return "JOIN"
    if any(kw in combined for kw in ("filter", "clean", "drop", "remove", "exclude")):
        return "FILTERING"
    if any(kw in combined for kw in ("aggregat", "groupby", "group_by", "group by", "agg")):
        return "AGGREGATION"
    if any(kw in combined for kw in ("load", "write", "insert", "target")):
        # Confirm by checking for to_sql in the code
        if "to_sql" in code_lower:
            return "LOADING"
    if any(kw in combined for kw in ("extract", "read", "source", "ingest")):
        return "EXTRACTION"
    if any(kw in combined for kw in ("transform", "calculat", "comput", "date", "column")):
        return "TRANSFORMATION"

    # Fall back to code-level detection
    if "create table" in code_lower:
        return "DDL"
    if "pd.merge(" in code_lower or ".merge(" in code_lower:
        return "JOIN"
    if ".to_sql(" in code_lower:
        return "LOADING"
    if ".groupby(" in code_lower:
        return "AGGREGATION"
    if ".dropna(" in code_lower or ".fillna(" in code_lower:
        return "FILTERING"

    return "OTHER"


def _inject_mistake(step: "TransformationStep", escalation_level: int = 0) -> str:
    """
    Take a transformation step and return code with a deliberate plausible mistake.

    Uses _classify_step to robustly match the step category regardless of
    how the AI named the skill_tags, then applies code-level mutations.

    escalation_level 0: semantic mutations (pedagogically ideal, data-dependent)
    escalation_level >= 1: row-affecting mutations (guaranteed to change row counts)
    """
    code = step.solution_code.strip()

    if not code:
        return f"# {step.title}\n# (no solution_code available for this step)"

    category = _classify_step(step)

    if escalation_level >= 1:
        return _inject_row_affecting_mistake(code, category)

    # --- Level 0: semantic mutations (current behavior) ---

    # DDL: remove a constraint from CREATE TABLE (FK, NOT NULL, CHECK, UNIQUE)
    if category == "DDL":
        import re
        # Try removing a FOREIGN KEY clause (most impactful for schema validation)
        modified = re.sub(
            r',?\s*FOREIGN\s+KEY\s*\([^)]*\)\s*REFERENCES\s+\w+\s*\([^)]*\)',
            '',
            code,
            count=1,
            flags=re.IGNORECASE,
        )
        if modified != code:
            return modified
        # Try removing a CHECK constraint
        modified = re.sub(
            r',?\s*CHECK\s*\([^)]*\)',
            '',
            code,
            count=1,
            flags=re.IGNORECASE,
        )
        if modified != code:
            return modified
        # Try removing NOT NULL from a non-PK column (skip lines with PRIMARY KEY)
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "NOT NULL" in line.upper() and "PRIMARY" not in line.upper():
                lines[i] = re.sub(r'\s+NOT\s+NULL', '', line, flags=re.IGNORECASE)
                return "\n".join(lines)
        # Try removing UNIQUE constraint
        modified = re.sub(
            r',?\s*UNIQUE\s*\([^)]*\)',
            '',
            code,
            count=1,
            flags=re.IGNORECASE,
        )
        if modified != code:
            return modified
        return code

    # DATA_MIGRATION: load only a subset of rows
    if category == "DATA_MIGRATION":
        import re
        # Add .head(1) before .to_sql() — loads only 1 row
        modified = re.sub(
            r'(\w+)(\.to_sql\()',
            r'\1.head(1)\2',
            code,
            count=1,
        )
        if modified != code:
            return modified
        return code

    # JOIN: change inner→left OR inner→outer, with regex fallback
    if category == "JOIN":
        import re
        # Try exact string patterns first
        for old, new in [
            ("how='inner'", "how='left'"),
            ('how="inner"', 'how="left"'),
        ]:
            if old in code:
                return code.replace(old, new)
        # Regex fallback for any quoting style
        modified = re.sub(r"how\s*=\s*['\"]inner['\"]", "how='left'", code)
        if modified != code:
            return modified
        # If merge/join is present but no how= parameter (defaults to inner),
        # add how='left' explicitly
        if "pd.merge(" in code or ".merge(" in code:
            modified = re.sub(r"(\.merge\([^)]*)\)", r"\1, how='left')", code, count=1)
            if modified != code:
                return modified
            modified = re.sub(r"(pd\.merge\([^)]*)\)", r"\1, how='left')", code, count=1)
            if modified != code:
                return modified
        return code

    # FILTERING: skip the filter step entirely
    if category == "FILTERING":
        # Find the output variable name from the code (e.g., "active = ..." or "filtered = ...")
        import re
        var_match = re.match(r"(\w+)\s*=", code)
        var_name = var_match.group(1) if var_match else "filtered"
        # Find the input DataFrame referenced in the code
        input_match = re.search(r"=\s*(\w+)\[", code)
        input_name = input_match.group(1) if input_match else "df"
        return (
            f"# Skipping filter — assuming all data is relevant\n"
            f"{var_name} = {input_name}.copy()\n"
            f"print(f'Rows (no filter applied): {{len({var_name})}}')"
        )

    # AGGREGATION: swap a sum→count or remove a groupby column
    if category == "AGGREGATION":
        import re
        # Try replacing 'sum' with 'count' (various quoting)
        for old, new in [("'sum'", "'count'"), ('"sum"', '"count"')]:
            modified = code.replace(old, new, 1)
            if modified != code:
                return modified
        # Try removing one column from groupby list to change the granularity
        gb_match = re.search(r"\.groupby\(\[([^\]]+)\]\)", code)
        if gb_match:
            cols_str = gb_match.group(1)
            cols = [c.strip() for c in cols_str.split(",")]
            if len(cols) >= 2:
                # Remove the first groupby column
                new_cols = ", ".join(cols[1:])
                return code.replace(gb_match.group(0), f".groupby([{new_cols}])")
        return code

    # LOADING: replace→append, which causes duplicates on re-run
    if category == "LOADING":
        import re
        for old, new in [
            ("if_exists='replace'", "if_exists='append'"),
            ('if_exists="replace"', 'if_exists="append"'),
        ]:
            if old in code:
                return code.replace(old, new)
        # Regex fallback
        modified = re.sub(
            r"if_exists\s*=\s*['\"]replace['\"]",
            "if_exists='append'",
            code,
        )
        if modified != code:
            return modified
        return code

    # TRANSFORMATION: drop a computed column assignment
    if category == "TRANSFORMATION":
        # Remove the first line that creates a new column (df['x'] = ...)
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "['" in line and "=" in line and line.index("=") > line.index("['"):
                lines[i] = f"# SKIPPED: {line.strip()}"
                return "\n".join(lines)
        return code

    # EXTRACTION / CONNECTION / OTHER: return correct code
    # (these steps don't meaningfully affect validation outcomes)
    return code


def _inject_row_affecting_mistake(code: str, category: str) -> str:
    """
    Level 1 mutations — guaranteed to change row counts.

    These are less pedagogically ideal but ensure the incorrect notebook
    actually fails validation.
    """
    import re

    # DDL: skip creating the table entirely — information_schema checks will fail
    if category == "DDL":
        return (
            "# Skipping table creation for now\n"
            "print('TODO: create table')"
        )

    # DATA_MIGRATION: load only 1 row
    if category == "DATA_MIGRATION":
        modified = re.sub(
            r'(\w+)(\.to_sql\()',
            r'\1.head(1)\2',
            code,
            count=1,
        )
        if modified != code:
            return modified
        # Fallback: comment out the entire migration
        return (
            "# Skipping data migration for now\n"
            "print('TODO: migrate data')"
        )

    # LOADING: .head(1) before .to_sql() — loads only 1 row
    if category == "LOADING":
        modified = re.sub(
            r"(\w+)(\.to_sql\()",
            r"\1.head(1)\2",
            code,
            count=1,
        )
        if modified != code:
            return modified

    # AGGREGATION: remove a groupby column to change number of groups
    if category == "AGGREGATION":
        gb_match = re.search(r"\.groupby\(\[([^\]]+)\]\)", code)
        if gb_match:
            cols_str = gb_match.group(1)
            cols = [c.strip() for c in cols_str.split(",")]
            if len(cols) >= 2:
                new_cols = ", ".join(cols[1:])
                return code.replace(gb_match.group(0), f".groupby([{new_cols}])")
        # Fallback: .head(1) after aggregation
        modified = re.sub(
            r"(\.reset_index\(\))",
            r"\1.head(1)",
            code,
            count=1,
        )
        if modified != code:
            return modified

    # FILTERING: df.head(1) instead of the real filter
    if category == "FILTERING":
        var_match = re.match(r"(\w+)\s*=", code)
        var_name = var_match.group(1) if var_match else "filtered"
        input_match = re.search(r"=\s*(\w+)\[", code)
        input_name = input_match.group(1) if input_match else "df"
        return (
            f"# Aggressive filter — keeping only first row\n"
            f"{var_name} = {input_name}.head(1).copy()\n"
            f"print(f'After filtering: {{len({var_name})}} rows')"
        )

    # JOIN: .head(2) before merge — shrinks result
    if category == "JOIN":
        # Find the first DataFrame argument and add .head(2)
        modified = re.sub(
            r"(pd\.merge\()(\w+)",
            r"\1\2.head(2)",
            code,
            count=1,
        )
        if modified != code:
            return modified
        modified = re.sub(
            r"(\w+)(\.merge\()",
            r"\1.head(2)\2",
            code,
            count=1,
        )
        if modified != code:
            return modified

    # Default safety net: .head(1) before the last .to_sql() call
    if ".to_sql(" in code:
        modified = re.sub(
            r"(\w+)(\.to_sql\()",
            r"\1.head(1)\2",
            code,
            count=1,
        )
        if modified != code:
            return modified

    # Ultimate fallback: return original code (no mutation possible)
    return code


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
