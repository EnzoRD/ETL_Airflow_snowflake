import os
import pandas as pd
import requests
from airflow.models import Variable
from datetime import datetime, timezone
from typing import Optional, Dict
from typing import List, Dict
from dotenv import load_dotenv
#import sys
#sys.stdout.reconfigure(encoding='utf-8')

# Diccionario de ligas a consultar
LEAGUES = {
    "CL": "UEFA Champions League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PL": "Premier League",
    "PD": "La Liga"
}
params_info = Variable.get("keys", deserialize_json=True)

DATA_PATH = params_info["DATA_PATH"]
API_URL = params_info["API_URL"]
API_KEY = params_info["API_KEY"]
HEADERS = {"X-Auth-Token": params_info["API_KEY"]}




def fetch_standings_all(league_code: str) -> Optional[Dict]:
    """Obtiene el JSON completo de standings para una liga."""
    url = API_URL.format(league_code)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f" Error al obtener datos para {league_code}: {e}")
        return None

# Standings

def fetch_standings_from_json(data: Dict, league_code: str) -> List[Dict]:
    """Extrae standings desde el JSON de standings."""
    standings_data = []
    for entry in data.get("standings", [])[0].get("table", []):
        team_info = entry["team"]
        standings_data.append({
            "LEAGUE_ID": league_code,  # Ajuste de nombre
            "SEASON_ID": data["season"]["id"],
            "TEAM_ID": team_info["id"],
            "POSITION": entry["position"],
            "PLAYED_GAMES": entry["playedGames"],
            "WON": entry["won"],
            "DRAW": entry["draw"],
            "LOST": entry["lost"],
            "POINTS": entry["points"],
            "GOALS_FOR": entry["goalsFor"],
            "GOALS_AGAINST": entry["goalsAgainst"],
            "GOAL_DIFFERENCE": entry["goalDifference"],
            "IS_ACTIVE": True,  # Marcamos como activo
            "UPDATED_AT": None  # Se actualizará si el registro cambia
        })
    return standings_data


def save_standings_to_csv(standings_data: List[Dict], output_path: str):
    """Guarda standings en `standings.csv`, eliminando cualquier versión anterior."""
    file_path = os.path.join(output_path, "standings.csv")
    
    print("Archivos antes de guardar:", os.listdir(output_path))  # Debug
    
    # Convertir a DataFrame y convertir columnas a mayúsculas
    df = pd.DataFrame(standings_data)
    df.columns = [col.upper() for col in df.columns]

    # Eliminar el archivo anterior si existe (para sobrescribir completamente)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Guardar la versión actualizada de standings
    df.to_csv(file_path, index=False, encoding="utf-8")
    
    print("Archivos después de guardar:", os.listdir(output_path))  # Debug
    print(f"Nuevo archivo standings.csv guardado en {file_path}")