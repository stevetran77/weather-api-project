# api_request/airflow/dags/dbt_orchestrator.py
from __future__ import annotations
import os
from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from docker.types import Mount  # 🔑 dùng Mount thay cho volumes

DBT_IMAGE = os.getenv("DBT_IMAGE", "ghcr.io/dbt-labs/dbt-postgres:1.9.latest")
DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/usr/app")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "/root/.dbt")  # là THƯ MỤC
DBT_TARGET = os.getenv("DBT_TARGET", "dev")
DBT_THREADS = os.getenv("DBT_THREADS", "4")

# Paths trên HOST (máy chạy Docker daemon)
HOST_PROJECT = os.getenv("AIRFLOW_DBT_PROJECT_HOST_PATH", "/opt/airflow/dbt/my_project")
# Khuyến nghị: để sẵn cả folder .dbt chứa profiles.yml
HOST_PROFILES_DIR = os.getenv("AIRFLOW_DBT_PROFILES_DIR_HOST_PATH", "/opt/airflow/.dbt")
# Nếu bạn chỉ có 1 file, cũng được, xem Option B phía dưới

COMMON_KWARGS = dict(
    image=DBT_IMAGE,
    auto_remove="success",
    tty=True,
    docker_url=os.getenv("DOCKER_URL", "unix://var/run/docker.sock"),
    network_mode=os.getenv("DOCKER_NETWORK", "api_request_my-network"),
    environment={
        "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
        "DBT_TARGET": DBT_TARGET,
        "DBT_THREADS": DBT_THREADS,
    },
    # ❗ mounts thay cho volumes
    mounts=[
        # Project: bind cả folder code vào /usr/app
        Mount(source=HOST_PROJECT, target=DBT_PROJECT_DIR, type="bind", read_only=False),

        # Option A (khuyến nghị): bind cả thư mục .dbt (chứa profiles.yml)
        Mount(source=HOST_PROFILES_DIR, target=DBT_PROFILES_DIR, type="bind", read_only=True),
    ],
    working_dir=DBT_PROJECT_DIR,
    mount_tmp_dir=False,  # tránh mount /tmp mặc định của operator nếu không cần
)

with DAG(
    dag_id="weather_dbt_orchestrator",
    description="DAG to orchestrate weather data fetching and dbt pipeline",
    start_date=datetime(2023, 10, 1),
    schedule=None,
    catchup=False,
    tags=["dbt"],
) as dag:
    dbt_run = DockerOperator(
        task_id="transform_data_task",
        command=f"run --target {DBT_TARGET}",  # image entrypoint already invokes `dbt`
        **COMMON_KWARGS,
    )
