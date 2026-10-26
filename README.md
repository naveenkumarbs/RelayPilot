# RelayPilot

**An AI-powered, multi-tenant SaaS platform for customer support and incident resolution.**

RelayPilot is being built to help small and medium businesses investigate customer issues, answer questions using approved business knowledge, execute authorized support actions, and escalate unresolved issues to a human with evidence and a clear handoff.

**Status: early development.** The current savepoint includes the backend foundation, identity models, password hashing, JWT login, and a protected current-user endpoint. Tenant authorization, chat, retrieval, and agent execution are not yet implemented. This is not a production-ready service.

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

Progress reflects the maintainer's reported implementation and manual checks, most recently updated on 2026-10-26. It is not an independent source-code audit. Implemented behavior and verified scenarios are tracked separately.

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
- [x] Tenant model and first Alembic migration applied and verified.
- [x] Idempotent seeding of two demo tenants.
- [x] User and tenant membership models with verified migrations.
- [x] Argon2 password hashing and development admin account creation.
- [x] JWT configuration validation and short-lived access tokens using PyJWT.
- [x] POST `/auth/login` and protected GET `/auth/me`.
- [x] Successful login and authenticated identity lookup manually verified.
- [x] Protected tenant membership endpoint: GET `/tenants/{tenant_slug}/me`.
- [x] Active tenant and membership validation using the authenticated user.
- [x] Cross-tenant membership access rejected.
- [x] Reusable verified tenant context for upcoming business operations.
- [x] Automated authentication and tenant-access tests using isolated SQLite databases.
- [x] Current pytest suite passes.
- [ ] Tenant/customer authorization and role enforcement.
- [ ] Customer chat, RAG, tools, agent orchestration, and escalation.

No LLM credentials are required to run the current backend.

## Tenant authorization

GET `/tenants/{tenant_slug}/me` returns the authenticated user's membership
only when the user, tenant, and membership are active.

The requested tenant slug selects a workspace; it does not grant access.
Application code verifies membership against the database before returning
a TenantContext containing the verified tenant ID, slug, user ID, and role.

| Scenario | Expected response |
| --- | --- |
| Active user accessing their active tenant membership | 200 |
| User accessing another tenant without membership | 403 |
| Unknown or inactive tenant | 403 |
| Inactive membership | 403 |
| Missing or invalid authentication | 401 |
| Inactive user with a previously issued token | 401 |

Inaccessible tenant scenarios use the same generic response:
`{"detail": "Tenant access denied"}`.

This boundary currently protects the tenant membership endpoint.
Role-specific permissions and resource-level authorization remain pending.

## Architecture and technology

| Layer | Technology | Status |
| --- | --- | --- |
| API | Python, FastAPI, Uvicorn | Implemented |
| Configuration | Pydantic Settings, `.env` | Implemented |
| Logging | Python `logging`, request middleware | Implemented |
| Business persistence | SQLite, SQLAlchemy | Implemented |
| Schema migrations | Alembic | Tenant and user/membership migrations verified |
| Frontend | React, TypeScript, Vite, Material UI | Planned |
| Identity | User/membership models, pwdlib with Argon2, PyJWT, FastAPI HTTPBearer | Login and current-user endpoint implemented; tenant authorization pending |
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

The layout below reflects the implemented backend savepoint. Runtime data and secrets remain local.

The key source locations are:

| Location | Responsibility |
| --- | --- |
| `backend/app/main.py` | Application setup, lifecycle, request logging |
| `backend/app/api/router.py` | Central route registration |
| `backend/app/api/dependencies.py` | Bearer authentication and current-user dependency |
| `backend/app/api/routes/health.py` | Liveness and database readiness |
| `backend/app/api/routes/auth.py` | Login and current-user endpoints |
| `backend/app/core/config.py` | Validated application and JWT settings |
| `backend/app/core/logging_config.py` | Console logging configuration |
| `backend/app/core/security.py` | Password hashing and verification |
| `backend/app/core/tokens.py` | JWT creation and validation |
| `backend/app/db/base.py` | Declarative model base and constraint naming |
| `backend/app/db/session.py` | Engine, sessions, foreign-key setup |
| `backend/app/models/` | Tenant, User, TenantMembership |
| `backend/app/schemas/auth.py` | Login, token, and safe user-response schemas |
| `backend/app/scripts/` | Tenant seeding and interactive admin creation |
| `backend/migrations/` | Versioned Alembic migrations |
| `backend/requirements.txt` | Backend dependencies |
| `backend/.env.example` | Configuration template without secrets |
| `backend/tests/` | Location reserved for automated checks |
| `docs/` | Architecture and contributor notes |

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

