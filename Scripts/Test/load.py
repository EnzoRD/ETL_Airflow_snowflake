from utils import get_snowflake_connection

conn = get_snowflake_connection()
cursor = conn.cursor()

cursor.execute("SELECT CURRENT_VERSION();")
print(f"✅ Conexión exitosa. Versión de Snowflake: {cursor.fetchone()[0]}")

cursor.close()
conn.close()
