# ETL Vacancies Pipeline (Airflow + PostgreSQL + Docker)

A fully containerized ETL pipeline that processes mock job vacancies data and loads it into a PostgreSQL data warehouse using a layered architecture (RAW → STAGING → MART).

The workflow is orchestrated with Apache Airflow and runs inside Docker Compose, making the entire project reproducible with a single command.

## Tech Stack

- Python 3
- PostgreSQL 15
- Apache Airflow 2.x
- Docker & Docker Compose

## Architecture Overview

The project follows a classic data engineering layered approach:

                 +---------------------+
                 |  JSON Source File   |
                 |  (Mock US data)     |
                 +----------+----------+
                            |
                            v
                     [Extract Layer]
                            |
                            v
                     RAW (JSONB)
                            |
                            v
                     STAGING (Cleaned Data)
                            |
                            v
                     MART (Aggregated Metrics)
                            |
                            v
                     PostgreSQL Data Warehouse

### Data Layers

#### 1. RAW Layer
- Stores raw JSON payload as-is
- Minimal transformation
- Used for traceability and reprocessing

#### 2. STAGING Layer
- Normalized and cleaned data
- Structured columns (title, company, salary, etc.)
- Prepared for analytics

#### 3. MART Layer
- Aggregated analytical table
- Example: average salary per skill
- Designed for reporting and BI usage

### Components

- **PostgreSQL**
  - `etl` database → stores business data (RAW, STAGING, MART)
  - `airflow` database → stores Airflow metadata

- **Apache Airflow**
  - Orchestrates ETL tasks
  - Manages scheduling, retries, and task dependencies

- **Docker Compose**
  - Provides a fully reproducible environment
  - Initializes databases and schema automatically

## How to Run the Project

This project is fully containerized.\
After cloning the repository, only **three commands** are required.

### Clone only the `etl_vacancies` branch

`git clone -b etl_vacancies https://github.com/tarmino-dev/thinking.git`  

### Environment Variables

The project uses a `.env` file.
Run to copy:

`cp .env.example .env`

### Start the environment

`cd thinking/fun_projects/etl_vacancies`  
`docker compose up --build`

This will:

-   Start PostgreSQL
-   Create the `etl` database
-   Initialize schema automatically
-   Start Airflow (webserver + scheduler)
-   Register the ETL DAG

### Open Airflow UI

Navigate to:

    http://localhost:8080

Default credentials:

    Username: admin
    Password: admin

### Run the ETL Pipeline

The extractor reads its source file by date: it looks for
`data/raw/vacancies_YYYY_MM_DD.json`, where the date is the DAG's logical
date (or, for a local run, the `--date` argument). The repo ships one sample
export, `vacancies_2024_01_10.json`, so trigger the DAG for that date rather
than "now" — otherwise the run fails with a "No vacancies export found"
error.

1.  Locate the DAG:

        vacancies_etl_pipeline

2.  Enable the DAG (toggle switch)

3.  Trigger it for the sample export date:
    - Click **Trigger DAG w/ config**
    - Set **Logical Date** to `2024-01-10`
    - Run

    (A plain **Trigger DAG** click uses today's date and will fail unless a
    matching `vacancies_YYYY_MM_DD.json` file exists for that date.)

To run the pipeline directly with Python instead of Airflow:

`python -m etl.main --date 2024-01-10`

(defaults to today's date if `--date` is omitted)

### Verify Results

After successful execution:

-   RAW table contains JSON payload
-   STAGING table contains normalized rows
-   MART table contains aggregated statistics

You can verify via:

-   DBeaver / pgAdmin
-   `psql`
-   Airflow task logs

## Stop the Project

To stop all containers:

`docker compose down`

To fully reset (including database volumes):

`docker compose down -v`