The current dependencies include FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy, Alembic, pwdlib[argon2], and PyJWT. Lang packages will be introduced when used rather than installed prematurely.

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
RELAYPILOT_JWT_SECRET_KEY=
RELAYPILOT_ACCESS_TOKEN_EXPIRE_MINUTES=15
RELAYPILOT_JWT_ISSUER=relaypilot
RELAYPILOT_JWT_AUDIENCE=relaypilot-api
```

Generate a random local signing secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Paste the output into `RELAYPILOT_JWT_SECRET_KEY` in your local `.env` before running any command that loads Settings. The secret is required and must contain at least 32 characters. Keep the value empty in the committed `.env.example`. Never commit or share the actual secret. `SecretStr` masks ordinary representations; it does not encrypt the file.

Access-token lifetime is validated between 1 and 60 minutes. The default is 15. Issuer and audience are checked when tokens are decoded. Changing the signing secret invalidates tokens signed with the previous secret.

| Setting | Purpose |
| --- | --- |
| `RELAYPILOT_APP_NAME` | API documentation title |
| `RELAYPILOT_APP_VERSION` | Application version |
| `RELAYPILOT_ENVIRONMENT` | `development`, `test`, or `production` |
| `RELAYPILOT_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `RELAYPILOT_DATABASE_PATH` | SQLite path; relative paths resolve against `backend` |
| `RELAYPILOT_DATABASE_TIMEOUT_SECONDS` | Positive SQLite lock-wait timeout in seconds |
| `RELAYPILOT_JWT_SECRET_KEY` | Required random signing secret; at least 32 characters |
| `RELAYPILOT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime, 1–60 minutes |
| `RELAYPILOT_JWT_ISSUER` | Expected token issuer |
| `RELAYPILOT_JWT_AUDIENCE` | Expected API audience |

Environment variables override `.env`; defaults apply when neither supplies a value. Restart the server after changing configuration. Invalid constrained values should fail startup validation. Setting `environment=production` alone does not harden or deploy the application.

### 4. Apply migrations

Run from `backend` to create or update the schema:

```powershell
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

The migrations create tenants, users, and memberships. Do not run `alembic init` in a checkout that already includes migration configuration.

### 5. Seed development tenants and accounts

Run these commands from `backend`, with the virtual environment active.

First, create the two demo tenants:

    python -m app.scripts.seed_demo_tenants

The tenants are:

- `acme-services`

- `brightdesk-solutions`

The script skips existing tenants on repeated sequential runs.

Next, create a development admin:

    python -m app.scripts.create_demo_admin

Run it once for each tenant, using different email addresses and passwords.

Suggested demo identities:

| Tenant slug | Admin email |
| --- | --- |
| `acme-services` | `admin.acme@example.com` |
| `brightdesk-solutions` | `admin.brightdesk@example.com` |

Passwords are entered through hidden terminal prompts and stored as Argon2 hashes. Use development-only passwords; do not commit credentials or database files.

Both scripts require `RELAYPILOT_ENVIRONMENT=development`.

The admin script creates a new user and their tenant membership in one transaction. If the email already exists, it makes no changes: it does not reset passwords or grant additional memberships.

These accounts can authenticate through POST `/auth/login` once the backend is running.

### 6. Start the backend

```powershell
python -m uvicorn app.main:app --reload --no-access-log
```

Run from `backend`. The server listens on localhost port 8000 by default. `--reload` is for development. `--no-access-log` avoids duplicating the custom HTTP request logs.

- API documentation: http://127.0.0.1:8000/docs

- OpenAPI schema: http://127.0.0.1:8000/openapi.json

- Liveness: http://127.0.0.1:8000/health

- Database readiness: http://127.0.0.1:8000/health/ready

Stop the server with `Ctrl+C`.

