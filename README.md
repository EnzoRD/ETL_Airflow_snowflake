# 📊 ETL de Datos de Fútbol con Snowflake y Airflow

Este proyecto implementa un pipeline ETL utilizando Apache Airflow y Snowflake para extraer, transformar y cargar datos de ligas de fútbol.

---


## 📄 **1. Descripción General**

Este proyecto permite la integración de datos de ligas de fútbol en Snowflake mediante un pipeline ETL automatizado con Airflow.

---

## 🏗 **2. Arquitectura del Proyecto**

El flujo de trabajo sigue las siguientes fases:
1. **Extracción**: Se consultan datos de la API y se guardan en archivos CSV.
2. **Transformación**: Se validan y ajustan los datos antes de la carga.
3. **Carga**: Los datos se suben a Snowflake, evitando duplicados mediante `MERGE`.

---
---

## 📥 **3. Extracción de Datos**

- Se obtienen datos de ligas, temporadas, equipos y clasificaciones desde la API `Football-Data.org`, incluyendo:
- **Ligas** (`LEAGUES`)
- **Equipos** (`TEAMS`)
- **Temporadas** (`SEASONS`)
- **Clasificaciones** (`STANDINGS` - actualizadas semanalmente)

---

## 🔄 **4. Transformación de Datos**

- Normalización de los datos y conversión a formato CSV.
- Uso de `MERGE` en Snowflake para evitar duplicados.
- Definición de `FILE_FORMAT` para facilitar la carga de archivos.

---

## 📤 **5. Carga de Datos en Snowflake**

- Se suben los CSV a un `STAGE` en Snowflake.
- Se usa `MERGE` para insertar y actualizar registros sin duplicados.
- **Carga diferenciada:**
  - `LEAGUES`, `TEAMS` y `SEASONS` se actualizan **una vez al año**.
  - `STANDINGS` se actualiza **semanalmente** con un DAG incremental en Airflow.
  - 
---

---

## 🛠 **6. Modelo de Datos**

A continuación, se presenta la estructura de las tablas utilizadas en Snowflake:

### **6.1 Tabla `LEAGUES` (Ligas)**
| Campo       | Tipo                | Descripción                          |
|------------|--------------------|--------------------------------------|
| LEAGUE_ID  | VARCHAR(16777216) (PK) | Código de la liga (Ej: 'PL', 'CL') |
| LEAGUE_NAME| VARCHAR(16777216)  | Nombre de la liga (Ej: 'Premier League') |

### **6.2 Tabla `SEASONS` (Temporadas)**
| Campo       | Tipo                | Descripción                              |
|------------|--------------------|------------------------------------------|
| SEASON_ID  | NUMBER(38,0) (PK)  | Identificador único de la temporada     |
| SEASON_YEAR| VARCHAR(16777216)  | Año de la temporada (Ej: '2024/2025')   |
| START_DATE | DATE               | Fecha de inicio                         |
| END_DATE   | DATE               | Fecha de finalización                   |
| IS_ACTIVE  | BOOLEAN            | Indica si la temporada está en curso    |
| LEAGUE_CODE| VARCHAR(16777216) (FK) | Código de la liga                      |

### **6.3 Tabla `TEAMS` (Equipos)**
| Campo       | Tipo                | Descripción                               |
|------------|--------------------|-------------------------------------------|
| TEAM_ID    | NUMBER(38,0) (PK)  | Identificador único del equipo           |
| TEAM_NAME  | VARCHAR(16777216)  | Nombre completo del equipo               |
| SHORT_NAME | VARCHAR(16777216)  | Nombre corto del equipo                  |
| TLA        | VARCHAR(16777216)  | Código de 3 letras del equipo (Ej: 'LIV')|
| CREST_URL  | VARCHAR(16777216)  | URL del escudo del equipo                |
| LEAGUE_CODE| VARCHAR(16777216) (FK) | Código de la liga                      |

### **6.4 Tabla `STANDINGS` (Clasificaciones)**
| Campo          | Tipo                | Descripción                                  |
|---------------|--------------------|----------------------------------------------|
| STANDING_ID  | NUMBER(38,0) (PK)  | Identificador único de la clasificación     |
| LEAGUE_ID    | VARCHAR(16777216) (FK) | Código de la liga                          |
| SEASON_ID    | NUMBER(38,0) (FK)  | Identificador de la temporada              |
| TEAM_ID      | NUMBER(38,0) (FK)  | Identificador del equipo                   |
| POSITION     | NUMBER(38,0)       | Posición en la tabla                       |
| PLAYED_GAMES | NUMBER(38,0)       | Partidos jugados                           |
| WON          | NUMBER(38,0)       | Partidos ganados                           |
| DRAW         | NUMBER(38,0)       | Partidos empatados                         |
| LOST         | NUMBER(38,0)       | Partidos perdidos                          |
| POINTS       | NUMBER(38,0)       | Puntos totales                             |
| GOALS_FOR    | NUMBER(38,0)       | Goles a favor                              |
| GOALS_AGAINST| NUMBER(38,0)       | Goles en contra                            |
| GOAL_DIFFERENCE | NUMBER(38,0)    | Diferencia de goles                        |
| LAST_UPDATED | TIMESTAMP          | Última actualización                       |

---

## ✅ Estado Actual
✔ **Implementado:**
- **Extracción y transformación** de `LEAGUES`, `TEAMS` y `SEASONS`.
- **Carga a Snowflake** con `MERGE` para evitar duplicados.
- **Definición de formatos de archivo y optimización de carga.**

🔜 **Próximos Pasos:**
- Implementar la **carga incremental de `STANDINGS`** con Airflow.
- Optimizar consultas en Snowflake para mejorar la performance.
- Automatizar el pipeline completamente en Airflow.

## 📂 Estructura del Proyecto
```
ETL_Airflow_Snowflake/
│── Scripts/
│   ├── extract_main.py  # Ejecuta la extracción de datos
│   ├── load_main.py     # Carga los datos en Snowflake
│   ├── utils.py         # Funciones auxiliares
│── dags/
│   ├── etl_pipeline.py  # DAG de Airflow
│── data/                # Archivos CSV generados
│── README.md            # Documentación del proyecto
```

## 📌 Configuración y Ejecución
1. **Configurar variables de entorno en Airflow UI** (Snowflake credentials, rutas, etc.).
2. **Ejecutar `extract_main.py`** para generar los CSV.
3. **Ejecutar `load_main.py`** para cargar datos a Snowflake.
4. **Configurar Airflow DAG** para la carga incremental de `STANDINGS`.

## 📌 Tecnologías Utilizadas
- **Python** (pandas, requests, Snowflake connector)
- **Airflow** (para la orquestación del pipeline)
- **Snowflake** (almacenamiento de datos y consultas optimizadas)
- **Football-Data.org API** (fuente de datos)

---
📌 **Autor:** Enzo Ruiz Diaz  
📌 **Contacto:** [LinkedIn](https://www.linkedin.com/in/enzo-ruiz-diaz)  
🚀 **Última actualización:** Febrero 2025
