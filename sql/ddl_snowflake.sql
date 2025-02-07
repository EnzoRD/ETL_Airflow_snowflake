CREATE STAGE "LEAGUES"."FOOTBALL".demo_stage;

-----------------------------------------------
-----------------------------------------------

-- Usar la base de datos leagues y el esquema football
USE DATABASE leagues;
CREATE SCHEMA IF NOT EXISTS football;

-- Crear la tabla de ligas
CREATE OR REPLACE TABLE football.leagues (
    league_id STRING PRIMARY KEY,  -- ID único de la liga (ej: 'PL', 'CL', 'BL1')
    league_name STRING UNIQUE      -- Nombre de la liga (ej: 'Premier League', 'Champions League')
);

-- Crear la tabla de temporadas con indicador de estado
CREATE OR REPLACE TABLE football.seasons (
    season_id INT AUTOINCREMENT PRIMARY KEY,  -- ID único de la temporada
    season_year INT UNIQUE,                   -- Año de la temporada (Ej: 2024)
    start_date DATE,                           -- Fecha de inicio de la temporada
    end_date DATE,                             -- Fecha de fin de la temporada
    is_active BOOLEAN DEFAULT TRUE             -- Indica si la temporada está en curso (TRUE = Activa, FALSE = Finalizada)
);

-- Crear la tabla de equipos
CREATE OR REPLACE TABLE football.teams (
    team_id INT PRIMARY KEY,  -- ID único del equipo según la API
    team_name STRING UNIQUE,  -- Nombre completo del equipo (Ej: 'Liverpool FC')
    short_name STRING,        -- Nombre corto (Ej: 'Liverpool')
    tla STRING,               -- Código de 3 letras del equipo (Ej: 'LIV' para Liverpool)
    crest_url STRING          -- URL del escudo del equipo
);

-- Crear la tabla standings con clustering para optimización
CREATE OR REPLACE TABLE football.standings (
    standing_id INT AUTOINCREMENT PRIMARY KEY, -- ID único de cada fila en la tabla standings
    league_id STRING REFERENCES football.leagues(league_id),
    season_id INT REFERENCES football.seasons(season_id),
    team_id INT REFERENCES football.teams(team_id),
    position INT,                 -- Posición en la tabla
    played_games INT,              -- Partidos jugados
    won INT,                       -- Partidos ganados
    draw INT,                      -- Partidos empatados
    lost INT,                      -- Partidos perdidos
    points INT,                    -- Puntos acumulados
    goals_for INT,                 -- Goles a favor
    goals_against INT,             -- Goles en contra
    goal_difference INT,           -- Diferencia de goles
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CLUSTER BY (league_id, season_id);  -- Mejora la velocidad de búsqueda por liga y temporada

-- Crear la tabla de histórico de standings para analizar cambios a lo largo del tiempo
CREATE OR REPLACE TABLE football.standings_history (
    history_id INT AUTOINCREMENT PRIMARY KEY,
    standing_id INT REFERENCES football.standings(standing_id),
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INT,
    points INT
);

list @demo_stage;

