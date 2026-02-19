from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.extract.vacancies_extractor import extract_vacancies_from_json
from etl.load.load_raw import load_raw_vacancies
from etl.extract.raw_reader import read_raw_vacancies
from etl.transform.vacancies_transformer import transform_vacancies
from etl.load.load_staging import load_staging_vacancies
from etl.load.load_mart import refresh_skill_stats

from pathlib import Path


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}


def extract_and_load_raw():
    path = Path("/opt/airflow/etl_project/data/raw/vacancies_2024_01_10.json")
    vacancies = extract_vacancies_from_json(path)
    load_raw_vacancies(vacancies)


def transform_and_load_staging():
    raw = read_raw_vacancies()
    transformed = transform_vacancies(raw)
    load_staging_vacancies(transformed)


dag = DAG(
    dag_id="vacancies_etl_pipeline",
    default_args=default_args,
    description="ETL pipeline for vacancies analytics",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
)


extract_task = PythonOperator(
    task_id="extract_load_raw",
    python_callable=extract_and_load_raw,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_load_staging",
    python_callable=transform_and_load_staging,
    dag=dag,
)

mart_task = PythonOperator(
    task_id="refresh_mart",
    python_callable=refresh_skill_stats,
    dag=dag,
)

extract_task >> transform_task >> mart_task
