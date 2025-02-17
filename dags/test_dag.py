from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator  
from airflow.models import Variable
from datetime import datetime
import os
from dag_utils import fetch_standings_all, fetch_standings_from_json, save_standings_to_csv, LEAGUES

# 🔹 Cargar variables de entorno desde Airflow UI
params_info = Variable.get("keys", deserialize_json=True)

DATA_PATH = params_info["DATA_PATH"]
API_URL = params_info["API_URL"]
API_KEY = params_info["API_KEY"]

# 🔹 Función para extraer standings y guardar CSV
def extract_and_save_standings():
    """Extrae standings y los guarda en un CSV."""
    os.makedirs(DATA_PATH, exist_ok=True)  # Asegurar que el directorio existe

    all_standings = []
    for league_code in LEAGUES.keys():
        print(f" Obteniendo standings para {league_code}...")
        data = fetch_standings_all(league_code)
        if data:
            standings = fetch_standings_from_json(data, league_code)
            all_standings.extend(standings)

    if all_standings:
        save_standings_to_csv(all_standings, DATA_PATH)
        print(f" CSV de standings guardado en {DATA_PATH}/standings.csv")

#  Configuración del DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 2, 1),
    "catchup": False
}

dag = DAG(
    "standings_etl",
    default_args=default_args,
    schedule_interval="0 12 * * 1",  # 🔹 Corre cada lunes a las 12:00 PM UTC
    description="DAG para extraer standings y generar CSV",
    tags=["ETL", "standings"]
)

#  Definir tarea de extración
extract_task = PythonOperator(
    task_id="extract_etl_standings",
    python_callable=extract_and_save_standings,
    dag=dag
)


# Tarea de subida a Snowflake
upload_task_stage = SnowflakeOperator(
    task_id="upload_etl_stage_standings",
    sql="PUT file://{{ params.PATH_FILE }} @{{ params.SNOWFLAKE_STAGE }} auto_compress=true;",  # SQL para subir el CSV
    snowflake_conn_id="snowflake_conect",
    warehouse=params_info["SNOWFLAKE_WAREHOUSE"],
    database=params_info["SNOWFLAKE_DATABASE"],
    role=params_info["SNOWFLAKE_ROLE"],
    params=params_info,
    dag=dag
)

# Definir el orden de ejecución
extract_task >> upload_task_stage