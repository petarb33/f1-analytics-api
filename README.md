# f1-analytics-api :checkered_flag:
[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=FastAPI&labelColor=555&logoColor=white)](https://fastapi.tiangolo.com/)
![RestAPI](https://img.shields.io/badge/API-REST-violet)
[![FastF1](https://img.shields.io/badge/FastF1-api-red)](https://docs.fastf1.dev/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?logo=python&logoColor=white)](https://matplotlib.org/)
[![Seaborn](https://img.shields.io/badge/Seaborn-4c72b0?logoColor=white)](https://seaborn.pydata.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)


---

A REST API for exploring Formula 1 seasons and sessions, and generating cached, styled race analysis charts — powered by [FastF1](https://docs.fastf1.dev/).

## 1. Overview

`f1-analytics-api` wraps the [FastF1](https://docs.fastf1.dev/) telemetry library behind a REST API. It lets clients:

- Browse seasons, completed races, and completed sessions.
- Generate styled visualizations from real session data:
  - **Overtakes** — driver position over the course of a race.
  - **Sector times** — fastest sector comparison by driver or team, either the theoretical best (fastest time in each sector independently) or taken from a single fastest lap, shown as absolute times or deltas to the fastest.
  - **Race pace** — lap time distribution (box plot) by driver or team, with in/out and safety-car-affected laps excluded.
  - **Strategy** — tyre stint timeline per driver, with Safety Car / Virtual Safety Car / Red Flag periods marked per driver (accounting for track position — a leader and a lapped car aren't necessarily on the same lap number when a stoppage starts).
- Register and log in via JWT-based authentication.

Overtakes, race pace, and strategy are only meaningful for full-distance sessions, so those endpoints are restricted to Race and Sprint sessions; sector comparisons remain available for any completed session.

Generated charts are rendered server-side (matplotlib/seaborn, dark themed, using official F1 driver/team/compound colors) and cached in PostgreSQL, keyed by season/round/session/analysis type/options, so repeat requests skip recomputation instead of reloading and reprocessing telemetry every time.

## 2. Tech Stack

| Layer            | Technology                                                        |
| ---------------- | ------------------------------------------------------------------ |
| Web framework    | [FastAPI](https://fastapi.tiangolo.com/)                           |
| F1 data source   | [FastF1](https://docs.fastf1.dev/)                                 |
| Database         | [PostgreSQL](https://www.postgresql.org/)                                                         |
| ORM / migrations | [SQLAlchemy](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/) |
| Auth             | [python-jose](https://github.com/mpdavis/python-jose) (JWT) + [passlib](https://passlib.readthedocs.io/)/bcrypt |
| Validation       | [Pydantic](https://docs.pydantic.dev/) / pydantic-settings          |
| Charting         | [matplotlib](https://matplotlib.org/), [seaborn](https://seaborn.pydata.org/)                                                |
| Dependency mgmt  | [uv](https://docs.astral.sh/uv/)                                    |

## 3. Project Structure

```
app/
├── api/
│   └── routes/
│       ├── auth.py            # register / login / me
│       ├── season.py          # seasons, races, sessions
│       └── analysis.py        # chart-generating endpoints
├── core/
│   ├── config.py               # Settings (env-driven)
│   ├── security.py             # password hashing, JWT
│   └── dependencies.py          # get_db, get_current_user
├── database/
│   └── db.py                   # SQLAlchemy engine/session
├── models/
│   ├── user.py                  # Users table
│   └── image.py                  # Images table + save/get helpers
├── schemas/
│   ├── user.py                    # auth request/response models
│   ├── session.py                  # season/round/session validation (incl. race-only sessions)
│   └── options.py                   # chart query options (group, display, basis)
└── services/
    ├── auth.py                       # user auth logic
    ├── fetch.py                       # FastF1 schedule/session lookups
    ├── constants.py                    # season range, session mapping, race sessions, track status colors
    ├── analyze.py                       # analysis orchestration
    └── plots/
        ├── core/
        │   └── base.py                    # BaseAnalysis: load/process/plot/cache template
        ├── analyzers/
        │   ├── overtakes.py                # position-by-lap chart
        │   ├── sector_times.py               # fastest sector comparison (driver/team)
        │   ├── race_pace.py                   # lap time distribution box plot (driver/team)
        │   └── strategy.py                     # tyre stint timeline + SC/VSC/RF markers
        ├── processing/
        │   ├── sector_times.py                # sector time data shaping
        │   ├── race_pace.py                    # lap time filtering/shaping for box plots
        │   ├── strategy.py                      # stint length aggregation
        │   └── track_status.py                   # per-driver SC/VSC/Red Flag lap detection
        └── plotting/
            ├── f1_colors.py                     # driver/team/compound color mappings
            └── plot_styles.py                     # shared dark-theme styling helpers

alembic/                # migrations
```

## 4. Installation

### Prerequisites

- Python 3.12+
- PostgreSQL
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup

```bash
# 1. Install dependencies
uv sync

# 2. Create a .env file in the project root (see table below for required variables)

# 3. Run database migrations
uv run alembic upgrade head

# 4. Start the dev server
uv run uvicorn app.main:app --reload
```

### Environment variables

| Variable       | Description                                  | Example                                              |
| -------------- | --------------------------------------------- | ----------------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection string                  | `postgresql://user:password@localhost:5432/f1_db`      |
| `SECRET_KEY`   | Secret used to sign JWT access tokens          | a long, random string — never commit a real value       |

## 5. Usage

Once running, the API is served under `/api/v1`. Interactive docs (Swagger UI) are available at `/docs`, and ReDoc at `/redoc`.

### Authentication flow

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Log in (form-encoded, OAuth2 password flow)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=you@example.com&password=yourpassword"
# -> { "access_token": "...", "token_type": "bearer" }

# Use the token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Browsing season data

```bash
curl http://localhost:8000/api/v1/season
curl http://localhost:8000/api/v1/season/2024/races
curl http://localhost:8000/api/v1/season/2024/5/sessions
```

### Generating a chart

Chart endpoints return raw `image/png` bytes (not JSON) — point a browser or `<img>` tag directly at the URL, or save the response to a file:

```bash
# Overtakes (Race/Sprint only)
curl http://localhost:8000/api/v1/analysis/2024/5/R/overtakes -o overtakes.png

# Sector times — any completed session, with options
curl "http://localhost:8000/api/v1/analysis/2024/5/R/sectors?group=drivers&display=delta&basis=fastest_lap" -o sectors.png

# Race pace box plot (Race/Sprint only)
curl "http://localhost:8000/api/v1/analysis/2024/5/R/racepace?group=teams" -o racepace.png

# Strategy, with SC/VSC/Red Flag markers (Race/Sprint only)
curl http://localhost:8000/api/v1/analysis/2024/5/R/strategy -o strategy.png
```

## API Endpoints

| Method | Endpoint                                                       | Description                                     | Auth |
| ------ | ---------------------------------------------------------------- | ------------------------------------------------- | :--: |
| POST   | `/api/v1/auth/register`                                           | Register a new user                                |      |
| POST   | `/api/v1/auth/login`                                               | Log in, returns a JWT access token                  |      |
| GET    | `/api/v1/auth/me`                                                   | Get the current authenticated user                   |  ✅  |
| GET    | `/api/v1/season`                                                     | List available seasons                                |      |
| GET    | `/api/v1/season/{year}/races`                                         | List completed races for a season                       |      |
| GET    | `/api/v1/season/{year}/{round_number}/sessions`                        | List completed sessions for a race round                  |      |
| GET    | `/api/v1/analysis/{year}/{round_number}/{session}/overtakes`            | Driver position/overtakes chart (PNG) — Race/Sprint only        |      |
| GET    | `/api/v1/analysis/{year}/{round_number}/{session}/sectors?group={drivers\|teams}&display={absolute\|delta}&basis={theoretical\|fastest_lap}` | Sector time comparison chart (PNG) — any completed session |      |
| GET    | `/api/v1/analysis/{year}/{round_number}/{session}/racepace?group={drivers\|teams}` | Lap time distribution box plot (PNG) — Race/Sprint only |      |
| GET    | `/api/v1/analysis/{year}/{round_number}/{session}/strategy`             | Tyre strategy chart with SC/VSC/Red Flag markers (PNG) — Race/Sprint only |      |

> Note: chart generation results are cached in PostgreSQL — the first request for a given season/round/session/analysis/options combination computes and stores the image; subsequent requests for the same combination are served from the cache.
