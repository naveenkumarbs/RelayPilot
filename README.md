# RelayPilot

**An AI-powered, multi-tenant SaaS platform for customer support and incident resolution.**

RelayPilot is being built to help small and medium businesses investigate customer issues, answer questions using approved business knowledge, execute authorized support actions, and escalate unresolved issues to a human with evidence and a clear handoff.

**Status: early development.** The current savepoint establishes the backend foundation. Authentication, enforced tenant isolation, chat, retrieval, and agent execution are not yet implemented. This is not a production-ready service.

## Product vision

Businesses will subscribe to RelayPilot and operate within their own workspace. The intended SaaS model supports tenant-specific knowledge, customer records, connected tools, escalation policies, and entitlements. Longer-term options include tenant-selected model providers, reports, and agent/tool subscriptions.

A typical customer journey will be:

1. A customer describes an issue through chat.
2. RelayPilot establishes the business and authenticated customer context.
3. It retrieves permitted knowledge and requests approved business tools.
4. The application authorizes and executes each requested action.
5. The agent verifies the outcome and responds with grounded information.
6. If resolution is unsuccessful or unsafe, it creates an escalation with the issue, evidence, and actions attempted.

The model never grants access or establishes authoritative tenant identity. Those decisions belong to application code.

## V1 scope

The first release targets one software/service-provider support domain, with two demo tenants and persistent demo business records.

Planned tools:

- Check a customer's subscription status.
- Check service status.
- Create a support ticket with duplicate-request protection.

V1 demonstration outcomes:

- **Resolved:** answer a support request using permitted knowledge and verified tool results.
- **Blocked:** reject access to another tenant's or customer's information.
- **Escalated:** create a ticket with evidence and a useful human handoff.

Web chat is the initial channel. WhatsApp integration, subscription billing, arbitrary tenant connectors, multiple model providers, autonomous remediation, Spring Boot, and Kubernetes are deferred.

## Current implementation

Progress below reflects the development savepoint reported by the maintainer. It is not an independent code audit. The tenant migration was the most recently supplied implementation step; its application is tracked separately until confirmed.

- [x] Python virtual environment and initial backend layout.
- [x] FastAPI application served by Uvicorn.
- [x] Modular health routes and central API router.
- [x] Interactive OpenAPI documentation.
- [x] Application startup/shutdown logging.
- [x] HTTP request logging with generated request IDs, status, and duration.
- [x] Centralized, validated environment settings using Pydantic Settings.
- [x] SQLite connection through SQLAlchemy 2.x.
- [x] Shared engine with request-scoped database sessions.
- [x] Foreign-key enforcement on new SQLite connections.
- [x] Database readiness endpoint and connection cleanup on shutdown.
- [ ] Confirm tenant model and first Alembic migration are applied and verified.
- [ ] Seed two demo tenants.
- [ ] Authentication and tenant/customer authorization.
- [ ] Customer chat, RAG, tools, agent orchestration, and escalation.

No LLM credentials are required to run the current backend.

## Architecture and technology

| Layer | Technology | Status |
| --- | --- | --- |
| API | Python, FastAPI, Uvicorn | Implemented |
| Configuration | Pydantic Settings, `.env` | Implemented |
| Logging | Python `logging`, request middleware | Implemented |
| Business persistence | SQLite, SQLAlchemy | Implemented |
| Schema migrations | Alembic | First migration pending confirmation |
| Frontend | React, TypeScript, Vite, Material UI | Planned |
| Identity | JWT authentication, password hashing, tenant membership | Planned; libraries to be selected |
| Retrieval and model integrations | LangChain | Planned |
| Vector storage | Local Chroma, tenant-scoped retrieval | Planned |
| Agent orchestration | LangGraph | Planned |
| Agent persistence | SQLite LangGraph checkpointer | Planned; separate from business DB |
| Agent traces and evaluations | LangSmith | Planned |
| Documents | Local filesystem | Planned |
| Verification | pytest, scenario datasets | Planned |
| Packaging and CI | Docker Compose, GitHub Actions | Planned |
| Infrastructure observability | OpenTelemetry, Prometheus, Grafana | Later extension; scope to be decided |

LangChain will provide model, retrieval, and tool integrations. LangGraph will control stateful execution and escalation. LangSmith will support agent tracing and evaluations. FastAPI remains the authorization and business-operation boundary.

