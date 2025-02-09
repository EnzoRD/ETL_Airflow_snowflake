import os
import pandas as pd
import requests
from typing import Optional, Dict
from typing import List, Dict
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()
API_URL = "http://api.football-data.org/v4/competitions/{}/standings"
HEADERS = {"X-Auth-Token": os.getenv('API_KEY')}

# Diccionario de ligas a consultar
LEAGUES = {
    "CL": "UEFA Champions League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PL": "Premier League",
    "PD": "La Liga"
}

# Funciones de Extación y Transformación

# Leagues
def extract_leagues(output_path: str):
    """Genera el archivo leagues.csv con el formato correcto."""
    df = pd.DataFrame(
        [{"LEAGUE_ID": code, "LEAGUE_NAME": name} for code, name in LEAGUES.items()],
        columns=["LEAGUE_ID", "LEAGUE_NAME"]
    )

    file_path = os.path.join(output_path, "leagues.csv")
    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ leagues.csv generado en {file_path}")



def fetch_standings_all(league_code: str) -> Optional[Dict]:
    """Obtiene el JSON completo de standings para una liga."""
    url = API_URL.format(league_code)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos para {league_code}: {e}")
        return None

# Seasons

def extract_season(data: Dict, output_path: str, league_code: str):
    """Extrae y guarda información de la temporada en `seasons.csv`."""
    """new_data = pd.DataFrame([{
        "start_date": season["startDate"],
        "end_date": season["endDate"],
        "is_active": True if season.get("currentMatchday") else False,
        "league_code": league_code,  
        "season_id": season["id"],  # Tomamos el ID de la API
        "season_year": season_year
    }])"""
    season_info = {
        "START_DATE": data["season"]["startDate"],
        "END_DATE": data["season"]["endDate"],
        "IS_ACTIVE": True,
        "LEAGUE_CODE": league_code,
        "SEASON_ID": data["season"]["id"],
        "SEASON_YEAR": f"{data['season']['startDate'][:4]}/{data['season']['endDate'][:4]}"
    }

    file_path = os.path.join(output_path, "seasons.csv")
    save_to_csv(pd.DataFrame([season_info]), file_path, ["SEASON_ID", "LEAGUE_CODE"])

# Teams

def fetch_teams_from_standings(league_code: str) -> List[Dict]:
    """Obtiene los equipos desde standings."""
    data = fetch_standings_all(league_code)
    if not data:
        return []

    teams = []
    seen_teams = set()
    for entry in data.get("standings", [])[0].get("table", []):
        team_info = entry["team"]
        team_id = team_info["id"]

        if team_id not in seen_teams:
            teams.append({
                "team_id": team_id,
                "team_name": team_info["name"],
                "short_name": team_info.get("shortName", ""),
                "tla": team_info.get("tla", ""),
                "crest_url": team_info.get("crest", ""),
                "league_code": league_code
            })
            seen_teams.add(team_id)
    
    return teams


# Standings

def fetch_standings_from_json(data: Dict, league_code: str) -> List[Dict]:
    """Extrae standings desde el JSON de standings."""
    standings_data = []
    for entry in data.get("standings", [])[0].get("table", []):
        team_info = entry["team"]
        standings_data.append({
            "league_code": league_code,
            "season_id": data["season"]["id"],
            "team_id": team_info["id"],
            "position": entry["position"],
            "played_games": entry["playedGames"],
            "won": entry["won"],
            "draw": entry["draw"],
            "lost": entry["lost"],
            "points": entry["points"],
            "goals_for": entry["goalsFor"],
            "goals_against": entry["goalsAgainst"],
            "goal_difference": entry["goalDifference"]
        })
    return standings_data

# Funciones de Guardado

def save_to_csv(new_data: pd.DataFrame, file_path: str, unique_keys: List[str]):
    """Guarda datos en un CSV evitando duplicados."""
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path, encoding="utf-8")
        merged_df = pd.concat([existing_data, new_data]).drop_duplicates(subset=unique_keys, keep="first")
    else:
        merged_df = new_data

    merged_df.columns = [col.upper() for col in merged_df.columns]  # Convierte todas las columnas a mayúsculas
    
    merged_df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ Datos guardados en {file_path}")


