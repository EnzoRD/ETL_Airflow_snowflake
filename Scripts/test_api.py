import pandas as pd
from typing import Dict, List, Optional
import requests
import sys
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
# Cargar el archivo .env desde la ruta especificada
load_dotenv(dotenv_path, override=True)


sys.stdout.reconfigure(encoding='utf-8')

# Configuración desde el archivo .env
API_KEY = os.getenv('API_KEY')

API_URL = "http://api.football-data.org/v4/competitions/{}/standings"
HEADERS = {"X-Auth-Token": API_KEY}

# Diccionario de ligas (Fácilmente actualizable)
LEAGUES = {
    "UEFA Champions League": "CL",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Premier League": "PL",
    "La Liga": "PD"
}

def fetch_standings(league_code: str) -> Optional[List[Dict]]:
    """
    Obtiene la tabla de posiciones de una liga específica.
    
    :param league_code: Código de la liga según football-data.org.
    :return: Lista con los datos de la tabla de posiciones o None si falla la solicitud.
    """
    url = API_URL.format(league_code)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        standings = data.get("standings", [])
        
        if not standings:
            print(f"⚠️ No se encontraron standings para {league_code}.")
            return None
        
        return standings[0].get("table", [])
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos para {league_code}: {e}")
        return None

def parse_standings(standings: List[Dict]) -> pd.DataFrame:
    """
    Convierte los datos de la tabla de posiciones en un DataFrame de Pandas.
    
    :param standings: Lista de diccionarios con la información de la tabla.
    :return: DataFrame con los datos de la liga.
    """
    teams_data = [
        [
            team["position"],
            team["team"]["name"],
            team["playedGames"],
            team["won"],
            team["draw"],
            team["lost"],
            team["points"],
            team["goalsFor"],
            team["goalsAgainst"]
        ]
        for team in standings
    ]
    
    columns = [
        "Position", "Team", "Played Games", "Won", "Draw", "Lost", 
        "Points", "Goals For", "Goals Against"
    ]
    
    return pd.DataFrame(teams_data, columns=columns)

def save_to_csv(df: pd.DataFrame, league_name: str):
    """
    Guarda un DataFrame en un archivo CSV.
    
    :param df: DataFrame con los standings de la liga.
    :param league_name: Nombre de la liga para nombrar el archivo.
    """
    file_name = f"standings_{league_name.replace(' ', '_').lower()}.csv"
    df.to_csv(file_name, index=False, encoding="utf-8")
    print(f"📁 Datos guardados en {file_name}")

def main():
    """
    Función principal que obtiene y muestra las tablas de posiciones de las ligas configuradas.
    """
    for league, code in LEAGUES.items():
        print(f"\n🏆 Tabla de posiciones - {league}\n")
        standings = fetch_standings(code)
        
        if standings:
            df = parse_standings(standings)
            print(df.to_string(index=False))
            save_to_csv(df, league)  # Guarda en CSV automáticamente

if __name__ == "__main__":
    main()
