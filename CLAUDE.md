# CLAUDE.md — Project Context for Claude

## What is this?

FairSplit is a group expense splitting app. Users create groups, add expenses
with different split strategies (equal, exact, percentage), view computed
balances, and settle debts. Built as a technical assessment demonstrating
architecture over feature count.

## Stack

- **Backend**: Python 3.14, Flask 3.1, SQLAlchemy, Marshmallow, SQLite
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS v3, Axios
- **Testing**: pytest (45 tests, 90%+ coverage)

## Project Structure

```
backend/
  app/
    api/         → Flask Blueprint route handlers (thin controllers)
    schemas/     → Marshmallow request/response validation
    services/    → Business logic (framework-agnostic, testable)
    models/      → SQLAlchemy models with DB constraints
    errors.py    → Typed domain exception hierarchy
    __init__.py  → App factory, middleware, error handlers
  tests/
    unit/        → Pure logic tests (splits, balances, settlements)
    integration/ → Full HTTP request/response tests
  run.py         → Entry point (port 5001)

frontend/
  src/
    api/         → Typed Axios client
    components/  → Presentational UI components
    pages/       → Route-level page components
    hooks/       → useApi generic data-fetching hook
    types/       → TypeScript interfaces (mirror backend schemas)
    utils/       → Pure utility functions
```

## Key Commands

```bash
# Run backend
cd backend && .\venv\Scripts\activate && python run.py

# Run frontend
cd frontend && npm run dev

# Run tests
cd backend && .\venv\Scripts\activate && python -m pytest tests/ -v

# Run tests with coverage
cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Type-check frontend
cd frontend && npx tsc --noEmit
```

## Core Domain

Three entities: Group (with Members), Expense (with Splits), Settlement.

Balance = (total paid by member) - (total owed via splits) + (settlements received) - (settlements paid)

Key constraint: sum of all balances in a group is always zero.

## Critical Files

| File | Why it matters |
|------|----------------|
| `services/balance_service.py` | Core balance computation + debt simplification algorithm |
| `services/expense_service.py` | Split strategy resolution (equal/exact/percentage) |
| `services/settlement_service.py` | Settlement validation (cap enforcement) |
| `errors.py` | Domain exception hierarchy — every error has a typed code |
| `schemas/expense.py` | Split validation at API boundary |
| `tests/unit/test_split_strategies.py` | Proves split math is correct (pure function tests) |

## Conventions

- Services are framework-agnostic (no Flask imports)
- Defense in depth: validation in schemas AND services AND DB constraints
- Monetary amounts: float, always rounded to 2 decimal places
- Comparison tolerance for money: 0.01
- Frontend components receive data via props, never call API directly
