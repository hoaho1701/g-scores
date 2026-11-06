# G-Scores

A web application for looking up and analysing the 2024 Vietnamese national high-school exam (THPT) results. Built for the Golden Owl web developer intern assignment. The dataset contains **1,061,605** candidates from `dataset/diem_thi_thpt_2024.csv`.

The user interface is in Vietnamese, since the data and its audience are Vietnamese.

## Live demo

**https://g-scores-aba2.onrender.com**

> On a free hosting plan the app may sleep when idle, so the first request can take about a minute to respond.

## Features

1. **Score lookup by registration number.** Enter an 8-digit registration number (SBD) to see the scores of all 9 subjects. Subjects the candidate did not take are shown as `—`. Input is validated and a clear message is shown when no candidate is found.
2. **Statistics report.** A stacked bar chart shows how many candidates fall into each of 4 score levels, per subject: `>= 8`, `6 <= score < 8`, `4 <= score < 6` and `< 4`. A detailed table is shown below the chart.
3. **Top 10 of group A.** The 10 candidates with the highest total of Math + Physics + Chemistry.
4. **Responsive layout** that works on desktop, tablet and mobile.

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3.12, Django 6.1 |
| Database | PostgreSQL 16 through the Django ORM |
| Frontend | Django templates, Bootstrap 5, Chart.js |
| Package manager | uv |
| Containers | Docker, Docker Compose |
| Production | gunicorn, WhiteNoise |

## Project structure

```text
g-scores/
├── config/                          # project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dataset/
│   └── diem_thi_thpt_2024.csv       # raw data (1,061,605 rows)
├── scores/                          # main application
│   ├── management/
│   │   └── commands/
│   │       └── seed_scores.py       # imports the CSV into the database
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── scores/
│   │       ├── base.html            # shared layout and navbar
│   │       ├── lookup.html          # score lookup page
│   │       ├── report.html          # statistics chart page
│   │       └── top10.html           # top 10 of group A page
│   ├── forms.py                     # registration number validation
│   ├── models.py                    # StudentScore model
│   ├── services.py                  # lookup, report and top 10 queries
│   ├── subjects.py                  # OOP: ScoreLevel, Subject, SubjectRegistry
│   ├── urls.py
│   └── views.py
├── screenshots/                     # images used in this README
├── .dockerignore
├── docker-compose.yml               # app + PostgreSQL
├── Dockerfile                       # image of the Django app
├── manage.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

## Design

### Architecture

Requests flow through three thin layers, and the rules about subjects live in one separate module:

```text
browser ──► urls.py ──► views.py ──► services.py ──► models.py (Django ORM) ──► PostgreSQL
                            │               │
                            │               └──► subjects.py  (levels, subjects, groups)
                            └──► templates/   (Bootstrap + Chart.js)
```

- **Views** only read the request, call a service and render a template.
- **Services** hold every database query, so queries are easy to find.
- **`subjects.py`** holds the domain rules (which subjects exist, what the score levels are), independent of Django views and templates.

### Object-oriented subjects (`scores/subjects.py`)

- **`ScoreLevel` (Enum)** represents the 4 score levels. Each member stores its lower bound (inclusive), upper bound (exclusive) and display label, and provides `contains`, `from_score` (which level a score belongs to) and `q` (the matching ORM filter). The thresholds 8, 6 and 4 are defined in one place only, so classifying a score in Python and counting rows in SQL always agree.
- **`Subject` (frozen dataclass)** represents one subject: the model field name and the display name. `count_expressions` builds the aggregate expressions that count candidates per level.
- **`SubjectRegistry`** is the only place that lists the 9 subjects and the group A subjects. Adding a subject or another group means changing it here and nowhere else.

### Key decisions

| Decision | Reason |
|---|---|
| Registration number stored as `CharField(8, unique=True)` | It has leading zeros (`01000001`), which a number type would lose. `unique` also creates the index that keeps lookups fast on 1M+ rows. |
| Missing scores stored as `NULL`, not `0` | "Did not take the subject" is different from "scored 0". With `NULL`, a candidate who skipped a subject is never counted in the `< 4` level. |
| Report computed with one `aggregate` query using `Count(filter=Q(...))` | 9 subjects x 4 levels in a single SQL statement, instead of loading a million rows into Python. |
| Top 10 total computed with `F()` in the database | The sorting and `LIMIT` run in PostgreSQL, so only 10 rows are returned. Ties are broken by registration number for a stable order. |
| Import with `bulk_create` in batches, reading the CSV as a stream | One SQL statement per batch is much faster than one per row, and memory use stays bounded. |
| Lookup uses `GET` | It only reads data, and the result page can be bookmarked or shared. |
| Bootstrap and Chart.js loaded from a CDN with pinned versions | No build step or static asset pipeline is needed for the frontend. |

### Validation

- The registration number must be exactly 8 digits (`RegexField`); invalid input shows a message and never reaches the database.
- A valid number that does not exist shows a "not found" message.
- Database access goes through the ORM, which parameterises all queries.

## Running locally

### Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker (to run PostgreSQL)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/hoaho1701/g-scores.git
   cd g-scores
   ```

2. Start PostgreSQL with Docker. It is published on port `5433` to avoid clashing with a Postgres that may already use `5432`:
   ```bash
   docker run -d --name gscores-db \
     -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=gscores \
     -p 5433:5432 postgres:16
   ```
   The default connection string is `postgres://postgres:pass@localhost:5433/gscores`. To use another database, set the `DATABASE_URL` environment variable.

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create the tables:
   ```bash
   uv run python manage.py migrate
   ```

5. Import the data. This takes a few minutes and ends with `Done: 1061605`:
   ```bash
   uv run python manage.py seed_scores
   ```
   Options: `--file path/to/file.csv` and `--batch 5000`.

6. Start the server:
   ```bash
   uv run python manage.py runserver
   ```
   Open http://127.0.0.1:8000/

| Path | Page |
|---|---|
| `/` | Score lookup |
| `/report/` | Statistics report |
| `/top10/` | Top 10 of group A |

## Running with Docker

Only Docker is required (no Python or uv). Port `8000` on your machine must be free.

```bash
docker compose up --build -d
docker compose exec web python manage.py seed_scores
```

The second command imports the data and ends with `Done: 1061605`. Then open http://localhost:8000/.

To stop the app, run `docker compose down`. Add `-v` to also delete the database volume.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:pass@localhost:5433/gscores` |
| `SECRET_KEY` | Django secret key | `dev-only-key` (development only) |
| `DEBUG` | `1` enables debug mode, any other value disables it | `1` |
| `ALLOWED_HOSTS` | Comma-separated host names | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | empty |

For a real deployment, set a new `SECRET_KEY`, `DEBUG=0` and the correct `ALLOWED_HOSTS`, run `python manage.py collectstatic --noinput`, then start the app with `gunicorn config.wsgi`.

## Screenshots

**Score lookup**

<img src="screenshots/lookup.png" width="800" alt="Score lookup page">

**Statistics report**

<img src="screenshots/report.png" width="800" alt="Statistics report page">

**Top 10 of group A**

<img src="screenshots/top10.png" width="800" alt="Top 10 of group A page">

## Data source

The 2024 national exam results are provided by the assignment (`dataset/diem_thi_thpt_2024.csv`).
