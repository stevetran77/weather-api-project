import sys
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append('/opt/airflow/api')

def safe_main_callable():    
    from api.insert_records import main
    return main()

default_args = {
    'description': 'DAG to orchestrate weather data fetching and insertion',
    'start_date': datetime(2023, 10, 1),
    'catchup': False
}
dag = DAG(
    'weather_data_orchestrator',
    default_args=default_args,
    schedule=None,
)

with dag:
    task1 = PythonOperator(
        task_id='ingest_data_task',
        python_callable=safe_main_callable
    )
