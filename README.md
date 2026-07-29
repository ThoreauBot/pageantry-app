# Pageantry App

A pageantry management system based on *Directing Pageants: A Master Guide* by **Tamsyn J. Simon**. This application helps independent pageant directors plan, manage, execute, and follow up on pageant events — from registration and scoring through titleholder management and financial reporting.

> **Reference site:** [www.PageantDirectorResource.com](https://www.PageantDirectorResource.com)

---

## Tech Stack

| Layer      | Technology                                                     |
| ---------- | -------------------------------------------------------------- |
| Backend    | **FastAPI** (Python 3.9+) — async-capable REST framework       |
| ORM        | **SQLAlchemy 2.0** — declarative models with relationship loading |
| Database   | **SQLite** — single-file storage, zero-config                  |
| Frontend   | **Vanilla JS** — served as static files from `/static/`        |
| Server     | **Uvicorn** — ASGI server                                      |

---

## Quick Start

```bash
# 1. Clone the repo
cd pageantry-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
chmod +x run.sh
./run.sh
```

The server starts on **http://localhost:9121** and creates the SQLite database (`pageantry.db`) automatically on first run.

### Default Credentials

| Field            | Value                     |
| ---------------- | ------------------------- |
| Tenant ID        | `1`                       |
| Email            | `director@example.com`    |
| Password         | `password`                |
| Role             | `director`                |

The default tenant is created automatically when the server starts if no tenant exists. All API requests authenticate via the `X-Tenant-ID: 1` header (no JWT tokens for development).

---

## API Overview

The API is organized by domain. All endpoints are prefixed per router; the full list is available at **http://localhost:9121/docs** (auto-generated Swagger UI).

### Auth (`/auth`)
| Method | Endpoint          | Description                       |
| ------ | ----------------- | --------------------------------- |
| POST   | `/auth/register`  | Create a new tenant account       |
| POST   | `/auth/login`     | Login (email + password)          |
| GET    | `/auth/me`        | Get current tenant info           |

### Pageants (`/pageants`)
| Method | Endpoint                                    | Description                          |
| ------ | ------------------------------------------- | ------------------------------------ |
| GET    | `/pageants/`                                | List pageants for current tenant     |
| POST   | `/pageants/`                                | Create a new pageant                 |
| GET    | `/pageants/{id}`                            | Get a single pageant                 |
| PATCH  | `/pageants/{id}`                            | Update a pageant                     |
| GET    | `/pageants/{id}/branding`                   | Get pageant branding                 |
| PUT    | `/pageants/{id}/branding`                   | Create or update branding            |
| GET    | `/pageants/{id}/divisions`                  | List age divisions                   |
| POST   | `/pageants/{id}/divisions`                  | Create an age division               |
| GET    | `/pageants/{id}/divisions/{div}/categories` | List competition categories          |
| POST   | `/pageants/{id}/divisions/{div}/categories` | Create a competition category        |
| GET    | `/pageants/{id}/divisions/{div}/cat/{cat}/rubric` | Get scoring rubric           |
| PUT    | `/pageants/{id}/divisions/{div}/cat/{cat}/rubric` | Create or update rubric       |

### Contestants
| Method | Endpoint                                          | Description                       |
| ------ | ------------------------------------------------- | --------------------------------- |
| GET    | `/pageants/{id}/contestants`                      | List contestants (with filters)   |
| POST   | `/pageants/{id}/contestants`                      | Register a contestant             |
| GET    | `/contestants/{id}`                               | Get contestant detail             |
| PATCH  | `/contestants/{id}`                               | Update contestant                 |
| POST   | `/contestants/{id}/check-in`                      | Check in a contestant             |
| GET    | `/contestants/{id}/documents`                     | List contestant documents         |
| POST   | `/contestants/{id}/documents`                     | Add a document                    |
| GET    | `/contestants/{id}/fees`                          | List registration fees            |
| POST   | `/contestants/{id}/fees`                          | Add a fee                         |
| PATCH  | `/contestants/{id}/fees/{fee_id}`                 | Update fee payment status         |

### Scoring
| Method | Endpoint                                  | Description                          |
| ------ | ----------------------------------------- | ------------------------------------ |
| POST   | `/pageants/{id}/panels`                   | Create a judge panel                 |
| GET    | `/pageants/{id}/panels`                   | List judge panels                    |
| GET    | `/panels/{id}`                            | Get a judge panel                    |
| POST   | `/panels/{id}/judges`                     | Add a judge to a panel               |
| DELETE | `/panels/{id}/judges/{judge_id}`          | Remove a judge from a panel          |
| POST   | `/pageants/{id}/scores`                   | Submit a score entry                 |
| GET    | `/pageants/{id}/scores`                   | List scores (with filters)           |
| POST   | `/pageants/{id}/tabulate/{division_id}`   | Run tabulation and rank contestants  |
| GET    | `/pageants/{id}/results`                  | Get latest tabulation results        |

### Venues
| Method | Endpoint                                   | Description                       |
| ------ | ------------------------------------------ | --------------------------------- |
| GET    | `/venues`                                  | List all venues                   |
| POST   | `/venues`                                  | Create a venue                    |
| GET    | `/venues/{id}`                             | Get venue detail                  |
| PATCH  | `/venues/{id}`                             | Update a venue                    |
| GET    | `/venues/{id}/amenities`                   | List venue amenities              |
| POST   | `/venues/{id}/amenities`                   | Add an amenity                    |
| GET    | `/pageants/{id}/venue-contracts`           | List venue contracts              |
| POST   | `/pageants/{id}/venue-contracts`           | Create a venue contract           |
| PATCH  | `/venue-contracts/{contract_id}`           | Update a venue contract           |
| GET    | `/pageants/{id}/venue-layouts`             | Get venue layouts                 |
| POST   | `/pageants/{id}/venue-layouts`             | Create or update venue layout     |

### Sponsors
| Method | Endpoint                                  | Description                          |
| ------ | ----------------------------------------- | ------------------------------------ |
| GET    | `/pageants/{id}/sponsors`                 | List sponsors                        |
| POST   | `/pageants/{id}/sponsors`                 | Create a sponsor                     |
| GET    | `/sponsors/{id}`                          | Get sponsor detail                   |
| PATCH  | `/sponsors/{id}`                          | Update a sponsor                     |
| POST   | `/pageants/{id}/sponsorship-tiers`        | Create a sponsorship tier            |
| GET    | `/pageants/{id}/sponsorship-tiers`        | List sponsorship tiers               |
| POST   | `/pageants/{id}/agreements`               | Create a sponsorship agreement       |
| GET    | `/pageants/{id}/agreements`               | List sponsorship agreements          |
| POST   | `/pageants/{id}/donations`                | Record a donation                    |
| GET    | `/pageants/{id}/donations`                | List donations                       |
| POST   | `/pageants/{id}/barter`                   | Create a barter agreement            |
| GET    | `/pageants/{id}/barter`                   | List barter agreements               |

### Marketing
| Method | Endpoint                                  | Description                          |
| ------ | ----------------------------------------- | ------------------------------------ |
| GET    | `/pageants/{id}/campaigns`                | List marketing campaigns             |
| POST   | `/pageants/{id}/campaigns`                | Create a marketing campaign          |
| PATCH  | `/campaigns/{id}`                         | Update a marketing campaign          |
| POST   | `/pageants/{id}/posts`                    | Create a social media post           |
| GET    | `/pageants/{id}/posts`                    | List social media posts              |
| PATCH  | `/posts/{id}`                             | Update a post                        |
| GET    | `/pageants/{id}/program-book`             | Get the program book                 |
| POST   | `/pageants/{id}/program-book`             | Create or update program book        |
| POST   | `/pageants/{id}/ads`                      | Create an ad                         |
| GET    | `/pageants/{id}/ads`                      | List ads                             |

### Titleholders
| Method | Endpoint                                              | Description                          |
| ------ | ----------------------------------------------------- | ------------------------------------ |
| GET    | `/pageants/{id}/titleholders`                         | List titleholders                    |
| POST   | `/pageants/{id}/titleholders`                         | Create a titleholder                 |
| GET    | `/titleholders/{id}`                                  | Get a titleholder                    |
| PATCH  | `/titleholders/{id}`                                  | Update titleholder status            |
| PUT    | `/titleholders/{id}/contract`                         | Set titleholder contract             |
| POST   | `/titleholders/{id}/appearances`                      | Log an appearance                    |
| GET    | `/titleholders/{id}/appearances`                      | List appearances                     |
| POST   | `/titleholders/{id}/appearance-requests`              | Submit an appearance request         |
| GET    | `/titleholders/{id}/appearance-requests`              | List appearance requests             |
| PATCH  | `/appearance-requests/{id}`                           | Approve or decline a request         |
| POST   | `/titleholders/{id}/points`                           | Add points                           |
| GET    | `/titleholders/{id}/points`                           | List points                          |
| POST   | `/titleholders/{id}/removal`                          | Initiate removal proceeding          |
| GET    | `/titleholders/{id}/removal`                          | Get removal proceeding               |

### Finances
| Method | Endpoint                                  | Description                          |
| ------ | ----------------------------------------- | ------------------------------------ |
| GET    | `/pageants/{id}/budget`                   | List budget line items               |
| POST   | `/pageants/{id}/budget`                   | Create a budget line item            |
| PATCH  | `/budget/{item_id}`                       | Update a budget line item            |
| GET    | `/pageants/{id}/financial-summary`        | Get revenue vs. expenses summary     |

### System
| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| GET    | `/`            | Redirect to SPA   |
| GET    | `/health`      | Health check      |

---

## Remote Access

The app is served externally via **Tailscale** at **port 9121**. With Tailscale running on the host machine, the server is reachable at:

```
http://<tailscale-ip>:9121
```

The `run.sh` script binds to `0.0.0.0` so the server accepts connections from any network interface.

---

## Project Structure

```
pageantry-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, CORS, startup
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models.py            # All SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Tenant registration, login, session
│       ├── pageants.py      # Pageant CRUD, branding, divisions, categories, rubrics
│       ├── contestants.py   # Contestant registration, documents, fees, check-in
│       ├── scoring.py       # Judge panels, score entries, tabulation, results
│       ├── venues.py        # Venue CRUD, amenities, contracts, layouts
│       ├── sponsors.py      # Sponsors, tiers, agreements, donations, barter
│       ├── marketing.py     # Campaigns, social posts, program book, ads
│       ├── titleholders.py  # Titleholders, appearances, contracts, points, removal
│       └── finances.py      # Budget line items, financial summary
├── static/
│   ├── index.html           # SPA frontend
│   ├── styles.css           # Frontend styles
│   └── app.js               # Frontend logic
├── pageantry.db             # SQLite database (auto-created)
├── requirements.txt         # Python dependencies
├── SPEC.md                  # Full technical specification
├── run.sh                   # Quick-start launcher
└── README.md                # This file
```

---

## Testing

There is no formal test suite yet. The app can be tested manually via:

- **Swagger UI** — http://localhost:9121/docs
- **SPA frontend** — http://localhost:9121 (redirects to `/static/index.html`)
- **curl / HTTPie** — direct API calls with `X-Tenant-ID: 1` header

Example:

```bash
curl -s http://localhost:9121/health
# {"status":"ok","app":"Pageantry App"}

curl -s http://localhost:9121/pageants/ -H "X-Tenant-ID: 1"
# []
```