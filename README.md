# Pipeline ETL de Clima + Calidad del Aire

Este es un pipeline ETL simple que:
1. Extrae datos del clima de la API de OpenWeatherMap
2. Extrae datos de calidad del aire de la API de AirVisual
3. Transforma y combina los datos usando dbt
4. Carga los resultados en una tabla analítica

## Requisitos Previos

Antes de comenzar, asegúrate de tener:
- Python 3.8 o superior instalado
- Git instalado
- Acceso a las claves API de OpenWeatherMap y AirVisual (puedes obtener niveles gratuitos para pruebas)

## Instrucciones de Configuración

Sigue estos pasos para configurar el proyecto:

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Crear y Activar un Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
# Asegurarse de que pip esté actualizado
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con tus claves API:
```
OPENWEATHER_API_KEY=tu_clave_api_de_openweathermap_aqui
AIRVISUAL_API_KEY=tu_clave_api_de_airvisual_aqui
```

> **Nota:** Nunca hagas commit de tu archivo `.env` al control de versiones. Ya está incluido en `.gitignore`.

### 5. Configurar dbt
```bash
# Navegar al directorio de dbt
cd dbt

# Instalar dependencias de dbt (si las hay)
dbt deps
```

### 6. Verificar la Configuración
Puedes comprobar que todo funciona correctamente ejecutando:
```bash
# Desde la raíz del proyecto
python -c "import pandas, requests, dotenv; print('Dependencias de Python OK')"

# Desde el directorio de dbt
cd dbt
dbt debug
# Debería mostrar: "Connection OK" y "All tests passed!"
```

## Estructura del Proyecto

```
weather-air-quality-pipeline/
├── src/
│   ├── extract_weather.py          # Extracción de datos del clima
│   └── extract_air_quality.py      # Extracción de datos de calidad del aire
├── dbt/
│   ├── models/
│   │   ├── stg_weather.sql
│   │   ├── stg_air_quality.sql
│   │   └── mart_weather_air_quality.sql
│   ├── tests/
│   │   └── schema_tests.yml
│   ├── dbt_project.yml
│   └── profiles.yml                # Configuración del perfil de dbt
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD con GitHub Actions
├── requirements.txt                # Dependencias de Python
├── .env                            # Variables de entorno (NO en el repo)
└── README.md
```

## Ejecutando el Pipeline

### 1. Extraer Datos
```bash
# Desde la raíz del proyecto
python src/extract_weather.py
python src/extract_air_quality.py
```
Esto creará archivos CSV en el directorio `data/`:
- `data/weather_raw.csv`
- `data/air_quality_raw.csv`

### 2. Transformar con dbt
```bash
# Desde el directorio de dbt
cd dbt
dbt run
```
Esto hará lo siguiente:
- Crear modelos de staging (`stg_weather`, `stg_air_quality`)
- Crear el modelo mart (`mart_weather_air_quality`)
- Guardar los resultados en una base de datos SQLite (`weather_air_quality.db`)

### 3. Ejecutar Pruebas
```bash
# Desde el directorio de dbt
dbt test
```
Esto ejecuta pruebas de datos y esquemas definidas en `dbt/tests/`

### 4. Ver Resultados (Opcional)
Puedes consultar los resultados usando SQLite:
```bash
sqlite3 dbt/weather_air_quality.db
```
Luego dentro de SQLite:
```sql
.headers on
.mode column
SELECT * FROM mart_weather_air_quality LIMIT 5;
```

## Flujo de Trabajo de Desarrollo

Para hacer cambios en este proyecto:

1. Crea una nueva rama: `git checkout -b feature/nombre-de-tu-funcionalidad`
2. Realiza tus cambios
3. Prueba localmente: Ejecuta la extracción, dbt run y dbt test
4. Haz un commit: `git add . && git commit -m "Tu mensaje descriptivo"`
5. Empuja los cambios: `git push origin feature/nombre-de-tu-funcionalidad`
6. Abre un Pull Request para revisión

## Solución de Problemas

### Problemas Comunes

**"ModuleNotFoundError: No module named 'pandas'"**
- Solución: Asegúrate de estar en el entorno virtual activado y de haber ejecutado `pip install -r requirements.txt`

**"dbt command not found"**
- Solución: Asegúrate de que dbt esté instalado (`pip install dbt-core dbt-sqlite`) y que tu entorno virtual esté activado

**"API key errors"**
- Solución: Verifica que tu archivo `.env` esté en la raíz del proyecto y contenga claves válidas
- Prueba con: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(bool(os.getenv('OPENWEATHER_API_KEY')))"`

**Errores "Database locked" con dbt**
- Solución: Asegúrate de que ningún otro proceso esté usando la base de datos SQLite. Elimina `dbt/weather_air_quality.db` y vuelve a ejecutar `dbt run` si es necesario.

## Pipeline de CI/CD

Este proyecto incluye un flujo de trabajo de GitHub Actions (`.github/workflows/ci.yml`) que automáticamente:
- Clona el código
- Configura Python
- Instala las dependencias
- Valida la sintaxis de Python
- Analiza el proyecto dbt
- Ejecuta las pruebas de dbt

El flujo de trabajo se ejecuta en cada push y pull request a la rama `main`.

## ¿Necesitas Ayuda?

Si encuentras problemas:
1. Revisa cada paso de la configuración
2. Asegúrate de que tu entorno virtual esté activado
3. Verifica que tus claves API sean válidas y no hayan expirado
4. Comprueba que estás ejecutando los comandos desde el directorio correcto
5. Busca el mensaje de error en internet - muchos problemas comunes tienen soluciones documentadas