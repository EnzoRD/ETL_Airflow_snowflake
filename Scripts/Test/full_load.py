import os
import pandas as pd
import requests
from typing import Optional, Dict
from typing import List, Dict
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
API_KEY = "0e04b607776d479681b2ed1e3d44e64e"
#load_dotenv()
API_URL = "http://api.football-data.org/v4/competitions/{}/standings"
HEADERS = {"X-Auth-Token": API_KEY}


# Diccionario de ligas a consultar
LEAGUES = {
    "CL": "UEFA Champions League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PL": "Premier League",
    "PD": "La Liga"
}

def fetch_standings_all(league_code: str) -> Optional[Dict]:
    """
    Obtiene los datos completos de una liga, incluyendo la temporada y las posiciones.

    :param league_code: Código de la liga según football-data.org.
    :return: JSON con la información de la liga o None si falla la solicitud.
    """
    url = API_URL.format(league_code)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # 🔍 DEBUG: Imprimir la respuesta completa para verificar el contenido
        print(f"📡 JSON recibido para {league_code}:")
        print(data)

        if "season" not in data:
            print(f"⚠️ No se encontró información de la temporada para {league_code}.")
            return None

        return data  # Devolvemos todo el JSON

    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos para {league_code}: {e}")
        return None

def extract_season(data: dict, output_path: str, league_code: str):
    """
    Extrae la información de la temporada desde el JSON y la guarda en un CSV sin duplicados.

    :param data: JSON con la información de la liga y temporada.
    :param output_path: Ruta donde se guardará el archivo CSV.
    :param league_code: Código de la liga para identificación en el CSV.
    """
    season = data.get("season", {})

    if not season:
        print(f"⚠️ No se encontró información de la temporada en {league_code}.")
        return
    
    # Construcción del season_year (Ej: "2024/2025")
    start_year = season["startDate"][:4]
    end_year = season["endDate"][:4]
    season_year = f"{start_year}/{end_year}"

    # Crear DataFrame con una fila
    new_data = pd.DataFrame([{
        "league_name": LEAGUES[league_code],
        "league_code": league_code,
        "season_id": season["id"],
        "season_year": season_year,
        "start_date": season["startDate"],
        "end_date": season["endDate"],
        "is_active": True if season.get("currentMatchday") else False
    }])

    # Ruta del archivo CSV
    file_path = os.path.join(output_path, "seasons.csv")

    if os.path.exists(file_path):
        # Si el archivo ya existe, cargarlo y evitar duplicados
        existing_data = pd.read_csv(file_path, encoding="utf-8")

        # Verificar si la nueva fila ya existe en el archivo
        is_duplicate = ((existing_data["season_id"] == new_data["season_id"].iloc[0]) &
                        (existing_data["season_year"] == new_data["season_year"].iloc[0]) &
                        (existing_data["start_date"] == new_data["start_date"].iloc[0]) &
                        (existing_data["end_date"] == new_data["end_date"].iloc[0]) &
                        (existing_data["is_active"] == new_data["is_active"].iloc[0])).any()

        if is_duplicate:
            print(f"⚠️ Temporada {season_year} de {league_code} ya existe en seasons.csv. No se agregará duplicado.")
            return

        # Agregar la nueva fila si no es duplicada
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # Si el archivo no existe, crearlo con la primera fila
        updated_data = new_data

    # Guardar el CSV actualizado
    updated_data.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ Temporada de {league_code} agregada a seasons.csv en {file_path}")


def fetch_teams_from_standings(league_code: str):
    """
    Obtiene los equipos únicos desde la tabla de posiciones de una liga.
    
    :param league_code: Código de la liga según football-data.org.
    :return: Lista de diccionarios con los datos de los equipos.
    """
    url = API_URL.format(league_code)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        standings = data.get("standings", [])
        if not standings:
            print(f"⚠️ No se encontraron standings para {league_code}.")
            return []

        teams = []
        seen_teams = set()

        # Extraer equipos desde standings
        for entry in standings[0].get("table", []):
            team_info = entry["team"]
            team_id = team_info["id"]

            # Evitar equipos duplicados dentro de la misma liga
            if team_id not in seen_teams:
                teams.append({
                    "team_id": team_id,
                    "league_code": league_code,
                    "team_name": team_info["name"],
                    "short_name": team_info.get("shortName", ""),
                    "tla": team_info.get("tla", ""),
                    "crest_url": team_info.get("crest", "")
                })
                seen_teams.add(team_id)

        return teams

    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener equipos para {league_code}: {e}")
        return []