Use one model provider and one embedding model initially; selection is pending. Ollama is an option for local experimentation, subject to tool-calling quality checks.

### Database ownership

The SQLAlchemy engine is shared per application process. Each request that declares the database dependency receives its own session. Connections are borrowed as needed and returned to the pool; sessions are not shared across concurrent requests. Business services will explicitly commit successful writes.

SQLite supports the local demo. It does not provide PostgreSQL-style row-level security, and it has limited concurrent-write capacity. Application authorization and tenant-scoped queries must enforce isolation. A later PostgreSQL migration will require migration and integration testing.

## Project layout

The backend layout below reflects the foundation and proposed first migration. Migration-related entries exist only after the Alembic step is completed.

```text
RelayPilot/
    README.md
    .gitignore
    docs/
    backend/
        .env.example
        requirements.txt
        alembic.ini                  # migration setup
        migrations/                  # migration setup
            env.py
            versions/
        app/
            __init__.py
            main.py
            api/
                __init__.py
                router.py
                routes/
                    __init__.py
                    health.py
            core/
                __init__.py
                config.py
                logging_config.py
            db/
                __init__.py
                session.py
                base.py              # migration setup
            models/                  # migration setup
                __init__.py
                tenant.py
        tests/
```

Local `.venv/`, `backend/.env`, and `backend/data/` are generated locally and must remain outside version control. Frontend, service, repository, retrieval, tool, and agent modules will be added when their milestones begin.

## Local environment setup

### Prerequisites

- Python 3.12 recommended for the current development baseline.
- Git.
- PowerShell on Windows; equivalent shell commands work on other platforms.
- A code editor such as VS Code.

Node.js/npm, Docker, an LLM provider, and LangSmith are not required for this backend savepoint. Add them when their milestones begin.

### 1. Clone and create a virtual environment

Clone your actual repository and change into its root. The repository URL is intentionally omitted until published.

```powershell
git clone <repository-url>
cd <repository-directory>
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Replace the angle-bracket placeholders before running the first two commands.

If local policy prevents activation, activation is optional: use `.\.venv\Scripts\python.exe` from the repository root, or `..\.venv\Scripts\python.exe` from `backend`, instead of `python` in the commands below.

### 2. Install dependencies

```powershell
cd backend
python -m pip install -r requirements.txt
```

The foundation dependencies are FastAPI, Uvicorn, Pydantic Settings, and SQLAlchemy. Alembic is needed once migrations are included. Lang packages will be introduced when used rather than installed prematurely.

### 3. Configure the environment

For a fresh checkout only, copy the template; do not overwrite an existing customized `.env`:

```powershell
Copy-Item .env.example .env
```

The template should contain:

```dotenv
RELAYPILOT_APP_NAME="RelayPilot API"
RELAYPILOT_APP_VERSION=0.1.0
RELAYPILOT_ENVIRONMENT=development
RELAYPILOT_LOG_LEVEL=INFO
RELAYPILOT_DATABASE_PATH=data/relaypilot.db
RELAYPILOT_DATABASE_TIMEOUT_SECONDS=10
```

| Setting | Purpose |
| --- | --- |
| `RELAYPILOT_APP_NAME` | API documentation title |
| `RELAYPILOT_APP_VERSION` | Application version |
| `RELAYPILOT_ENVIRONMENT` | `development`, `test`, or `production` |
| `RELAYPILOT_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `RELAYPILOT_DATABASE_PATH` | SQLite path; relative paths resolve against `backend` |
| `RELAYPILOT_DATABASE_TIMEOUT_SECONDS` | Positive SQLite lock-wait timeout in seconds |

Environment variables override `.env`; defaults apply when neither supplies a value. Restart the server after changing configuration. Invalid constrained values should fail startup validation. Setting `environment=production` alone does not harden or deploy the application.

### 4. Apply migrations, when included

If this checkout contains `alembic.ini` and the initial tenant revision, run from `backend`:

```powershell
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

If those files have not been added yet, skip this step: health and database connectivity can be checked without application tables. Do not run `alembic init` in a checkout that already includes migration configuration.

### 5. Start the backend

```powershell
python -m uvicorn app.main:app --reload --no-access-log
```

Run from `backend`. The server listens on localhost port 8000 by default. `--reload` is for development. `--no-access-log` avoids duplicating the custom HTTP request logs.

- API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Liveness: http://127.0.0.1:8000/health
- Database readiness: http://127.0.0.1:8000/health/ready

Stop the server with `Ctrl+C`.

### 6. Verify the savepoint

In a second PowerShell terminal:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health/ready"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health"
$response.Headers["X-Request-ID"]
```

