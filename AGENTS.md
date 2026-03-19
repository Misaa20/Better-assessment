# AGENTS.md — AI Agent Constraints for FairSplit

This file defines rules, invariants, and constraints that any AI coding agent
must follow when working on this codebase. Violations of MUST rules should be
treated as bugs.

---

## Architecture Rules

### Backend — Layered Architecture (MUST follow)

```
API Routes (app/api/)          ← HTTP concerns only
     ↓
Schemas (app/schemas/)         ← Boundary validation
     ↓
Services (app/services/)       ← Domain logic (framework-agnostic)
     ↓
Models (app/models/)           ← Data structure + DB constraints
```

**Layer rules:**

| Rule | Rationale |
|------|-----------|
| Route handlers MUST NOT contain business logic | Keeps controllers thin; logic is testable without Flask |
| Services MUST NOT import Flask (`request`, `g`, `abort`) | Services must be framework-agnostic for testability |
| Models MUST NOT contain business logic | Models define structure; services define behavior |
| Schemas validate at the boundary; services validate domain rules | Defense in depth — each layer catches what the one above misses |

### Frontend — Component Architecture

```
API Client (src/api/)          ← Single source of truth for HTTP
     ↓
Hooks (src/hooks/)             ← Data fetching + state
     ↓
Pages (src/pages/)             ← Route-level composition
     ↓
Components (src/components/)   ← Presentational, props-driven
```

**Rules:**
- Components MUST NOT call the API directly. Data comes via props.
- All HTTP calls go through `src/api/client.ts`.
- TypeScript types in `src/types/` MUST mirror backend schema shapes.
- Utilities live in `src/utils/` and must be pure functions.

---

## Domain Invariants (MUST NOT be violated)

These are the core correctness properties of the system. Every invariant has
at least one test. If you change code that touches an invariant, run the
related tests before committing.

| # | Invariant | Enforcement | Test file |
|---|-----------|-------------|-----------|
| 1 | Sum of all member balances in a group = 0 | `balance_service.compute_balances` | `test_balance_service.py::test_zero_sum_invariant` |
| 2 | Split amounts must sum to expense total (±0.01) | Schema + `expense_service.create_expense` | `test_split_strategies.py` |
| 3 | Percentage splits must sum to 100 | `ExpenseCreateSchema.validate_splits` | `test_split_strategies.py::TestPercentageSplit` |
| 4 | Expense members must belong to the group | `expense_service._validate_members_in_group` | `test_api.py::test_rejects_nonmember_payer` |
| 5 | Settlement ≤ min(payer debt, payee credit) | `settlement_service.create_settlement` | `test_settlement_rules.py::test_rejects_overpayment` |
| 6 | paid_by ≠ paid_to in settlements | DB CHECK constraint | `models/settlement.py` |
| 7 | Voided expenses excluded from balances | `balance_service` filters by STATUS_ACTIVE | `test_balance_service.py::test_voided_expenses_excluded` |
| 8 | Cannot delete group with unsettled balances | `group_service.delete_group` | `test_api.py::test_delete_group_with_zero_balances` |

---

## Verification Checklist

Before any change is considered complete, verify:

- [ ] `python -m pytest tests/ -v` — all 45 tests pass
- [ ] `npx tsc --noEmit` — no TypeScript errors in frontend
- [ ] New domain logic has at least one unit test
- [ ] New API endpoints have at least one integration test
- [ ] Error cases return typed domain exceptions, not generic 500s
- [ ] No `any` types introduced in TypeScript
- [ ] No bare `except:` introduced in Python

---

## Safety Boundaries

### What AI agents MUST NOT do

- **Do NOT modify domain invariant logic** without running the full test suite
- **Do NOT add new dependencies** without explicit justification
- **Do NOT bypass schema validation** by passing raw data to services
- **Do NOT catch and swallow exceptions** — always log with context
- **Do NOT add authentication** — out of scope, would change every layer
- **Do NOT use raw SQL** — use SQLAlchemy ORM exclusively
- **Do NOT put UI logic in API responses** — keep backend data-oriented

### What AI agents SHOULD do

- Run tests after every change
- Use typed domain exceptions for error cases
- Keep functions under 30 lines; extract helpers
- Mirror backend validation in frontend forms
- Use early returns over deep nesting

---

## Change Impact Analysis

When modifying a file, check this table to understand downstream effects:

| If you change... | Also check... |
|------------------|---------------|
| `models/*.py` | Schemas, services, migrations, all tests |
| `schemas/*.py` | API routes, frontend types |
| `services/balance_service.py` | `settlement_service.py`, all balance tests |
| `services/expense_service.py` | Balance computation, expense API tests |
| `errors.py` | Error handlers in `__init__.py`, integration tests |
| `src/types/index.ts` | API client, all components using those types |
| `src/api/client.ts` | All hooks and pages that call the API |

---

## Error Handling

- Domain errors use the hierarchy in `app/errors.py`
- Every error has a unique `error_code` string for client-side handling
- Route-level errors return `{"error": "...", "code": "..."}` JSON
- Unexpected errors are logged with request ID for traceability
- Frontend displays error messages from `error` field in API responses

---

## Code Style

- Python: snake_case functions/variables, PascalCase classes, type hints on all signatures
- TypeScript: camelCase functions/variables, PascalCase components/types/interfaces
- Comments explain *why*, never *what* — code should be self-documenting
- Monetary values: always round to 2 decimal places, use tolerance of 0.01 for comparisons

---

## Coding Standards (used as IDE-level rules during development)

### General (Python + TypeScript)

- Use type hints on all function signatures (Python) and strict types (TypeScript).
- Service functions accept primitive types, not framework request objects.
- All amounts are floats rounded to 2 decimal places at computation boundaries.
- `db.session.commit()` only in service functions, never in models or routes.
- Domain errors must use the exception hierarchy in `app/errors.py`.
- Every new service function must have a corresponding test.
- All API response types live in `src/types/index.ts`, kept in sync with backend schemas.
- Use `useApi` hook for data fetching; do not use raw `useEffect` + `fetch`.
- No `any` types. Use `unknown` and narrow with type guards.
- No bare `except:`. Always catch specific exceptions.
- Keep functions under 30 lines. Extract named helpers if longer.

### Backend-Specific

- `app/api/` files: ONLY parse request, call service, return response.
- `app/services/` files: MUST NOT import from Flask. Testable without app context.
- `app/models/` files: Define schema and relationships only. No business logic methods.
- Always use SQLAlchemy ORM. No raw SQL.
- Add CHECK constraints for data integrity (positive amounts, valid enums).
- Raise domain exceptions from `app/errors.py`, never `abort()` from services.

### Frontend-Specific

- Pages compose hooks and components. Components are presentational (props-driven).
- Components must never import from `src/api/`. Only pages and hooks call the API.
- Tailwind utility classes exclusively. No custom CSS files.
- Design tokens: gray-900 primary text, gray-500 secondary, gray-50 page background.
- Cards: `rounded-lg border border-gray-200 bg-white`. No heavy shadows or gradients.
- Keep styling restrained — no decorative elements that don't serve function.
