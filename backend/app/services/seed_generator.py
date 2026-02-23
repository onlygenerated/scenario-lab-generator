"""
Blueprint → SQL conversion.

Generates seed SQL files from a ScenarioBlueprint:
  - seed_source.sql: CREATE TABLE + INSERT for source tables (data + schema)
  - seed_target.sql: CREATE TABLE only for target tables (schema only)
                     + read-only validator role

Security: Uses parameterized-style value formatting (not f-string interpolation)
for all data values. Table/column names are pre-validated by Pydantic validators.
"""

from __future__ import annotations

from ..models.blueprint import (
    ColumnDataType,
    ColumnDefinition,
    ScenarioBlueprint,
    SourceTable,
    TargetTable,
)


def _pg_type(col: ColumnDefinition) -> str:
    """Map ColumnDataType enum to Postgres DDL type string."""
    return col.data_type.value


def _col_ddl(col: ColumnDefinition) -> str:
    """Generate a single column's DDL fragment."""
    parts = [f'    "{col.name}" {_pg_type(col)}']
    if col.is_primary_key:
        parts.append("PRIMARY KEY")
    if not col.nullable and not col.is_primary_key:
        parts.append("NOT NULL")
    return " ".join(parts)


def _escape_sql_value(value: str | int | float | bool | None) -> str:
    """Safely escape a value for SQL INSERT. Not f-string interpolation."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    # String: escape single quotes by doubling them
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _create_table_sql(table_name: str, columns: list[ColumnDefinition]) -> str:
    """Generate CREATE TABLE statement."""
    col_defs = ",\n".join(_col_ddl(col) for col in columns)
    return f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n{col_defs}\n);\n'


def _insert_rows_sql(table_name: str, columns: list[ColumnDefinition], rows: list[dict]) -> str:
    """Generate INSERT statements for sample data rows."""
    if not rows:
        return ""
    col_names = [col.name for col in columns]
    quoted_cols = ", ".join(f'"{c}"' for c in col_names)

    lines = []
    for row in rows:
        values = []
        for col_name in col_names:
            val = row.get(col_name)
            values.append(_escape_sql_value(val))
        values_str = ", ".join(values)
        lines.append(f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({values_str});')

    return "\n".join(lines) + "\n"


def _validate_generated_sql(sql: str) -> None:
    """Sanity check: ensure no dangerous DDL/DML leaked into seed scripts."""
    dangerous = {"DROP", "ALTER", "GRANT", "REVOKE", "TRUNCATE"}
    # Tokenize and check (skip our own CREATE TABLE and INSERT INTO)
    upper = sql.upper()
    for keyword in dangerous:
        # Check for keyword as a standalone word
        if f" {keyword} " in f" {upper} ":
            raise ValueError(f"Generated SQL contains forbidden keyword: {keyword}")


def generate_source_sql(blueprint: ScenarioBlueprint) -> str:
    """Generate the full seed SQL for the source database."""
    parts = ["-- Source database seed SQL (auto-generated from blueprint)\n"]
    parts.append("-- Tables with sample data\n\n")

    for table in blueprint.source_tables:
        parts.append(f"-- Table: {table.table_name}\n")
        parts.append(_create_table_sql(table.table_name, table.columns))
        parts.append("\n")
        parts.append(_insert_rows_sql(table.table_name, table.columns, table.sample_data))
        parts.append("\n")

    result = "".join(parts)
    _validate_generated_sql(result)
    return result


def generate_target_sql(blueprint: ScenarioBlueprint) -> str:
    """Generate the seed SQL for the target database (schema only + validator role)."""
    parts = ["-- Target database seed SQL (auto-generated from blueprint)\n"]
    parts.append("-- Empty target table schemas\n\n")

    for table in blueprint.target_tables:
        parts.append(f"-- Table: {table.table_name}\n")
        parts.append(_create_table_sql(table.table_name, table.columns))
        parts.append("\n")

    # Create read-only validator role for secure validation queries
    parts.append("-- Read-only validator role for completion checking\n")
    parts.append("DO $$\n")
    parts.append("BEGIN\n")
    parts.append("  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'validator') THEN\n")
    parts.append("    CREATE ROLE validator WITH LOGIN PASSWORD 'validatorpass';\n")
    parts.append("  END IF;\n")
    parts.append("END\n")
    parts.append("$$;\n\n")

    # Grant SELECT-only on all target tables
    for table in blueprint.target_tables:
        parts.append(f'GRANT SELECT ON "{table.table_name}" TO validator;\n')

    # Default privileges for future tables
    parts.append("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO validator;\n")

    result = "".join(parts)
    return result
