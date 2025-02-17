from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime, timedelta
import os
from dag_utils import fetch_standings_all, fetch_standings_from_json, save_standings_to_csv

# Configuración del DAG
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

""" usamos dag = DAG(...) porque nos permite definir tareas de manera modular
    Permite mayor flexibilidad para definir tareas en diferentes partes del código
"""


dag = DAG(
    'standings_dag_2',
    default_args=DEFAULT_ARGS,
    description='DAG para extraer, transformar y cargar standings en Snowflake',
    schedule_interval='0 0 * * 0',  # Se ejecuta todos los domingos a la medianoche
    catchup=False
)

# Ruta del archivo CSV
DATA_PATH = os.getenv("DATA_PATH")
STANDINGS_FILE = os.path.join(DATA_PATH, "standings.csv")

# 1️⃣ Tarea: Extraer y Transformar Standings
def extract_transform_standings():
    all_standings = []
    for league_code in ["CL", "BL1", "SA", "PL", "PD"]:
        data = fetch_standings_all(league_code)
        if data:
            standings = fetch_standings_from_json(data, league_code)
            all_standings.extend(standings)
    save_standings_to_csv(all_standings, DATA_PATH)

extract_transform_task = PythonOperator(
    task_id='extract_transform_standings',
    python_callable=extract_transform_standings,
    dag=dag
)

# 2️⃣ Tarea: Subir CSV a Snowflake
upload_standings_task = PythonOperator(
    task_id='upload_standings_to_snowflake',
    python_callable=lambda: upload_file_to_snowflake("standings.csv"),
    dag=dag
)

# 3️⃣ Tarea: Desactivar standings previos en Snowflake
update_previous_standings_task = SnowflakeOperator(
    task_id='update_previous_standings',
    sql="""
        UPDATE LEAGUES.FOOTBALL.STANDINGS
        SET IS_ACTIVE = FALSE
        WHERE IS_ACTIVE = TRUE;
    """,
    snowflake_conn_id='snowflake_default',
    dag=dag
)
