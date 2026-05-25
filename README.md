# Pipeline ETL Clima + Calidad del Aire
### Template de Gobernanza de IA con Trunk-Based Development

> **Git ya no es una herramienta de control de versiones — es la única línea de defensa
> que tienes contra el código que genera la IA.**

[![CI](https://github.com/knowmads/git4scale/actions/workflows/ci.yml/badge.svg)](https://github.com/knowmads/git4scale/actions/workflows/ci.yml)

Este repositorio es el template utilizado en el workshop **"TBD para Data Engineering"**.
Demuestra cómo aplicar **Trunk-Based Development (TBD)** para gobernar la velocidad de
los agentes de IA en un pipeline de datos real.

---

## ¿Por qué este repositorio?

En la era de los agentes de IA (Cursor, Copilot, Claude), el volumen de código generado
se ha multiplicado por diez. El problema ya no es *escribir* código: es **auditarlo y
controlarlo**.

Sin una disciplina de integración continua y ramas cortas, cada línea que genera la IA
acumula lo que llamamos **Verification Debt** (deuda de verificación): código no validado,
posibles alucinaciones ocultas en ramas de larga duración, y conflictos masivos al momento
del merge.

Este pipeline demuestra el antídoto: **TBD + CI/CD automático**.

---

## El Pipeline

Un ETL modular, agnóstico de proveedores (lock-in free) que:

1. **Extrae** datos de clima desde la API de OpenWeatherMap (`src/extract_weather.py`)
2. **Extrae** datos de calidad del aire desde la API de AirVisual (`src/extract_air_quality.py`)
3. **Transforma** y combina los datos con dbt (`dbt/models/`)
4. **Carga** los resultados en una base de datos SQLite para analítica

---

## Estructura del Proyecto

```
git4scale/
├── src/
│   ├── extract_weather.py       # Script de extracción del clima (protagonista del workshop)
│   ├── extract_air_quality.py   # Script de extracción de calidad del aire
│   └── tests/
│       └── test_extract_weather.py  # Tests unitarios — el "freno de mano" del CI
├── dbt/
│   ├── models/
│   │   ├── stg_weather.sql
│   │   ├── stg_air_quality.sql
│   │   └── mart_weather_air_quality.sql
│   ├── tests/
│   └── dbt_project.yml
├── .github/
│   └── workflows/
│       └── ci.yml               # CI: pytest + dbt test (falla si hay alucinación)
├── preparacion/
│   ├── facilitator_guide_v2.md  # Guía completa para el video de 30 min
│   ├── facilitator_guide.md     # Guía del taller presencial de 90 min (V1)
│   ├── demo_alucinacion.py      # Código de referencia para la demo del error de IA
│   └── paso1_ana_weather_timeout.md  # Flujo paso a paso del caso Ana
├── requirements.txt
└── setup.sh
```

---

## Setup Rápido

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd git4scale

# 2. Setup automático (recomendado)
chmod +x setup.sh
./setup.sh
```

O manualmente:

```bash
# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env        # Edita con tus claves de API
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENWEATHER_API_KEY=tu_clave_aqui   # https://openweathermap.org/api
AIRVISUAL_API_KEY=tu_clave_aqui     # https://dashboard.iqair.com/personal/api-keys
```

> **Nota:** El archivo `.env` está en `.gitignore`. Nunca lo hagas commit.

---

## Reproducir la Demo del Workshop

### Paso 1 — Verificar que `main` está en verde

```bash
pytest src/tests/ -v   # Todos los tests deben pasar
```

### Paso 2 — Simular el flujo de Ana (la alucinación de la IA)

```bash
# Ana crea su rama corta
git checkout -b feature/weather-api-timeout

# Ana copia el código generado por la IA (con el parámetro alucinado)
# Ver: preparacion/demo_alucinacion.py

# Ana hace commit y push
git add src/extract_weather.py
git commit -m "feat: add exponential backoff to weather API calls"
git push origin feature/weather-api-timeout
```

El CI en GitHub Actions fallará en el paso **Run Python unit tests** con:
```
TypeError: requests.get() got an unexpected keyword argument 'exponential_decay'
```

### Paso 3 — Recuperación inmediata (el poder de TBD)

```bash
git revert HEAD --no-edit
git push origin feature/weather-api-timeout
```

El CI vuelve a verde ✅. El bug de la IA fue detectado en < 3 minutos, no en 2 semanas.

---

## CI/CD Pipeline

El workflow de GitHub Actions (`.github/workflows/ci.yml`) ejecuta en cada PR:

| Paso | Qué valida |
|------|-----------|
| `Check Python syntax` | Sintaxis básica (`py_compile`) |
| `Run Python unit tests` | **Tests unitarios con pytest** — detecta alucinaciones de parámetros |
| `dbt seed` | Carga datos de prueba |
| `dbt run` | Ejecuta los modelos de transformación |
| `dbt test` | Valida esquemas y datos |

> El paso `Run Python unit tests` es la clave de la demo: **falla** con el código
> alucinado por la IA y **pasa** con la implementación correcta.

---

## Flujo de Desarrollo (Trunk-Based Development)

```bash
# Siempre desde main actualizado
git checkout main
git pull origin main

# Rama corta (≤ 48 horas)
git checkout -b feature/tu-cambio

# Cambios pequeños, un solo enfoque
git add <archivos>
git commit -m "tipo: descripción concisa"

# Push + PR + esperar CI verde
git push origin feature/tu-cambio

# Merge a main y borrar rama
git checkout main
git merge feature/tu-cambio
git branch -d feature/tu-cambio
```

**Las 3 Reglas de Oro:**
1. 🕐 **Ramas ≤ 48 horas** — No acumules código sin integrar
2. 📏 **PRs ≤ 200 líneas** — Los humanos solo pueden auditar cambios pequeños
3. 🛡️ **CI obligatorio** — Ningún código llega a `main` sin pasar las pruebas

---

## Ejecutar el Pipeline Completo

```bash
# Extracción (requiere claves de API)
python src/extract_weather.py
python src/extract_air_quality.py

# Transformación con dbt
cd dbt
dbt seed
dbt run
dbt test

# Ver resultados
sqlite3 dbt/weather_air_quality.db
SELECT * FROM mart_weather_air_quality LIMIT 5;
```

---

## Solución de Problemas

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'pandas'` | Activa el entorno virtual y corre `pip install -r requirements.txt` |
| `dbt command not found` | `pip install dbt-core dbt-sqlite` con el entorno virtual activo |
| `API key errors` | Verifica que `.env` existe en la raíz con claves válidas |
| `sqlite3: command not found` | `sudo apt install sqlite3` (Linux) o `brew install sqlite` (macOS) |
| `Database locked` | Borra `dbt/weather_air_quality.db` y vuelve a ejecutar `dbt run` |

---

## Recursos del Workshop

| Recurso | Descripción |
|---------|-------------|
| [`preparacion/facilitator_guide_v2.md`](preparacion/facilitator_guide_v2.md) | Guía y guion completo del video de 30 min |
| [`preparacion/facilitator_guide.md`](preparacion/facilitator_guide.md) | Guía del taller presencial de 90 min (V1) |
| [`preparacion/demo_alucinacion.py`](preparacion/demo_alucinacion.py) | Código de referencia para la demo |
| [`preparacion/paso1_ana_weather_timeout.md`](preparacion/paso1_ana_weather_timeout.md) | Flujo detallado del caso Ana |
| [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com) | Guía definitiva de TBD |