Expected liveness response:

```json
{"status": "ok", "service": "relaypilot-api"}
```

Expected readiness response:

```json
{"status": "ready", "database": "ok"}
```

Readiness returns HTTP 503 when its database operation fails. It currently verifies `SELECT 1`, not schema completeness, write capability, agent health, or tenant isolation. The SQLite file is created on the first database connection.

From `backend`, verify foreign keys:

```powershell
python -c "from app.db.session import engine; c = engine.connect(); print(c.exec_driver_sql('PRAGMA foreign_keys').scalar_one()); c.close(); engine.dispose()"
```

Expected output: `1`.

After applying the first migration, inspect table names:

```powershell
python -c "from sqlalchemy import inspect; from app.db.session import engine; print(inspect(engine).get_table_names()); engine.dispose()"
```

Expected tables include `tenants` and `alembic_version`.

## Logging

Application logs currently go to the console and include lifecycle events and HTTP method, route template, status, duration, and a generated request ID. Completed responses include `X-Request-ID`.

Do not deliberately log credentials, authorization headers, customer message bodies, documents, or full settings objects. SQLAlchemy parameter hiding is enabled. Unexpected exceptions currently include tracebacks; comprehensive redaction is not yet implemented, so use synthetic data and review logs before sharing them.

Future work includes authenticated tenant context, correlation with agent runs, structured JSON output, and redaction. LangSmith tracing must follow the same data-handling rules before external tracing is enabled.

## V1 milestones and checkpoints

Status is maintained manually. Update the checkboxes and development log in the same pull request as the corresponding implementation. A milestone is complete only after its acceptance checkpoints pass.

| ID | Milestone | Tentative technology | Acceptance checkpoint | Status |
| --- | --- | --- | --- | --- |
| M1 | Application foundation | Python, FastAPI, Uvicorn, Pydantic Settings, Python logging | Health/docs work; settings validate; request logs exist | Complete per maintainer |
| M2 | Persistence, identity, and tenant boundaries | SQLite, SQLAlchemy, Alembic, JWT, password hashing | Migrations reproduce schema; two tenants seeded; unauthorized cross-tenant/customer requests rejected | In progress |
| M3 | Support chat interface | React, TypeScript, Vite, Material UI, FastAPI | Login, authorized conversation history, and ticket status work | Planned |
| M4 | Tenant knowledge and RAG | LangChain, Chroma, embedding model, local files | Scoped ingestion/retrieval; relevant source citations; explicit insufficient-evidence fallback | Planned |
| M5 | Authorized business tools | LangChain tools, Pydantic, service/repository layer, SQLite | Three tools work; permissions enforced; duplicate ticket requests handled | Planned |
| M6 | Stateful support agent | LangGraph, SQLite checkpointer, chosen model integration | Bounded tool loop, persisted conversations, verified outcomes, authorized resume | Planned |
| M7 | Human escalation | LangGraph routing, FastAPI, SQLite, React | Queue shows summary, evidence, attempted actions, unresolved questions; customer receives ticket reference | Planned |
| M8 | Evaluations and observability | LangSmith, pytest, scenario datasets, structured logging | Repeatable results for correctness, grounding, access control, failures, latency, and usage/cost | Planned |
| M9 | Reproducible demo and delivery | Docker Compose, GitHub Actions, documentation | Fresh checkout starts reproducibly; CI passes; demo reproduces resolve/block/escalate scenarios | Planned |

Testing begins with each feature. M8 consolidates the evaluation harness and results; authorization tests must begin in M2.

### Detailed progress checklist

#### M1 — Foundation

- [x] Health endpoint and API docs.
- [x] Route separation.
- [x] Lifecycle and request logging.
- [x] Centralized validated settings.
- [ ] Record a reproducible dependency-version baseline.

#### M2 — Persistence and identity

- [x] SQLite engine and request-scoped sessions.
- [x] Foreign-key enforcement and database readiness.
- [x] Confirm model base, tenant model, and initial migration verification.
- [x] Idempotent development seed script for two tenants.
- [ ] Users, tenant membership, and customer identity.
- [ ] Authentication and password hashing.
- [ ] Tenant/customer authorization checks with negative tests.
- [ ] Define role permissions and disabled-tenant behavior.