def save_teams_to_csv(teams_data: List[Dict], output_path: str):
    """Guarda equipos en `teams.csv` evitando duplicados."""
    file_path = os.path.join(output_path, "teams.csv")
    save_to_csv(pd.DataFrame(teams_data), file_path, ["team_id"])

def save_standings_to_csv(standings_data: List[Dict], output_path: str):
    """Guarda standings en `standings.csv` evitando duplicados."""
    file_path = os.path.join(output_path, "standings.csv")
    save_to_csv(pd.DataFrame(standings_data), file_path, ["league_code", "team_id", "position"])


# Función de Carga a snowflake

import snowflake.connector
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Credenciales de Snowflake desde variables de entorno
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_STAGE = os.getenv("SNOWFLAKE_STAGE")
SNOWFLAE_ROLE = os.getenv("SNOWFLAE_ROLE")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
DATA_PATH = os.getenv("DATA_PATH")  

def get_snowflake_connection():
    """Establece una conexión con Snowflake usando variables de entorno."""
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAE_ROLE,
        warehouse=SNOWFLAKE_WAREHOUSE
    )
    return conn

def upload_file_to_snowflake(file_name: str):
    """
    Sube un archivo CSV al Stage de Snowflake de manera robusta.

    :param file_name: Nombre del archivo CSV a subir.
    """
    # Ruta completa al archivo
    file_path = os.path.abspath(os.path.join(DATA_PATH, file_name)).replace("\\", "/")  # Windows/Linux-safe
    
    # Verificar si el archivo existe y no está vacío
    if not os.path.exists(file_path):
        print(f"⚠️ Archivo {file_name} no encontrado en {DATA_PATH}. No se subirá.")
        return
    if os.path.getsize(file_path) == 0:
        print(f"⚠️ Archivo {file_name} está vacío. No se subirá a Snowflake.")
        return

    sql_query = f"PUT 'file://{file_path}' @LEAGUES.FOOTBALL.DEMO_STAGE auto_compress=true;"

    conn = get_snowflake_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        print(f"✅ Archivo {file_name} subido a Snowflake.")
    except Exception as e:
        print(f"❌ Error al subir {file_name}: {e}")
    finally:
        cur.close()
        conn.close()

        
def load_csv_into_snowflake(table_name: str, file_name: str, unique_keys: List[str], columns: List[str]):
    """
    Carga datos desde el Stage a una tabla en Snowflake sin duplicar registros.

    :param table_name: Nombre de la tabla destino en Snowflake.
    :param file_name: Nombre del archivo en el Stage.
    :param unique_keys: Columnas únicas para evitar duplicados.
    :param columns: Lista de nombres de las columnas del archivo CSV.
    """
    # Convertir la lista de claves únicas en una condición ON para MERGE
    merge_condition = " AND ".join([f"TARGET.{key} = SOURCE.{key}" for key in unique_keys])

    # Especificar las columnas explícitamente
    column_list = ", ".join(columns)
    source_column_list = ", ".join([f"SOURCE.{col}" for col in columns])

    sql_query = f"""
    MERGE INTO LEAGUES.FOOTBALL.{table_name} AS TARGET
    USING (
        SELECT 
            {", ".join([f"${i+1} AS {col}" for i, col in enumerate(columns)])}
        FROM @LEAGUES.FOOTBALL.DEMO_STAGE/{file_name}.gz
        (FILE_FORMAT => LEAGUES.FOOTBALL.CSV_FORMAT)
    ) AS SOURCE
    ON {merge_condition}
    WHEN MATCHED THEN
        UPDATE SET {", ".join([f"TARGET.{col} = SOURCE.{col}" for col in columns if col not in unique_keys])}
    WHEN NOT MATCHED THEN
        INSERT ({column_list}) 
        VALUES ({source_column_list});
"""



    conn = get_snowflake_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        print(f"✅ Datos de {file_name} cargados en {table_name} sin duplicados.")
    except Exception as e:
        print(f"❌ Error al cargar {file_name} en {table_name}: {e}")
    finally:
        cur.close()
        conn.close()



