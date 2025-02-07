# 📊 Football Data ETL: Python + Snowflake 🚀

Este proyecto implementa un **ETL (Extract, Transform, Load)** para obtener datos en tiempo real de **Football-Data.org**, procesarlos y almacenarlos en **Snowflake**.  
El diseño de la base de datos y las optimizaciones aplicadas garantizan **escalabilidad, eficiencia y fácil mantenimiento**.

---
## 📂 **Estructura del Proyecto**
📦 football-etl  
 ┣ 📂 dags                 # DAGs de Apache Airflow para la automatización del ETL  
 ┣ 📂 sql                  # DDL y queries SQL para Snowflake  
 ┃ ┣ 📄 ddl_snowflake.sql  # Definición de tablas y optimizaciones en Snowflake  
 ┣ 📂 scripts              # Código Python para la ETL  
 ┃ ┣ 📄 extract.py         # Obtiene datos de la API de Football-Data.org  
 ┃ ┣ 📄 transform.py       # Procesa y normaliza datos  
 ┃ ┣ 📄 load.py            # Carga los datos en Snowflake  
 ┣ 📂 config               # Archivos de configuración (.env, credenciales)  
 ┣ 📄 requirements.txt     # Dependencias del proyecto  
 ┣ 📄 README.md            # Este archivo  



---

## 🏗 **1. Modelado de la Base de Datos en Snowflake**
### 📌 **Tablas creadas y optimizaciones**
Para garantizar una estructura **limpia y eficiente**, dividimos la información en **múltiples tablas normalizadas**, en lugar de guardar todo en una sola tabla.  
Esta separación permite **manejar múltiples temporadas, optimizar consultas y evitar redundancia**.

### 🏆 **1.1 Tabla `leagues` (Ligas)**
| Campo      | Tipo    | Descripción |
|------------|--------|-------------|
| league_id  | STRING | Código único de la liga (Ej: 'PL', 'CL', 'BL1') |
| league_name | STRING | Nombre de la liga (Ej: 'Premier League') |

✅ **Motivo**:  
Evita repetir el nombre de la liga en cada registro de clasificación, optimizando almacenamiento y consultas.

---

### 📅 **1.2 Tabla `seasons` (Temporadas)**
| Campo      | Tipo      | Descripción |
|------------|----------|-------------|
| season_id  | INT (PK) | ID único de la temporada |
| season_year | INT (UNIQUE) | Año de la temporada (Ej: 2024) |
| start_date | DATE | Fecha de inicio |
| end_date   | DATE | Fecha de fin |
| is_active  | BOOLEAN | Indica si la temporada está en curso (`TRUE = Activa`) |

✅ **Motivo**:  
- Manejo de múltiples temporadas sin duplicar datos.  
- Permite saber si una temporada **está en curso o ya finalizó**.  
- Se actualiza automáticamente con `UPDATE seasons SET is_active = FALSE WHERE end_date < CURRENT_DATE;`

---

### 🏟 **1.3 Tabla `teams` (Equipos)**
| Campo      | Tipo    | Descripción |
|------------|--------|-------------|
| team_id    | INT (PK) | ID único del equipo |
| team_name  | STRING  | Nombre del equipo (Ej: 'Liverpool FC') |
| short_name | STRING  | Nombre corto (Ej: 'Liverpool') |
| tla        | STRING  | Código de 3 letras del equipo (Ej: 'LIV') |
| crest_url  | STRING  | URL del escudo del equipo |

✅ **Motivo**:  
- Evita **duplicar nombres de equipos en cada temporada**.  
- Facilita integraciones con otras bases de datos.

---

### 📊 **1.4 Tabla `standings` (Clasificación)**
| Campo         | Tipo      | Descripción |
|--------------|----------|-------------|
| standing_id  | INT (PK) | ID único de la fila |
| league_id    | STRING (FK) | Relación con `leagues` |
| season_id    | INT (FK) | Relación con `seasons` |
| team_id      | INT (FK) | Relación con `teams` |
| position     | INT      | Posición en la liga |
| played_games | INT      | Partidos jugados |
| won          | INT      | Partidos ganados |
| draw         | INT      | Partidos empatados |
| lost         | INT      | Partidos perdidos |
| points       | INT      | Puntos acumulados |
| goals_for    | INT      | Goles a favor |
| goals_against | INT     | Goles en contra |
| goal_difference | INT   | Diferencia de goles |
| last_updated | TIMESTAMP | Fecha de última actualización |

**✅ Optimización**:  
🚀 **`CLUSTER BY (league_id, season_id)`** → Acelera búsquedas por liga y temporada.  

---

### 📜 **1.5 Tabla `standings_history` (Histórico de posiciones)**
| Campo         | Tipo      | Descripción |
|--------------|----------|-------------|
| history_id   | INT (PK) | ID único |
| standing_id  | INT (FK) | Relación con `standings` |
| date_updated | TIMESTAMP | Fecha de actualización |
| position     | INT      | Posición en ese momento |
| points       | INT      | Puntos en ese momento |

✅ **Motivo**:  
- Permite **ver cómo evolucionó la clasificación a lo largo del tiempo**.  
- Útil para análisis históricos.

---

## 📧 **4. Contacto**
📌 **Autor:** [Enzo Ruiz Diaz](https://github.com/enzoruizdiaz)  
📌 **LinkedIn:** [linkedin.com/in/enzoruizdiaz](https://linkedin.com/in/enzoruizdiaz)