def save_teams_to_csv(teams_data: list, output_path: str):
    """
    Guarda los equipos en teams.csv evitando duplicados.
    
    :param teams_data: Lista de diccionarios con información de equipos.
    :param output_path: Ruta donde se guardará el archivo CSV.
    """
    if not teams_data:
        print("⚠️ No hay equipos para guardar.")
        return

    file_path = os.path.join(output_path, "teams.csv")
    new_df = pd.DataFrame(teams_data)

    if os.path.exists(file_path):
        # Cargar el archivo existente y evitar duplicados
        existing_df = pd.read_csv(file_path, encoding="utf-8")

        # Verificar si los equipos ya existen
        merged_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["team_id"], keep="first")
    else:
        merged_df = new_df

    # Guardar el CSV actualizado
    merged_df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ teams.csv actualizado en {file_path}")

def fetch_standings_from_json(data: Dict, league_code: str) -> List[Dict]:
    """
    Extrae la tabla de posiciones desde el JSON completo de la API.

    :param data: JSON obtenido de la API.
    :param league_code: Código de la liga.
    :return: Lista de diccionarios con los standings.
    """
    standings = data.get("standings", [])
    if not standings:
        print(f"⚠️ No se encontraron standings para {league_code}.")
        return []

    standings_data = []
    for entry in standings[0].get("table", []):  # Tomamos solo la primera etapa (Regular Season)
        team_info = entry["team"]

        standings_data.append({
            "league_code": league_code,
            "position": entry["position"],
            "team_id": team_info["id"],
            "team_name": team_info["name"],
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



def save_standings_to_csv(standings_data: list, output_path: str):
    """
    Guarda los standings en standings.csv evitando duplicados.
    
    :param standings_data: Lista de diccionarios con información de standings.
    :param output_path: Ruta donde se guardará el archivo CSV.
    """
    if not standings_data:
        print("⚠️ No hay standings para guardar.")
        return

    file_path = os.path.join(output_path, "standings.csv")
    new_df = pd.DataFrame(standings_data)

    if os.path.exists(file_path):
        # Cargar el archivo existente y evitar duplicados
        existing_df = pd.read_csv(file_path, encoding="utf-8")

        # Verificar si la combinación de `league_code` + `team_id` + `position` ya existe
        merged_df = pd.concat([existing_df, new_df]).drop_duplicates(
            subset=["league_code", "team_id", "position"], keep="first"
        )
    else:
        merged_df = new_df

    # Guardar el CSV actualizado
    merged_df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ standings.csv actualizado en {file_path}")





def main():
    """Función principal para extraer y guardar los datos de la temporada."""
    output_directory = r"C:\Users\enzor\Documents\Proyectos\Proyecto 2 ETL\ETL_Airflow_snowflake\Data"
    os.makedirs(output_directory, exist_ok=True)  # Crear la carpeta si no existe
    
    all_teams = []  # Lista para almacenar los equipos de todas las ligas
    all_standings = []# Lista para almacenar los standings de todas las ligas

    for league_code in LEAGUES.keys():
        print(f"📡 Obteniendo datos para {league_code}...")
        data = fetch_standings_all(league_code)  # Obtener el JSON completo
        if data:
            extract_season(data, output_directory, league_code)  # Extraer y guardar la temporada
            
            # Extraer equipos desde los standings y agregarlos a la lista
            teams = fetch_teams_from_standings(league_code)
            all_teams.extend(teams)
            
            # Extraer standings desde los standings y agregarlos a la lista
            standings = fetch_standings_from_json(data, league_code)  
            all_standings.extend(standings)
            
    # Guardar todos los equipos en teams.csv una sola vez para evitar múltiples escrituras
    if all_teams:
        save_teams_to_csv(all_teams, output_directory)
    
    # Guardar todos los standings en standings.csv una sola vez
    if all_standings:
        save_standings_to_csv(all_standings, output_directory)

if __name__ == "__main__":
    main()
