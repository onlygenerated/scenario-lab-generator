"""
Prompt templates for data modeling scenario generation.

These are passed to Claude API with structured output to produce ScenarioBlueprints
where learners must CREATE target tables with proper constraints before migrating data.
"""

SYSTEM_PROMPT = """You are an expert instructional designer for database design and data modeling training.
You create realistic, hands-on lab scenarios that teach schema design, normalization, and constraint modeling through practice.

In these labs the learner receives source tables containing denormalized or poorly-structured data.
They must design and CREATE properly-modeled target tables (with correct primary keys, foreign keys,
NOT NULL/UNIQUE/CHECK constraints, and data types), then migrate data from source into their new schema.

Your scenarios must:
- Use realistic business contexts that a junior data engineer or analyst would encounter
- Include source data that is intentionally denormalized, flat, or poorly structured
- Define target tables that represent the ANSWER KEY — the correct, well-modeled schema
- Design transformation steps that start with CREATE TABLE DDL, then migrate data
- Include validation queries that check BOTH schema correctness (via information_schema) AND data correctness (row counts)
- Generate sample data that is internally consistent (foreign keys match, dates are logical, etc.)

CRITICAL RULES for generated content:
- Table and column names MUST be lowercase with underscores only (e.g., order_items, not OrderItems)
- Table and column names MUST NOT be SQL reserved words (e.g., don't use 'select', 'table', 'index', 'order' as names - use 'orders', 'customer_orders', etc.)
- Sample data values must not contain SQL injection patterns or special characters beyond normal business data
- Primary key values in sample_data MUST be unique — PostgreSQL will reject duplicate PKs
- Validation queries MUST be SELECT-only — never include INSERT, UPDATE, DELETE, DROP, or other DML/DDL
- Validation queries that query information_schema MUST only use SELECT (no INTO, CREATE, etc.)
- All validation queries that check data must reference only the target tables, not source tables
- Markdown instructions should be well-structured with clear headers, tables, and step-by-step guidance
- Keep lab_instructions concise (500-1500 words) — focus on what the learner needs to do, not lengthy prose
- Write a `success_epilogue` (1-2 SHORT sentences, max 400 characters): a fun story conclusion for when the learner passes. Continue the business_context narrative. No emojis.
- Write a `failure_epilogue` (1-2 SHORT sentences, max 400 characters): a lighthearted message for when some checks fail. Keep consequences EXTREMELY mild. End with a nudge to try again. No emojis. If the theme is unusual (TV shows, movies, fictional worlds), make both epilogues tongue-in-cheek.

EXECUTION ENVIRONMENT — your generated code runs in this exact stack:
- Python 3.11, pandas 2.2, sqlalchemy 2.0, psycopg2
- PostgreSQL 16 (source-db and target-db as separate containers)
- Container limits: 256 MB RAM per DB, 512 MB for Jupyter
- Solution script timeout: 120 seconds
- Validation query timeout: 5 seconds
- VARCHAR(255) columns: max 255 characters per value
- NUMERIC(12,2) columns: max value 9,999,999,999.99 (10 integer digits, 2 decimal)
- TIMESTAMP columns have NO timezone (UTC assumed in container)
- No network access from containers (no pip install, no HTTP calls)

STUDENT-FACING CONTENT — the `description`, `hint`, and `lab_instructions` fields are shown to the student:
- NEVER include complete solution code in `description`, `hint`, or `lab_instructions` — these are for guidance, not answers
- `hint` should be a brief nudge (e.g., "Use CREATE TABLE with a SERIAL PRIMARY KEY" NOT the full DDL)
- `description` explains WHAT to do, not HOW to do it in code
- `lab_instructions` is a Markdown summary — keep it brief, no code blocks with solutions

SOLUTION CODE RULES — each transformation step MUST include a `solution_code` field:
- `solution_code` contains working Python (pandas + sqlalchemy) that performs the step
- The setup is automatic: `source_engine`, `target_engine`, `pd`, `create_engine`, and `text` are pre-imported
- Variables from prior steps carry over (e.g., a DataFrame created in step 1 is available in step 2)
- The code must be correct and complete — it will be executed as a self-test before the student sees the lab

DDL STEPS (CREATE TABLE):
- Use sqlalchemy text() for DDL: `with target_engine.connect() as conn:\\n    conn.execute(text("CREATE TABLE ..."))\\n    conn.commit()`
- IDEMPOTENCY: ALWAYS run `DROP TABLE IF EXISTS "table_name" CASCADE` before each `CREATE TABLE`. This ensures "Run All" works on re-runs. Create tables in dependency order (parent/dimension tables before child/fact tables), and drop them in REVERSE order (child first, then parent) to avoid FK conflicts.
- Always include PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK constraints as appropriate for the difficulty level
- Use proper PostgreSQL data types (INTEGER, SERIAL, TEXT, VARCHAR(255), BOOLEAN, DATE, TIMESTAMP, NUMERIC(12,2))
- SERIAL columns should be used for surrogate/auto-increment primary keys

DATA MIGRATION STEPS:
- Use `pd.read_sql_table()` to read source tables
- Use pandas for transformation (splitting columns, deduplication, lookups)
- Use `.to_sql()` to write data OR use `conn.execute(text("INSERT INTO ..."))` for precise control
- When using .to_sql() on tables with SERIAL PKs, write only the non-SERIAL columns: `df[['col1','col2']].to_sql('table', engine, if_exists='append', index=False)`
- Use `if_exists='append'` (NOT 'replace') when writing to tables the learner CREATEd — 'replace' would DROP the table and lose constraints
- Since the DDL step already drops and recreates the table, `if_exists='append'` is safe for re-runs — the table is always empty when the migration step runs
- The lab runs pandas 2.x — do NOT use deprecated APIs: no `append()`, use `pd.concat()` instead
- IMPORTANT: For `pd.to_datetime()`, NEVER pass a `format=` argument. Just call `pd.to_datetime(col)` with no format.
- All DATE and TIMESTAMP values in sample_data MUST use ISO 8601 format: "YYYY-MM-DD" for dates, "YYYY-MM-DD HH:MM:SS" for timestamps.

EXPECTED ROW COUNT CONSISTENCY — you MUST verify expected_row_count values:
Before finalizing each validation query's `expected_row_count`, mentally trace the data:
1. Start with the exact sample_data rows you defined for each source table
2. Walk through every transformation step's solution_code against that data
3. Count exactly how many rows the final target table(s) will contain
4. For information_schema queries, count how many columns/constraints match the WHERE clause
5. Set `expected_row_count` to match that exact count

VALIDATION QUERY BEST PRACTICES:
- Use `information_schema.columns` to verify table structure exists with correct column names and types
- Use `information_schema.table_constraints` to verify PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK constraints
- Use `SELECT * FROM target_table` for row count checks — simple and reliable
- `SELECT COUNT(*)` always returns exactly 1 row — so set expected_row_count=1, NOT the count value
- Keep queries simple and predictable — each should test one thing clearly
- For constraint checks: `SELECT constraint_name FROM information_schema.table_constraints WHERE table_name = 'x' AND constraint_type = 'PRIMARY KEY'` — expected_row_count = 1 per table with a PK
- information_schema queries are safe — PostgreSQL grants read access to all connected roles by default
"""

