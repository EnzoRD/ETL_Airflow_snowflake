import os
import pandas as pd
import requests
from typing import Optional, Dict
from typing import List, Dict
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding='utf-8')
from utils import (
    LEAGUES, fetch_standings_all, extract_season, extract_leagues, fetch_teams_from_standings,
    fetch_standings_from_json, save_teams_to_csv, save_standings_to_csv
)

def main():
    """Función principal para extraer y guardar datos de la temporada, equipos y standings."""
    output_directory = r"C:\Users\enzor\Documents\Proyectos\Proyecto 2 ETL\ETL_Airflow_snowflake\Data"
    os.makedirs(output_directory, exist_ok=True)

    # Extraer datos de las ligas
    extract_leagues(output_directory)
    
    # Extraer datos de la temporada, equipos y standings
    
    all_teams = []
    #all_standings = []
    

    for league_code in LEAGUES.keys():
        print(f"📡 Obteniendo datos para {league_code}...")
        data = fetch_standings_all(league_code)
        if data:
            extract_season(data, output_directory, league_code)

            teams = fetch_teams_from_standings(league_code)
            all_teams.extend(teams)

            #standings = fetch_standings_from_json(data, league_code)
            #all_standings.extend(standings)

    if all_teams:
        save_teams_to_csv(all_teams, output_directory)

    #if all_standings:
        #save_standings_to_csv(all_standings, output_directory)

if __name__ == "__main__":
    main()
