from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime
import json

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="microservices_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    scraper = HttpOperator(
        task_id="run_scraper",
        http_conn_id="scraper",
        endpoint="scrape",
        method="POST",
        data=json.dumps({
            "url": "https://www.google.com/maps/place/Caf%C3%A9+de+Flore/@48.8541623,2.3300297,16z/data=!4m8!3m7!1s0x47e671d781fb9dab:0x18bba6dd45e173ff!8m2!3d48.8541588!4d2.3326046!9m1!1b1!16zL20vMDhkeXY4?entry=ttu&g_ep=EgoyMDI2MDIyMy4wIKXMDSoASAFQAw%3D%3D",
            "name": "cafe_de_flore",
            "max_reviews": "20"
        }),
        headers={"Content-Type": "application/json"},
    )

    cleaning = HttpOperator(
        task_id="run_cleaning",
        http_conn_id="cleaning",
        endpoint="clean",
        method="POST",
        data=json.dumps({
            "name": "cafe_de_flore"
        }),
        headers={"Content-Type": "application/json"},
    )

    ml = HttpOperator(
        task_id="run_ml",
        http_conn_id="ml",
        endpoint="sentiment",
        method="POST",
        data=json.dumps({
            "name": "cafe_de_flore",
            "plot": False
        }),
        headers={"Content-Type": "application/json"},
    )

    scraper >> cleaning >> ml