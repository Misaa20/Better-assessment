# FairSplit — Group Expense Splitter

A small, well structured expense splitting application built as an assessment project. Deliberately minimal in scope 3 core entities, rich domain logic, thorough validation, and automated tests.

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python run.py
```

The API runs at `http://localhost:5001`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` (or next available port) and proxies API calls to the backend.

### Run Tests

```bash
cd backend
.\venv\Scripts\activate    # or source venv/bin/activate
python -m pytest tests/ -v --tb=short
```

## Architecture

```
┌─────────────────────────────────┐    ┌────────────────────────┐
│         React Frontend          │    │    Flask Backend        │
│                                 │    │                        │
│  Pages → Hooks → API Client  ───┼──→│  Routes → Schemas      │
│  Components (presentational)    │    │      → Services        │
│  Types (mirror backend)         │    │      → Models → SQLite │
└─────────────────────────────────┘    └────────────────────────┘
```

### Backend Layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Routes** | `app/api/` | Parse HTTP requests, call services, return JSON. No business logic. |
| **Schemas** | `app/schemas/` | Validate input, serialize output. First line of defense against bad data. |
| **Services** | `app/services/` | All business logic. Framework-agnostic (no Flask imports). Testable in isolation. |
| **Models** | `app/models/` | SQLAlchemy models with DB-level constraints (CHECK, UNIQUE). Last line of defense. |
| **Errors** | `app/errors.py` | Typed domain exceptions with error codes. Never generic 400s. |

### Frontend Structure

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **API Client** | `src/api/` | Typed Axios wrapper. Single source of truth for all HTTP calls. |
| **Types** | `src/types/` | TypeScript interfaces mirroring backend schemas. |
| **Hooks** | `src/hooks/` | `useApi` generic hook for data fetching with loading/error states. |
| **Pages** | `src/pages/` | Route-level components that compose hooks and presentational components. |
| **Components** | `src/components/` | Reusable UI. Receive data via props; never call API directly. |

## Key Technical Decisions

| Decision | Why | Tradeoff |
|----------|-----|----------|
| **SQLite** | Zero-config, single-file, perfect for demo. No external DB server needed. | No concurrent write safety. Would use PostgreSQL in production. |
| **Marshmallow schemas** | Declarative validation at API boundary. Catches bad data before it reaches services. | Extra layer of code vs. inline validation. Worth it for interface safety. |
| **Service layer pattern** | Isolates domain logic from HTTP. Services are testable without Flask, reusable. | More files for a small app. Pays off in change resilience. |
| **Domain exception hierarchy** | Typed errors (`InvalidSplit`, `InsufficientBalance`) produce clear API responses with error codes. | Slight overhead for a small domain. Enables precise error handling. |
| **Defense in depth** | Validation at schema level, service level, AND database constraints. | Redundant checks. Intentional — each layer catches what the one above misses. |
| **Structured logging + request IDs** | Every request gets a UUID. Logs include request context for traceability. | Log noise in development. Critical for diagnosing production issues. |
| **Tailwind CSS** | Rapid, consistent styling without custom CSS files. Utility-first = predictable. | Verbose class names. Acceptable for this scope. |
| **Vite proxy** | Frontend dev server proxies `/api` to Flask. No CORS issues in dev, mirrors production. | Dev-only config. Production would use nginx or similar. |

## Domain Rules Enforced

1. Expense split amounts must sum to the expense total (tolerance: $0.01)
2. Percentage splits must sum to exactly 100%
3. Settlement amount cannot exceed the outstanding balance
4. Cannot settle with yourself
5. Cannot add expenses for non-group members
6. Cannot delete a group with unsettled balances
7. Voided expenses are excluded from balance calculations
8. All balances are zero-sum (invariant verified in tests)

## Testing Strategy

- **45 tests** covering unit and integration levels
- **Unit tests**: Pure function tests for split calculations, balance computation, debt simplification, settlement validation rules
- **Integration tests**: Full HTTP request → response cycle testing happy paths and error cases
- **Fixtures**: `sample_group` provides consistent 3-member test data

## Observability Features

- **Activity log**: Every domain action (group created, expense added, settlement made, expense voided, member added) is recorded to an `activities` table and surfaced in the UI as a timestamped feed
- **Request ID tracing**: Every HTTP request is tagged with a UUID, propagated through logs for end-to-end traceability
- **Structured logging**: All service-layer actions logged with context (amounts, member IDs, group IDs)
- **Group stats**: Real-time computed summary — total spent, expense count, per-member share breakdown

## What I'd Change in Production

- **PostgreSQL** for concurrent writes and richer constraint support
- **User authentication** with JWT or session-based auth
- **Decimal type** instead of float for monetary amounts (avoids IEEE 754 issues)
- **Pagination** on list endpoints
- **WebSocket** for real-time balance updates when another member adds an expense
- **CI/CD pipeline** with automated test runs on every PR
- **Rate limiting** on API endpoints

## AI Guidance Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Architecture rules, domain invariants with test mappings, verification checklist, safety boundaries, change impact analysis |
| `CLAUDE.md` | Project context for Claude — structure, key commands, critical files, conventions |
| `.cursor/rules/project.mdc` | Cross-cutting coding standards (Python + TypeScript) |
| `.cursor/rules/backend.mdc` | Backend-specific rules — layer boundaries, DB conventions, error handling, testing |
| `.cursor/rules/frontend.mdc` | Frontend-specific rules — component architecture, design system, type safety |

## AI Usage

- AI was used extensively for code generation (Cursor with Claude)
- All generated code was critically reviewed for correctness, especially:
  - Balance computation algorithm (zero-sum invariant)
  - Rounding behavior in split strategies (remainder assignment)
  - Settlement validation logic (cap enforcement, direction checks)
- `AGENTS.md` includes a verification checklist AI must complete before considering a change done
- `CLAUDE.md` provides quick project context so AI doesn't need to re-explore the codebase each session
- `.cursor/rules/` files enforce conventions at the file level — backend rules can't leak into frontend rules