#### M3–M5 — Customer experience and capabilities

- [ ] Authenticated web chat and persisted history.
- [ ] Customer ticket status view.
- [ ] Scoped document ingestion, retrieval, and citations.
- [ ] Subscription-status tool.
- [ ] Service-status tool.
- [ ] Ticket-creation tool and idempotency handling.
- [ ] Tests for missing records, denied access, and tool failures.

#### M6–M7 — Agent and handoff

- [ ] Explicit graph state, routing, and execution limits.
- [ ] Persistent checkpoints scoped to tenant and conversation.
- [ ] Evidence-grounded outcome verification.
- [ ] Human escalation queue and customer ticket reference.
- [ ] Authorization checks for checkpoint resume and support access.

#### M8–M9 — Evaluation and release

- [ ] Versioned scenario dataset and grading criteria.
- [ ] Redacted agent tracing and prompt/version tracking.
- [ ] Recorded resolution, grounding, escalation, latency, and usage results.
- [ ] Tests for cross-tenant attempts and misleading document/tool content.
- [ ] Docker packaging and CI checks.
- [ ] Fresh-checkout walkthrough and demo recording.

## Security requirements for upcoming work

- Derive tenant and customer identity from verified application context, not model output or untrusted tool arguments.
- Add tenant ownership to tenant-owned records and enforce access in the service/repository layer.
- Filter both retrieval and business queries before data reaches the model.
- Scope conversations, documents, checkpoints, credentials, and support views to authorized users.
- Treat retrieved documents and tool output as untrusted content; they cannot override application permissions.
- Define approval requirements before adding consequential actions.
- Use synthetic records and documents for public demonstrations.

These are design requirements, not a claim that isolation is already implemented.

## Development and migration workflow

For a model change, from `backend`:

```powershell
python -m alembic revision --autogenerate -m "describe the schema change"
# Review the generated upgrade and downgrade functions before applying.
python -m alembic upgrade head
#seed demo tenants
python -m app.scripts.seed_demo_tenants
python -m alembic check
```

Commit migration scripts with the model change. Do not use application-startup `create_all()` as a replacement for migrations. Autogenerated migrations need review, particularly renames and SQLite table changes.

When pytest and tests are introduced, run from `backend`:

```powershell
python -m pytest
```

No automated test coverage or CI pass is claimed at the current savepoint.

## Contributing

Contributions are welcome in backend development, frontend, retrieval, agent orchestration, security, testing/evaluations, and documentation.

1. Discuss a milestone-sized task with the maintainer before starting.
2. Create a focused branch and keep changes reviewable.
3. Include setup/configuration changes and relevant verification results.
4. Add meaningful tests for business rules, authorization, and failure handling.
5. Update the applicable milestone checkboxes and development log.
6. Open a pull request describing the behavior, validation, and remaining limitations.

Develop the project incrementally: contributors should be able to explain the behavior and tradeoffs of code they add. Avoid introducing infrastructure or frameworks without a current need.

License and contribution terms have not yet been selected. Repository visibility alone does not establish an open-source license; agree on terms with the maintainer before substantial contributions or redistribution.

## Development log

| Date | Savepoint/change | Verification | Next action |
| --- | --- | --- | --- |
| 2026-10-25 | Backend foundation: routing, logging, validated settings, SQLite/SQLAlchemy integration | Maintainer reports foundation complete; health/docs confirmed earlier; no independent source review performed for this README | Confirm first tenant migration, seed tenants, begin identity and authorization |

For each future change, add a row with the date, concrete behavior implemented, checks performed, and next action. Replace pending items only after verification; record failures and limitations honestly.

## Current limitations

- Early local-development implementation, not a deployed SaaS service.
- No customer-facing agent, chat UI, knowledge ingestion, or tool execution yet.
- Authentication and tenant isolation remain to be implemented.
- No billing, WhatsApp integration, arbitrary connectors, or subscription enforcement.
- No published agent accuracy, security, load, or production reliability results.
- SQLite connectivity alone does not validate schema state or production scalability.

## Reference documentation

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [LangChain and LangGraph](https://docs.langchain.com/)
- [Chroma](https://docs.trychroma.com/)