### 7. Verify the savepoint

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

Expected tables are `alembic_version`, `tenants`, `users`, and `tenant_memberships`.

## Authentication

### Implemented behavior

- POST `/auth/login` accepts JSON email/password credentials and issues a short-lived access token.
- Email input is stripped and lowercased to match development account creation.
- Password verification uses pwdlib with Argon2; unknown accounts use a dummy hash to reduce timing differences.
- GET `/auth/me` requires an Authorization Bearer header, validates the token, and reloads the user from the database.
- JWT decoding restricts the algorithm to HS256, validates issuer/audience/expiry, requires the configured claims, and checks access-token type and user subject.
- Missing/deleted/inactive users are rejected by the current-user dependency.
- The response schema exposes only user ID, email, and display name; password hashes are excluded.
- Successful token responses include cache-prevention headers.
- Authentication failures use generic 401 responses.

These describe the implementation; only the successful login/current-user path has been explicitly reported as verified.

| Method | Endpoint | Purpose | Authentication |
| --- | --- | --- | --- |
| POST | `/auth/login` | Issue an access token | JSON email/password |
| GET | `/auth/me` | Return current-user identity | Bearer access token |

Example login body (replace the password locally):

```json
{
  "email": "admin.acme@example.com",
  "password": "<your-development-password>"
}
```

Protected requests use:

```http
Authorization: Bearer <access_token>
```

### Verify through Swagger

1. Open http://127.0.0.1:8000/docs.
2. Execute POST `/auth/login` with a seeded development account.
3. Copy only the returned `access_token` value.
4. Click **Authorize** and paste the token without quotes or the `Bearer` prefix. Swagger adds the prefix for HTTPBearer.
5. Execute GET `/auth/me` and confirm the expected user identity, without a password hash.

Login does not automatically authorize later Swagger requests. Refreshing the page may require authorizing again. Do not share screenshots or generated curl commands containing tokens.

### Verification tracker

| Scenario | Status |
| --- | --- |
| Correct credentials return an access token | Manually verified |
| Valid Bearer token returns current-user identity | Manually verified |
| Missing authorization returns 401 | Pending explicit verification |
| Incorrect password returns 401 | Pending verification |
| Unknown email receives the same authentication error | Pending verification |
| Modified token is rejected | Pending verification |
| Expired token is rejected | Pending verification |
| Inactive user is rejected | Pending verification |
| Automated authentication regression checks | Not implemented |

JWTs are signed, not encrypted. They identify the user; they do not grant tenant permissions. Login rate limiting, refresh tokens, individual-token revocation, account recovery, MFA, and deployment hardening remain pending. Keep the current implementation local.

## Logging

Application logs currently go to the console and include lifecycle events and HTTP method, route template, status, duration, and a generated request ID. Completed responses include `X-Request-ID`.

Do not deliberately log credentials, authorization headers, customer message bodies, documents, or full settings objects. SQLAlchemy parameter hiding is enabled. Unexpected exceptions currently include tracebacks; comprehensive redaction is not yet implemented, so use synthetic data and review logs before sharing them.

Future work includes authenticated tenant context, correlation with agent runs, structured JSON output, and redaction. LangSmith tracing must follow the same data-handling rules before external tracing is enabled.

## V1 milestones and checkpoints

Status is maintained manually. Update the checkboxes and development log in the same pull request as the corresponding implementation. A milestone is complete only after its acceptance checkpoints pass.

