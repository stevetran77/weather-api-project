# api_request/airflow/dags/weather_data_pipeline.py
from __future__ import annotations

import os
import sys
from datetime import datetime

from airflow.models.dag import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator
from docker.types import Mount

# =====================================================================================
# ==                            CẤU HÌNH CHO DBT TASK                                ==
# =====================================================================================

DBT_IMAGE = os.getenv("DBT_IMAGE", "ghcr.io/dbt-labs/dbt-postgres:1.9.latest")
DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/usr/app")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "/root/.dbt")
DBT_TARGET = os.getenv("DBT_TARGET", "dev")
DBT_THREADS = os.getenv("DBT_THREADS", "4")

# Paths trên máy HOST (máy chạy Docker daemon)
HOST_PROJECT_DIR = os.getenv("AIRFLOW_DBT_PROJECT_HOST_PATH", "/opt/airflow/dbt/my_project")
HOST_PROFILES_DIR = os.getenv("AIRFLOW_DBT_PROFILES_DIR_HOST_PATH", "/opt/airflow/.dbt")

# Các tham số chung cho DockerOperator để tránh lặp lại code
COMMON_DOCKER_KWARGS = dict(
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
    # Sử dụng Mount để map volume, đây là cách làm được khuyến nghị
    mounts=[
        # Map toàn bộ thư mục project dbt vào container
        Mount(source=HOST_PROJECT_DIR, target=DBT_PROJECT_DIR, type="bind", read_only=False),
        # Map thư mục chứa profiles.yml vào container
        Mount(source=HOST_PROFILES_DIR, target=DBT_PROFILES_DIR, type="bind", read_only=True),
    ],
    working_dir=DBT_PROJECT_DIR,
    mount_tmp_dir=False,
)

# =====================================================================================
# ==                            HÀM CHO PYTHON TASK                                  ==
# =====================================================================================

# Thêm đường dẫn tới module 'api' để Airflow có thể import
sys.path.append('/opt/airflow/api')

def safe_main_callable():
    """
    Wrapper function để import và gọi hàm main từ script bên ngoài một cách an toàn.
    Điều này ngăn ngừa việc ô nhiễm global namespace của file DAG.
    """
    from api.insert_records import main
    return main()

# =====================================================================================
# ==                            ĐỊNH NGHĨA DAG VÀ TASKS                              ==
# =====================================================================================

with DAG(
    dag_id="weather_data_pipeline",
    description="Pipeline hoàn chỉnh: lấy dữ liệu thời tiết và biến đổi bằng dbt.",
    start_date=datetime(2023, 10, 1),
    schedule=None,
    catchup=False,
    tags=["api", "dbt"],
) as dag:
    # --- TASK 1: Lấy dữ liệu từ API và lưu vào database ---
    ingest_data_task = PythonOperator(
        task_id='ingest_data_task',
        python_callable=safe_main_callable,
        doc_md="Chạy script Python để gọi API thời tiết và ghi dữ liệu thô vào database."
    )

    # --- TASK 2: Chạy dbt để biến đổi dữ liệu ---
    transform_data_task = DockerOperator(
        task_id="transform_data_task",
        command=f"run --target {DBT_TARGET}",
        **COMMON_DOCKER_KWARGS,
        doc_md="Chạy `dbt run` trong một container Docker để biến đổi dữ liệu đã được ingest."
    )

    # --- Thiết lập thứ tự thực thi: Ingest -> Transform ---
    ingest_data_task >> transform_data_task