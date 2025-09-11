import sys
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append('/opt/airflow/api')

def safe_main_callable():    
    from api.insert_records import main
    return main()

dèfault_args = {
    'description': 'DAG to orchestrate weather data fetching and insertion',
    'owner': 'airflow',
    'start_date': datetime(2023, 10, 1),
    'schedule' : None,
    'catchup': False
}
dag = DAG(
    'weather_data_orchestrator',
    default_args=dèfault_args,
    schedule_interval=timedelta(minutes=5)
)

with dag:
    task1 = PythonOperator(
        task_id='orchestrate_weather_data',
        python_callable=safe_main_callable
    )
