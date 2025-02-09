from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago

SNOWFLAKE_CONN_ID = "snowflake_conect"  # Asegúrate de que el ID coincida con tu conexión en Airflow

dag = DAG(
    "test_snowflake_connection",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

test_query = SnowflakeOperator(
    task_id="test_snowflake_query",
    sql="SELECT CURRENT_VERSION();",
    snowflake_conn_id=SNOWFLAKE_CONN_ID,
    dag=dag,
)

test_query
