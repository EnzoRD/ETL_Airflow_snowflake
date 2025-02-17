from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Ruta donde queremos guardar el archivo dentro del contenedor
DATA_PATH = "/usr/local/airflow/tests"

def create_test_csv():
    """Crea un archivo CSV de prueba en la ruta especificada."""
    file_path = os.path.join(DATA_PATH, "test.csv")
    
    # Crear un DataFrame de prueba
    df = pd.DataFrame({"ID": [1, 2, 3], "Nombre": ["Equipo A", "Equipo B", "Equipo C"]})

    # Guardar el archivo CSV
    df.to_csv(file_path, index=False, encoding="utf-8")

    print(f"Archivo guardado en {file_path}")

# Definir el DAG
with DAG(
    dag_id="dag_test_csv",
    schedule_interval=None,  # Ejecutar manualmente
    start_date=datetime(2025, 2, 13),
    catchup=False,
    tags=["debug", "csv"]
) as dag:

    task_create_csv = PythonOperator(
        task_id="create_csv",
        python_callable=create_test_csv
    )

    task_create_csv
