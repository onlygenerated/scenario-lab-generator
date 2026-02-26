"""
Prompt templates for data pipeline / ETL scenario generation.

These are passed to Claude API with structured output to produce ScenarioBlueprints.
"""

SYSTEM_PROMPT = """You are an expert instructional designer for data engineering training.
You create realistic, hands-on ETL lab scenarios that teach data pipeline skills through practice.

Your scenarios must:
- Use realistic business contexts that a junior data engineer would encounter
- Include properly normalized source data with deliberate data quality challenges
- Define clear transformation steps that build skills progressively
- Include validation queries that verify the learner completed the work correctly
- Generate sample data that is internally consistent (foreign keys match, dates are logical, etc.)

CRITICAL RULES for generated content:
- Table and column names MUST be lowercase with underscores only (e.g., order_items, not OrderItems)
- Table and column names MUST NOT be SQL reserved words (e.g., don't use 'select', 'table', 'index', 'order' as names - use 'orders', 'customer_orders', etc.)
- Sample data values must not contain SQL injection patterns or special characters beyond normal business data
- Primary key values in sample_data MUST be unique — PostgreSQL will reject duplicate PKs. If you want learners to handle duplicates, use a SERIAL auto-increment PK and place duplicate values in non-PK columns (e.g., an `is_duplicate` flag or repeated business-key values in a non-PK column)
- Validation queries MUST be SELECT-only — never include INSERT, UPDATE, DELETE, DROP, or other DML/DDL
- All validation queries must reference only the target tables, not source tables
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
- `hint` should be a brief nudge (e.g., "Use pd.merge() with an inner join" NOT the full merge statement with all arguments)
- `description` explains WHAT to do, not HOW to do it in code
- `lab_instructions` is a Markdown summary — keep it brief, no code blocks with solutions

SOLUTION CODE RULES — each transformation step MUST include a `solution_code` field:
- `solution_code` contains working Python (pandas + sqlalchemy) that performs the step
- The setup is automatic: `source_engine`, `target_engine`, `pd`, and `create_engine` are pre-imported
- Variables from prior steps carry over (e.g., a DataFrame created in step 1 is available in step 2)
- The code must be correct and complete — it will be executed as a self-test before the student sees the lab
- Use `pd.read_sql_table()` to read source tables and `.to_sql()` to write target tables
- Use `if_exists='replace'` when writing to target tables for idempotency
- The lab runs pandas 2.x — do NOT use deprecated APIs: no `infer_datetime_format`, no `append()`, use `pd.concat()` instead of `DataFrame.append()`
- IMPORTANT: For `pd.to_datetime()`, NEVER pass a `format=` argument. Just call `pd.to_datetime(col)` with no format — pandas 2.x infers automatically. Specifying a format causes failures when it doesn't match the data.
- All DATE and TIMESTAMP values in sample_data MUST use ISO 8601 format: "YYYY-MM-DD" for dates, "YYYY-MM-DD HH:MM:SS" for timestamps. Never use "MM/DD/YYYY" or other regional formats.

EXPECTED ROW COUNT CONSISTENCY — you MUST verify expected_row_count values:
Before finalizing each validation query's `expected_row_count`, mentally trace the data:
1. Start with the exact sample_data rows you defined for each source table
2. Walk through every transformation step's solution_code against that data
3. Count exactly how many rows the final target table(s) will contain
4. Set `expected_row_count` to match that exact count

Common pitfalls that cause mismatches:
- INNER JOIN reduces rows when keys don't match across all source rows
- GROUP BY produces one row per distinct group — count the unique group keys in your sample data
- WHERE/HAVING clauses filter rows — count how many sample rows actually pass the condition
- NULL values in join keys cause rows to be dropped in INNER JOINs
- One-to-many joins can INCREASE row count — if a key appears 3 times in the right table, you get 3 output rows
- NULL values in aggregated columns: if ALL values in a group are NULL, aggregate functions (SUM, AVG) return NULL, which can cause the entire row to be dropped by downstream filters or HAVING clauses
- If sample_data contains NULLs in columns used for aggregation or grouping, trace exactly what happens to those NULLs through every transformation step — they may cause groups to disappear from the final output
- SAFEST APPROACH: do NOT put NULL values in columns that are used for aggregation, JOIN keys, or GROUP BY keys unless NULL handling is explicitly part of the learning objective. Use realistic non-NULL placeholder values instead.
Do a final double-check: for every validation query, verify expected_row_count against the sample data.

VALIDATION QUERY BEST PRACTICES:
- For total row count checks, prefer `SELECT * FROM target_table` — simple and reliable
- `SELECT COUNT(*)` always returns exactly 1 row — so set expected_row_count=1, NOT the count value
- Avoid complex subqueries in validation queries — keep them simple and predictable
- Each validation query should test one thing clearly
- When a validation query filters with WHERE on a specific value (e.g., WHERE city = 'X'), verify that value actually survives all JOINs, filters, GROUP BYs, and NULL handling in the sample data — if no rows match, the query returns 0 rows
- Prefer validation queries that check the full target table (e.g., `SELECT * FROM target_table`) over queries that filter for specific values that may not exist after transformations
- If you must validate a specific row, pick a value you are 100% certain exists in the output after all transformations — trace it through every step
"""

USER_PROMPT_TEMPLATE = """Generate a data pipeline lab scenario with these parameters:

- **Difficulty**: {difficulty}
- **Number of source tables**: {num_source_tables}
- **Focus skills**: {focus_skills}
- **Industry/domain**: {industry}

Requirements:
1. Create {num_source_tables} source table(s) with realistic sample data (5-8 rows each, use fewer rows when there are more tables)
2. Create 1-2 target table(s) that the learner must populate
3. Design transformation steps that emphasize: {focus_skills}
4. Write validation queries that check the final result
5. Write comprehensive lab instructions in Markdown

For {difficulty} difficulty:
- beginner: Simple JOINs, basic aggregation, straightforward cleaning
- intermediate: Multi-table JOINs, date handling, NULL treatment, grouping
- advanced: Window functions, pivoting, complex business rules, data quality edge cases

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
