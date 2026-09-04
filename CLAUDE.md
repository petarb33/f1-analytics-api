# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`f1-analytics-api` is a FastAPI REST API that wraps the [FastF1](https://github.com/theOehrly/Fast-F1) telemetry library to browse F1 seasons/races/sessions and generate cached, dark-themed matplotlib/seaborn charts (overtakes, sector times, race pace, strategy, gap-to-pole, lap-time consistency, etc.).

## Commands

- Install dependencies: `uv sync`
- Apply DB migrations: `uv run alembic upgrade head`
- Create a migration: `uv run alembic revision --autogenerate -m "description"`
- Run dev server: `uv run uvicorn app.main:app --reload` (docs at `/docs`, ReDoc at `/redoc`, API under `/api/v1`)
- Lint/format: `uv run ruff check --fix .` and `uv run ruff format .` (or `uv run pre-commit run --all-files` for the full hook set)

There is no test suite in this repo (no pytest dependency, no `tests/` directory — only a scratch `test.ipynb` notebook). Don't invent test commands; if you add tests, set up pytest first.

## Environment

Config is loaded from a root `.env` file via `pydantic-settings` (`app/core/config.py`). Required vars: `DATABASE_URL` (Postgres connection string), `SECRET_KEY` (JWT signing secret). `.env` is gitignored — never print or commit its contents.

## Architecture

- **Routing & auth**: `app/api/routes/__init__.py` aggregates three routers: `season` and `auth` are open, `analysis` is gated with `dependencies=[Depends(get_current_user)]` at the *router* level (not per-endpoint) — so any new route added under the `analysis` router is auth-protected automatically. The `analysis` router shares the path prefix `/analysis/{year}/{round_number}/{session}`.
- **Global error handling** (`app/main.py`): three exception handlers registered on the app instance — `pydantic.ValidationError` → 422 (`{"detail": exc.errors()}`), custom `AnalysisDataError` (`app/core/exceptions.py`, raised when a session has no usable data) → 404, catch-all `Exception` → logged via structlog + generic 500. New endpoints should raise/rely on these instead of building ad hoc error responses.
- **Param validation**: request/query params are validated via Pydantic classes injected with `Depends()` rather than inline checks — see `app/schemas/session.py` (`SessionParameters`, `RaceSessionParameters`, `QualifyingSessionParameters`, which enforce session-type applicability) and `app/schemas/options.py` (`GroupOptions`, `DisplayOptions`, `BasisOptions`, `LapModeOptions`).
- **Analysis/plotting pipeline**: template-method pattern via the `BaseAnalysis` ABC (`app/services/plots/core/base.py`). `run()` orchestrates: check cache (`get_image(cache_key)`) → on miss, `load()` (fetch FastF1 session data) → `process()` (optional override) → `plot()` (abstract, must override) → `plt.close("all")`. Concrete chart types live in `app/services/plots/analyzers/` (one class per chart), data-shaping helpers in `app/services/plots/processing/`, shared styling/F1 colors in `app/services/plots/plotting/`. `app/services/analyze.py` exposes `run_*` functions consumed directly by route handlers.
- **Chart caching**: rendered charts are cached as bytes in Postgres (`app/models/image.py`, `Image` table), keyed by a unique `filename` derived from year/round/session/analysis-type/options. `save_image()` catches the `IntegrityError` from the unique constraint to safely handle concurrent duplicate first-render requests — don't remove this without preserving that race handling.
- **Layout**: `app/api/routes` (endpoints) · `app/core` (config, security/JWT, `get_current_user` dependency, logging, exceptions) · `app/database` (SQLAlchemy engine/session/`Base`, `get_db()`) · `app/models` (`Users`, `Image`) · `app/schemas` (Pydantic validation) · `app/services` (business logic, with the `plots/` subpackage for the analysis pipeline).
- **Logging**: `structlog`, configured once via `configure_logging()` in `app/main.py` at startup; JSON output, ISO timestamps.
