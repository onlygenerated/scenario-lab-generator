# Security

## Trust Boundaries

1. **AI-generated content is untrusted** — all blueprint data (table names, SQL, sample data, Markdown) passes through Pydantic validators and runtime security checks before being used.

2. **Lab containers are sandboxed** — each lab runs in an isolated Docker network. Containers have resource limits (memory, CPU), no privileged mode, and no access to the host Docker socket.

3. **Validation queries are read-only** — the validator uses a Postgres role with SELECT-only grants and a 5-second statement timeout.

## Dependency Audit Process

- **Python**: Run `pip-audit` after every dependency change. All versions are pinned in `requirements.txt`.
- **Node.js**: Run `npm audit` after every dependency change. `package-lock.json` is committed to git.
- **Docker**: Run `docker scout cves` on all base images before incorporating them.

## Reporting Vulnerabilities

If you discover a security issue, please email the maintainer directly rather than opening a public issue.

## Known Limitations (PoC Scope)

- No authentication or authorization (would be added for production)
- API rate limiting is in-memory only (not distributed)
- CORS is restricted to localhost origins
- Lab credentials are hardcoded (acceptable for local PoC)