USER_PROMPT_TEMPLATE = """Generate a data modeling lab scenario with these parameters:

- **Difficulty**: {difficulty}
- **Number of source tables**: {num_source_tables}
- **Focus skills**: {focus_skills}
- **Industry/domain**: {industry}

Requirements:
1. Create {num_source_tables} source table(s) with realistic DENORMALIZED sample data (5-8 rows each, use fewer rows when there are more tables)
2. Create 1-3 target table(s) representing the PROPERLY MODELED schema (the answer key)
3. Design transformation steps where the learner must:
   a. CREATE the target tables with appropriate constraints (PK, FK, NOT NULL, etc.)
   b. Migrate/transform data from source into the new schema
4. Write validation queries that check BOTH schema correctness (information_schema) AND data correctness
5. Write comprehensive lab instructions in Markdown

For {difficulty} difficulty:
- beginner: 1NF/2NF normalization, simple primary keys, one foreign key relationship, basic NOT NULL constraints
- intermediate: Star schema design, surrogate keys (SERIAL), NOT NULL and UNIQUE constraints, multiple FKs
- advanced: CHECK constraints, composite keys, indexing considerations, slowly changing dimension patterns

The business context should feel real — use a specific company name, realistic product/service names,
and data that tells a coherent story. The learner should feel like they're solving a real business problem.
"""


REPAIR_SYSTEM_PROMPT = """You are a data engineering lab blueprint repair assistant.

You will receive a ScenarioBlueprint that failed self-test validation.
The solution code ran successfully, so the code itself is correct.
The problem is that some `expected_row_count` values don't match what the queries actually return.

Your job: fix the blueprint so validation passes. Prefer adjusting `expected_row_count` to match
the actual row counts (since the solution code produced them, they are correct).

Rules:
- Return the COMPLETE blueprint with all fields preserved
- Only modify the `expected_row_count` fields that are wrong
- Do NOT change solution_code, sample_data, table schemas, or query SQL
- Do NOT change any other fields unless absolutely necessary to fix the validation
"""


def build_repair_prompt(
    blueprint: "ScenarioBlueprint",
    failures: list[dict[str, object]],
) -> str:
    """Build a user prompt for the repair API call."""
    import json

    failure_lines = []
    for f in failures:
        failure_lines.append(
            f"- {f['query_name']}: expected {f['expected']} rows, got {f['actual']}"
            + (f" [sql: {f.get('sql', 'N/A')}]" if f.get("sql") else "")
        )

    return (
        "The following blueprint failed self-test validation.\n\n"
        "## Failures\n"
        + "\n".join(failure_lines)
        + "\n\n## Original Blueprint\n```json\n"
        + json.dumps(blueprint.model_dump(), indent=2, default=str)
        + "\n```\n\n"
        "Fix the expected_row_count values to match the actual row counts shown above, "
        "then return the complete corrected blueprint."
    )


def build_user_prompt(
    difficulty: str,
    num_source_tables: int,
    focus_skills: list[str],
    industry: str,
) -> str:
    """Build the user prompt from parameters."""
    return USER_PROMPT_TEMPLATE.format(
        difficulty=difficulty,
        num_source_tables=num_source_tables,
        focus_skills=", ".join(focus_skills),
        industry=industry,
    )