| ID | Milestone | Tentative technology | Acceptance checkpoint | Status |
| --- | --- | --- | --- | --- |
| M1 | Application foundation | Python, FastAPI, Uvicorn, Pydantic Settings, Python logging | Health/docs work; settings validate; request logs exist | Complete per maintainer |
| M2 | Persistence, identity, and tenant boundaries | SQLite, SQLAlchemy, Alembic, PyJWT, pwdlib/Argon2 | Migrations reproduce schema; two tenants seeded; unauthorized cross-tenant/customer requests rejected | In progress |
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
- [x] Model base, tenant model, and initial migration verification.
- [x] Idempotent development seed script for two demo tenants.
- [x] User identity and tenant membership models.
- [x] Database constraints for unique memberships and allowed roles.
- [x] User/membership migration applied and verified.
- [x] Password hashing and verification using pwdlib with Argon2.
- [x] Development-only admin creation with hidden password prompts.
- [x] Demo admin accounts and memberships verified.
- [x] Login and short-lived JWT access tokens.
- [x] Protected authenticated-user endpoint.
- [x] Successful login and current-user lookup manually verified.
- [x] Automated authentication regression tests for the currently covered scenarios
- [x] Active tenant membership validation for protected tenant endpoints.
- [x] Protected tenant membership endpoint.
- [x] Cross-tenant membership rejection tests in both directions.
- [x] Unknown-tenant and missing-authentication tests.
- [x] Disabled-user, disabled-tenant, and disabled-membership access tests.
- [x] Current automated test suite passes.
- [ ] Expired-token and additional JWT validation tests.
- [ ] Automated migration verification.
- [ ] Tenant/customer authorization checks with negative tests.
- [ ] Role permission enforcement.
- [ ] Customer identity mapping and resource-level ownership checks.
- [ ] Tenant-scoped authorization for conversations, tickets, documents, and tools.
- [ ] Disabled-user, disabled-tenant, and disabled-membership access checks.

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

M2 remains in progress until tenant authorization and its negative tests pass.

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
| 2026-10-25 | Added tenant seeding, user/membership models and migrations, Argon2 password utilities, and interactive development admin creation | Migration checks passed; tenant seeding repeated without duplicates; password checks and admin membership inspection passed | Implement login, JWT access tokens, and protected endpoints |
| 2026-10-26 | Added validated JWT configuration, login, and protected current-user endpoint; authentication savepoint pushed to Git | Successful POST `/auth/login` and authorized GET `/auth/me` manually verified; negative scenarios remain pending | Add active tenant membership validation, tenant endpoints, and authorization tests |
| 2026-10-26 | Added verified tenant context, protected membership endpoint, and isolated authentication/tenant-access tests | Manual tenant boundary checks passed; current pytest suite passed, including cross-tenant rejection and disabled-access scenarios | Implement role-specific authorization and extend negative tests |

For each future change, add a row with the date, concrete behavior implemented, checks performed, and next action. Replace pending items only after verification; record failures and limitations honestly.

## Automated tests

Install development dependencies from `backend`:

    python -m pip install -r requirements-dev.txt

Run the suite:

    python -m pytest -v

Uvicorn does not need to be running. FastAPI's TestClient invokes the
application directly.

Each test uses a fresh temporary SQLite database with synthetic tenants,
users, and memberships. The database dependency is overridden; real
password verification, JWT validation, and tenant authorization still run.

Test configuration uses a synthetic signing secret. Development database
records and credentials are not used.

### Verified coverage

- Successful login followed by authenticated identity lookup.
- User response excludes password hashes and unexpected fields.
- Incorrect passwords and unknown accounts receive the same error response.
- Invalid Bearer tokens are rejected.
- Missing authentication is rejected on the tenant endpoint.
- Both demo users can access their own tenant membership.
- Cross-tenant access is rejected in both directions.
- Unknown tenant access is rejected.
- Previously issued tokens cannot bypass a disabled user, tenant, or membership.

The current suite passes.

These tests create disposable schemas from SQLAlchemy metadata. They do not
verify Alembic migrations. Expired-token tests, broader JWT validation tests,
role permissions, and resource-level isolation tests remain pending.

## Current limitations

- Early local-development implementation, not a deployed SaaS service.

- No customer-facing agent, chat UI, knowledge ingestion, or tool execution yet.

- User identities, tenant memberships, and password hashing are implemented.

- JWT login and current-user authentication are implemented; 
- Tenant membership authorization is implemented for the membership endpoint.
- Role-specific permissions and customer/resource-level authorization remain pending.
- Passing tests cover the implemented endpoints; they do not establish application-wide tenant isolation or production readiness.
- No login rate limiting, refresh tokens, or individual-token revocation yet.

- Membership records and role constraints do not themselves enforce tenant isolation.

- No password reset, email verification, MFA, or account recovery flow exists yet.

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
- [pwdlib](https://frankie567.github.io/pwdlib/)
- [PyJWT](https://pyjwt.readthedocs.io/)


