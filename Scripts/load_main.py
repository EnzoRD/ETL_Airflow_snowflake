from utils import upload_file_to_snowflake, load_csv_into_snowflake

def main():
    """Función para cargar `teams.csv` y `seasons.csv` en Snowflake."""

    # Subir los archivos al Stage de Snowflake
    upload_file_to_snowflake("teams.csv")
    upload_file_to_snowflake("seasons.csv")
    upload_file_to_snowflake("leagues.csv")

    # Cargar los archivos en las tablas de Snowflake
    load_csv_into_snowflake(
        "TEAMS",
        "teams.csv",
        ["TEAM_ID", "LEAGUE_CODE"], # Un equipo puede estar en varias ligas
        ["TEAM_ID", "TEAM_NAME", "SHORT_NAME", "TLA", "CREST_URL", "LEAGUE_CODE"])
    load_csv_into_snowflake(
        "SEASONS",
        "seasons.csv",
        ["LEAGUE_CODE", "SEASON_ID"], # Cada temporada es única por liga
        ["SEASON_ID", "SEASON_YEAR","START_DATE", "END_DATE", "IS_ACTIVE","LEAGUE_CODE"])
    load_csv_into_snowflake(
        "LEAGUES",
        "leagues.csv",
        ["LEAGUE_ID"], # Cada liga es única
        ["LEAGUE_ID", "LEAGUE_NAME"])


if __name__ == "__main__":
    main()
