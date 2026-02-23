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
- Validation queries MUST be SELECT-only — never include INSERT, UPDATE, DELETE, DROP, or other DML/DDL
- All validation queries must reference only the target tables, not source tables
- Markdown instructions should be well-structured with clear headers, tables, and step-by-step guidance

SOLUTION CODE RULES — each transformation step MUST include a `solution_code` field:
- `solution_code` contains working Python (pandas + sqlalchemy) that performs the step
- The setup is automatic: `source_engine`, `target_engine`, `pd`, and `create_engine` are pre-imported
- Variables from prior steps carry over (e.g., a DataFrame created in step 1 is available in step 2)
- The code must be correct and complete — it will be executed as a self-test before the student sees the lab
- Use `pd.read_sql_table()` to read source tables and `.to_sql()` to write target tables
- Use `if_exists='replace'` when writing to target tables for idempotency
"""

USER_PROMPT_TEMPLATE = """Generate a data pipeline lab scenario with these parameters:

- **Difficulty**: {difficulty}
- **Number of source tables**: {num_source_tables}
- **Focus skills**: {focus_skills}
- **Industry/domain**: {industry}

Requirements:
1. Create {num_source_tables} source table(s) with realistic sample data (5-15 rows each)
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
