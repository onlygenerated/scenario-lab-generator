# Labwright

**AI-powered scenario-based lab generation for technical training**

## The Problem

Technical training has a content bottleneck. Writing a good hands-on lab — one with realistic data, a coherent business scenario, working solution code, and meaningful validation — takes hours of skilled effort per exercise. Multiply that across difficulty levels, industry contexts, and skill combinations, and you're looking at a catalog that either stays small or goes stale. Learners end up cycling through the same five exercises. Instructors spend more time authoring labs than teaching.

I wanted to see if generative AI could do the heavy lifting: not just produce text instructions, but generate a complete, testable, runnable lab environment from a handful of parameters.

## What It Does

Labwright takes a learner's selections — difficulty level, focus skills (joins, window functions, data normalization, etc.), and an industry context — and produces a fully functional lab environment in about 60–90 seconds. That environment includes:

- A **realistic business scenario** with seeded source databases containing coherent sample data
- **Structured instructions** with numbered transformation steps, hints, and learning objectives
- A **JupyterLab workspace** connected to isolated PostgreSQL databases (separate source and target instances)
- A **reference solution** and a deliberately flawed solution for comparison
- **Automated validation** that checks the learner's work against expected query results, with AI-generated feedback on failures

The key constraint I set early on: every generated lab must actually work. No shipping exercises with broken solutions or mismatched validation queries. This led to the self-test architecture described below.

## How It Works

The system is a four-stage pipeline:

**1. Generation.** A prompt module (selected by topic) sends the learner's parameters to the Claude API using tool-based structured output. The response is forced into a `ScenarioBlueprint` — a Pydantic v2 model that serves as the single contract between every subsystem. Pydantic validates all identifiers against strict regex patterns, enforces SELECT-only validation queries, blocks SQL keywords in column names, and constrains data types. The AI's output is treated as untrusted input throughout.

**2. Self-test.** Before the lab reaches a learner, it's tested end-to-end. The system launches the full Docker stack, executes the solution code inside the Jupyter container, runs every validation query, and confirms they pass. It then runs the deliberately incorrect solution and verifies it fails at least one check. If validation queries have row-count mismatches, a repair loop sends the failures back to Claude to adjust expected counts while preserving the solution logic. If any step fails, the lab is blocked and diagnostics are saved. This is the part that takes most of the generation time, and it's worth it.

**3. Lab session.** The validated environment is handed to the learner with numbered workspace files (instructions, starter notebook, solution, incorrect solution) mounted into JupyterLab. Source and target databases run in separate containers on an isolated Docker network with resource limits.

**4. Validation and feedback.** When the learner submits their work, validation queries run against the target database using a read-only PostgreSQL role with a 5-second statement timeout. Failed checks are sent back to Claude for context-aware hints that reference the specific step and data involved.

## Technical Stack

- **Backend:** FastAPI (Python 3.13), Pydantic v2 for schema validation, python-on-whales for Docker orchestration, Jinja2 for compose templates
- **AI:** Anthropic Claude API with tool-based structured outputs — the model is constrained to return valid JSON matching the blueprint schema
- **Frontend:** React, TypeScript, Vite, Tailwind CSS v4
- **Lab environment:** PostgreSQL 16 and JupyterLab in per-lab isolated Docker Compose networks

## Extending to New Domains

The architecture separates *what gets taught* from *how labs are built and validated*. Adding a new domain means writing a prompt module (system prompt and parameter builder) and adding a frontend category entry. The blueprint schema, Docker orchestration, self-test pipeline, validation system, and notebook generation all work unchanged.

The current implementation covers ETL pipelines and data modeling. The category system has placeholders for data quality, exploratory analysis, feature engineering, CI/CD, container orchestration, infrastructure-as-code, networking, and security — each would require its own prompt module and possibly its own container topology, but the core generate → test → provision → validate flow remains the same.

Beyond data engineering, the pattern could apply to any domain where you can define a scenario as structured data, provision an environment from it, and validate outcomes programmatically. Database administration, API development, system configuration — anything where "did it work?" has a concrete answer.

## What's Interesting About This Approach

Most AI-assisted education tools generate content — text, quizzes, explanations. Labwright generates *infrastructure*. The AI output isn't a document to read; it's a specification that gets compiled into running databases, seeded with data, and validated by executing code against them. The self-test loop means the system won't serve a lab it can't solve itself.

The treatment of AI output as untrusted input is also worth noting. Every identifier is regex-validated. Every query is checked for mutation. Data values are escaped, not interpolated. The validation role is read-only at the database level. This isn't just defensive coding — it's a design decision that the generation pipeline should be as constrained as a user-facing form, because in a sense, it is one. The AI is filling out a very detailed form, and every field has validation rules.

The repair loop — where validation failures are fed back to the AI to fix specific mismatches — is a practical example of using AI feedback cycles to converge on correctness rather than hoping for it on the first pass.

## Status

Working proof of concept. Generates and self-tests labs across multiple difficulty levels and skill combinations. Demo mode allows exploration without API costs.
