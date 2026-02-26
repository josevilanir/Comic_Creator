# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Minimal code impact.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Only touch what's necessary. Avoid introducing side-effects.

## Workflow

### Plan Before Acting

- Enter plan mode for any non-trivial task (3+ steps or architectural decisions).
- Write plan to `tasks/todo.md` with checkable items, then check in before starting implementation.
- If something goes sideways, stop and re-plan immediately — don't keep pushing.

### Subagent Strategy

- Offload research, exploration, and parallel analysis to subagents to keep the main context window clean.
- One focused task per subagent.

### Self-Improvement Loop

- After any correction from the user, update `tasks/lessons.md` with the pattern.
- Write rules that prevent the same mistake from recurring. Review lessons at session start.

### Verification Before Done

- Never mark a task complete without proving it works: run tests, check logs, demonstrate correctness.
- Mark items complete in `tasks/todo.md` as you go, and add a result summary when finished.
- Ask: "Would a staff engineer approve this?"

### Elegance Check

- For non-trivial changes, pause and ask: "Is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution."
- Skip for simple, obvious fixes.

### Autonomous Bug Fixing

- When given a bug report, just fix it. Point at logs/errors/failing tests, then resolve them.
- Go fix failing tests without being told how.

## Project Overview

Comic Creator is a fullstack app for downloading, organizing, and reading manga/comics. It has multi-user JWT authentication with per-user libraries and reading progress.

- **Backend**: Flask (Python 3.10+) on port 5000
- **Frontend**: React 18 + Vite on port 5173
- **Database**: SQLite (`data/comic_creator.db`) for users/URLs/progress; filesystem for manga files
- **Comics storage**: `~/Comics/<username>/` by default (configurable via `BASE_COMICS` env var)

## Commands

### Backend

```bash
# Setup (first time)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # testes e ferramentas de dev
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" > .env

# Desenvolvimento
python main.py

# Produção (Gunicorn)
FLASK_ENV=production gunicorn "main:app" --config gunicorn.conf.py

# Tests — note: actual test dir is Tests/ (uppercase), not tests/
pytest Tests/ -v
pytest Tests/unit/ -v -m unit
pytest Tests/integration/ -v -m integration
pytest Tests/ --cov=src --cov-report=term   # with coverage

# Run a single test file
pytest Tests/unit/presentation/test_api_v1.py -v
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # configure VITE_API_URL if backend runs on different port

npm run dev            # dev server on port 5173
npm run build          # production build to frontend/dist/
npm run preview        # preview production build
```

## Architecture

### Backend: Clean Architecture

```
Request → Presentation → Application (Use Cases) → Domain ← Infrastructure
```

- **`src/domain/`** — entities (`Manga`, `Capitulo`, `User`, `URLSalva`), repository interfaces (`interfaces.py`), domain exceptions
- **`src/application/use_cases/`** — business logic: `BaixarCapituloUseCase`, `LoginUserUseCase`, `RegisterUserUseCase`, `RefreshTokenUseCase`, `LogoutUserUseCase`
- **`src/infrastructure/`** — concrete implementations: filesystem repos for manga/chapters, SQLite repos for users/URLs/progress, `JwtService`, `ImageDownloadService`, `PDFGeneratorService`, `ThumbnailService`
- **`src/presentation/`** — Flask blueprints, API routes, controllers, middlewares
- **`config/dependencies.py`** — `DependencyContainer` wires all dependencies; accessed via `current_app.container` in routes

### Multi-User Isolation

All repository methods accept `user_id` as the first argument. The `@auth_required` decorator (in `src/presentation/decorators/auth_required.py`) validates the JWT and sets `g.user_id` and `g.username` on the Flask request context. Manga/chapters are stored at `~/Comics/<username>/`.

### API Design

- All REST endpoints are under `/api/v1/` (blueprints: `api_bp`, `auth_api_bp`, `progresso_bp`)
- Responses follow **JSend** format (`src/presentation/api/jsend.py`):
  - `{"status": "success", "data": ...}` — 2xx
  - `{"status": "fail", "data": {...}}` — 4xx (client error / validation)
  - `{"status": "error", "message": ..., "code": ...}` — 5xx (server error)
- Legacy `/api/*` routes (without `v1`) are kept as 308 redirects for backward compatibility and should eventually be removed

### Auth Flow

- JWT with two token types: `access` (short-lived) and `refresh` (long-lived, stored in SQLite)
- `JWT_SECRET_KEY` must be set in `.env` for production
- Image endpoints (e.g., `/manga/<name>/capa`, `/capitulo/<name>/<file>`) support both `Authorization: Bearer <token>` header and `?token=<token>` query param so `<img src>` tags can load authenticated resources

### Frontend Architecture

- **`frontend/src/services/api.js`** — Axios instance with auto-refresh interceptor (queues failed requests during token refresh)
- **`frontend/src/contexts/AuthContext.jsx`** — global auth state; tokens stored in `localStorage`; `queryClient.clear()` is called on login/logout to invalidate React Query cache
- **`frontend/src/hooks/`** — custom hooks for data fetching (`useLibrary`, `useChapters`, `useDownload`, `useUrls`, `useProgresso`)
- **`frontend/src/features/`** — page-level feature components: `library/`, `downloader/`, `reader/`, `landing/`
- **`frontend/src/components/`** — shared/reusable: `ui/` (Button, Alert, ProgressBar), `shared/` (MangaCard, Pagination), `PrivateRoute`
- React Query v5 (`@tanstack/react-query`) manages server state caching

### Range Downloads

Async downloads of chapter ranges run in background threads (`threading.Thread`). Jobs are tracked in an in-memory dict (`_download_jobs` in `routes.py`) with a lock. Frontend polls `/api/v1/download/progresso/<job_id>` for status.

## Environment Variables

### Backend (`.env` in project root)
| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | — | **Required** for JWT signing |
| `FLASK_ENV` | `development` | `development`, `testing`, or `production` |
| `BASE_COMICS` | `~/Comics` | Root directory for manga files |
| `SECRET_KEY` | dev default | Flask session secret |

### Frontend (`frontend/.env`)
| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:5000` | Backend base URL |

## Known Issues / TODOs

- `pytest.ini` has `testpaths = tests` (lowercase) but actual directory is `Tests/` (uppercase) — always specify `pytest Tests/` explicitly
- `BaixarCapituloUseCase` has inline TODO about the `user_id` parameter pattern
- `/api/v1/auth/me` uses a workaround pattern to apply `@auth_required` — there are two separate auth middleware implementations (`src/presentation/decorators/auth_required.py` and `src/presentation/middlewares/auth_required.py`)
- Legacy compat routes in `app.py` (308 redirects) should be removed once all clients migrate to `/api/v1`
