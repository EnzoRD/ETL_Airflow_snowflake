import snowflake.connector

conn = snowflake.connector.connect(
    user="ENZORD",  # Usa tu usuario de Snowflake
    password="Snowys15",  # Ingresa tu contraseña
    account="tn11007.sa-east-1.aws"  # Usa el account correcto (sin 'aws' ni '.snowflakecomputing.com')
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION();")
print(cursor.fetchone())