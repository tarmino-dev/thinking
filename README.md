# thinking — Multi-Project Portfolio

This repository is a **multi-project portfolio**. It collects my pet projects and learning
work in one place, under `fun_projects/`. Each project has its own `README.md` with full
details.

If you're a recruiter or engineer landing here, start with the **Main Projects** below —
those are the ones built to a production-like standard (own architecture, tests, Docker,
CI/CD, cloud deployment). Everything else is grouped as secondary and learning work so it's
clear at a glance what is what.

---

## Main Projects

Production-oriented projects. Each lives on its own deployment branch where noted.

| Project | What it is | Tech stack | Links |
|---|---|---|---|
| **Literary Diary** | A Flask web app for writing and sharing notes, with AI-assisted discussion and AI-generated header images. | Flask · SQLAlchemy · Jinja · AI (Anthropic Claude, Cloudflare Workers AI + R2) · Open Library API · unit + UI tests (CI) · Render | [Code](https://github.com/tarmino-dev/thinking/tree/main/fun_projects/flask/flask_lit_diary) · [Live](https://literature-diary.onrender.com/) · [README](fun_projects/flask/flask_lit_diary/README.md) |
| **Image Upload API** | Cloud backend to upload, process (async), and store images, with JWT auth and automated deployment. | FastAPI · Celery · Redis · PostgreSQL · AWS S3 + RDS · JWT · Docker · GitHub Actions (deploy to EC2) | [Code](https://github.com/tarmino-dev/thinking/tree/image_upload_api/fun_projects/image_upload_api) · [README](fun_projects/image_upload_api/README.md) |
| **ETL Vacancies Pipeline** | Containerized ETL pipeline (RAW → STAGING → MART) for job-vacancy data, orchestrated with Airflow. | Python · PostgreSQL · Apache Airflow · Docker Compose | [Code](https://github.com/tarmino-dev/thinking/tree/etl_vacancies/fun_projects/etl_vacancies) · [README](fun_projects/etl_vacancies/README.md) |
| **RAG Pipeline** | Minimal Retrieval-Augmented Generation pipeline: embed documents, store in a vector index, retrieve, and generate with a local LLM. | Python · FAISS · Sentence Transformers · Ollama | [Code](https://github.com/tarmino-dev/thinking/tree/rag/fun_projects/rag) · [README](fun_projects/rag/README.md) |

> Note: Image Upload API is deployed on AWS EC2; a stable public URL is not linked yet
> because the instance IP changes on restart.

---

## Also Worth a Look

Smaller projects that still show real engineering signal (tests, databases, external-API
integrations) — a step above pure exercises.

- **[API integrations](fun_projects/api/)** — a collection of mini-apps working with external
  APIs (cafe API, flight deals, habit tracker, ISS notifier, quizzler, rain alert, stock news,
  workout tracker, and more).
- **[Coffee Machine](fun_projects/learning/coffee_machine/)** — coffee-machine simulator with a
  database layer, config, and unit tests (runs in CI).
- **[Number Guessing](fun_projects/learning/number_guessing/)** — a small game with unit tests
  (runs in CI).

---

## Learning & Experiments

Exercises and experiments from my Python learning journey (bootcamp-style). Kept for history —
not intended as showcase projects. All live under [`fun_projects/learning/`](fun_projects/learning/).

<details>
<summary>Expand list</summary>

- **Python fundamentals & small scripts:** `auto_bday_wisher`, `motiv_quotes_sender`,
  `mail_merge`, `nato_alphabet`, `csv_data_pandas`, `PYQT1`
- **GUI & games (Tkinter / Turtle):** `tkinter_basics`, `turtle_challenges`, `us_states_game`,
  `flash_cards`
- **Web fundamentals (HTML/CSS):** `web`
- **Flask course exercises:** `flask_course/` (blog templating, auth, bootstrap intros,
  SQLAlchemy/SQLite tests, tindog, top-movies, and more)

</details>

---

## Repository layout

```
fun_projects/
├── flask/flask_lit_diary/   Literary Diary (main)
├── image_upload_api/        Image Upload API (main)
├── etl_vacancies/           ETL Pipeline (main)
├── rag/                     RAG Pipeline (main)
├── api/                     external-API mini-projects
└── learning/                bootcamp exercises & experiments
```
