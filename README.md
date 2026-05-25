# Pipeline ETL Clima + Calidad del Aire
## 🚀 Template de Gobernanza de IA con Trunk-Based Development (TBD)

> **Git ya no es solo una herramienta de control de versiones — es la única línea de defensa real que tienes contra el código alucinado por la IA.**

[![CI Pipeline](https://github.com/knowmads/git4scale/actions/workflows/ci.yml/badge.svg)](https://github.com/knowmads/git4scale/actions/workflows/ci.yml)

Este repositorio es el laboratorio interactivo y template oficial del workshop **"Git a Escala: Trunk-Based Development para Data Engineering"**. 

El objetivo de este proyecto es demostrar cómo un equipo de datos de alto rendimiento puede usar **TBD** e **Integración Continua (CI)** para auditar, probar y gobernar la velocidad de los cambios generados por agentes de Inteligencia Artificial (como Cursor, Copilot o ChatGPT) sin romper producción.

---

## 💡 El Modelo Mental: La Teoría de los Dos Escudos

Para dominar este proyecto y el flujo de trabajo moderno de ingeniería de datos, debes entender que el desarrollo se divide en dos niveles de validación:

```
                      ┌───────────────────────────────────────┐
                      │    Mesa de Trabajo Local (Manual)     │
                      │  - Requiere API Keys reales en .env   │
                      │  - Permite depurar y ver datos en vivo│
                      │  - Tu espacio libre de experimentación │
                      └──────────────────┬────────────────────┘
                                         │  git push / PR
                                         ▼
                      ┌───────────────────────────────────────┐
                      │    Aduana Central de Integración (CI)  │
                      │  - NO requiere API Keys (Mocks/Seeds) │
                      │  - Servidor limpio aislado en la nube │
                      │  - Freno de mano ante alucinaciones   │
                      └───────────────────────────────────────┘
```

1. **El Primer Escudo (Mesa de Trabajo Local):** Es tu laptop. Ejecutas los scripts manualmente, creas bases de datos locales y usas API Keys reales para conectarte a internet y depurar. Es donde creas y prototipas.
2. **El Segundo Escudo (Aduana de Integración Continua - CI):** Es un entorno hermético en la nube (GitHub Actions). Corre de forma automática en cada Pull Request. **No usa internet ni requiere API Keys** porque valida la sintaxis y la lógica utilizando **Mocks** (simulaciones de red) y **Seeds** (datos estáticos locales de dbt). Es el guardián de la rama principal (`main`).

---

## 🛠️ Setup Rápido (El Primer Escudo)

Sigue estos pasos para configurar tu **Mesa de Trabajo Local**:

### 1. Clonar el repositorio y entrar al directorio
```bash
git clone <repository-url>
cd git4scale
```

### 2. Configuración automática (Recomendado)
El script de configuración instalará el entorno virtual de Python, las dependencias del sistema (como `sqlite3`) y los paquetes necesarios automáticamente:
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configuración manual (Alternativa)
Si prefieres configurar paso a paso en tu máquina:
```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate       # En Windows
# source venv/bin/activate  # En macOS/Linux

# 2. Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno y API Keys
Para extraer datos en vivo localmente, necesitas credenciales gratuitas de las APIs públicas:
* Genera una clave API de clima en [OpenWeatherMap API](https://openweathermap.org/api).
* Genera una clave API de calidad de aire en [AirVisual IQAir](https://dashboard.iqair.com/personal/api-keys).

Crea un archivo `.env` en la raíz del proyecto y añade tus llaves:
```env
OPENWEATHER_API_KEY=tu_clave_de_openweathermap_aqui
AIRVISUAL_API_KEY=tu_clave_de_airvisual_aqui
```
> ⚠️ **Nota de Seguridad:** El archivo `.env` ya está en `.gitignore` para evitar que tus llaves privadas se publiquen en GitHub. Nunca lo hagas commit.

---

## 🏃 Ejecución Local del Pipeline (Mesa de Trabajo)

Una vez configuradas tus claves en el `.env`, puedes ejecutar los engranajes del pipeline manualmente:

### 1. Extraer los datos crudos en vivo
```bash
python src/extract_weather.py
python src/extract_air_quality.py
```
Esto consultará las APIs y generará dos archivos CSV locales en la carpeta `data/`:
* `data/weather_raw.csv`
* `data/air_quality_raw.csv`

### 2. Transformar los datos con dbt
Navega al directorio de dbt y ejecuta los modelos para limpiar los datos crudos y unirlos en una base de datos SQLite analítica:
```bash
cd dbt
dbt seed     # Carga tablas de referencia
dbt run      # Ejecuta las transformaciones SQL (staging y mart)
dbt test     # Ejecuta pruebas de calidad de datos
```

### 3. Consultar la base de datos resultante
Puedes verificar los datos resultantes usando el cliente de SQLite del sistema:
```bash
sqlite3 weather_air_quality.db
```
Dentro de la consola de SQLite:
```sql
.headers on
.mode column
SELECT city, weather_temperature, aqi, weather_description FROM mart_weather_air_quality LIMIT 5;
.quit
```

---

## 🛡️ La Aduana Automatizada (El Segundo Escudo - CI/CD)

En un entorno corporativo o al trabajar con agentes de IA rápidos, las pruebas manuales locales no bastan porque los humanos olvidamos ejecutarlas o configuramos cosas diferentes en cada máquina. 

Para resolver esto, el repositorio incluye un pipeline automatizado de **GitHub Actions** (`.github/workflows/ci.yml`) que actúa en cada Pull Request y ejecuta:

1. **Check Python syntax:** Valida que el código de Python sea sintácticamente correcto.
2. **Run Python unit tests:** **La clave del taller.** Ejecuta pruebas unitarias (`pytest`) usando *mocks* (respuestas de red simuladas). Detecta parámetros inexistentes o alucinados en segundos **sin requerir API Keys**.
3. **dbt validation:** Corre `dbt seed`, `dbt run` y `dbt test` en una base SQLite aislada en la nube usando datos fijos locales para comprobar que el SQL analítico no tenga fallas de lógica.

---

## 🧪 Cómo reproducir la Demo del Workshop (El Caso Ana)

El workshop te invita a simular cómo la IA puede alucinar un cambio y cómo el **CI (Segundo Escudo)** salva al equipo en 3 minutos.

### Paso 1 — Crear una rama feature corta
```bash
# Siempre partiendo de main actualizado
git checkout main
git pull origin main

# Crea la rama de Ana
git checkout -b feature/weather-api-timeout
```

### Paso 2 — Aplicar el cambio alucinado de la IA
Simula que le pides a una IA que añada lógica de reintentos a `src/extract_weather.py` y la IA alucina agregando un parámetro inexistente en la librería `requests` (`exponential_decay=True`).
1. Abre [preparacion/demo_alucinacion.py](preparacion/demo_alucinacion.py).
2. Copia la sección marcada como `CÓDIGO ALUCINADO` y reemplaza el contenido de `src/extract_weather.py`.
3. Haz commit y push de esta rama:
```bash
git add src/extract_weather.py
git commit -m "feat: add exponential backoff to weather API calls"
git push origin feature/weather-api-timeout
```

### Paso 3 — Observar el CI fallando
Ve a la pestaña de **Pull Requests** o **Actions** en tu repositorio de GitHub. Verás que el pipeline de CI falla inmediatamente en el paso `Run Python unit tests` arrojando:
```
TypeError: requests.get() got an unexpected keyword argument 'exponential_decay'
```
**¡No se necesitaron configurar claves API secretas en GitHub para detectar esta alucinación!** El test unitario local interceptó la llamada y la validó de forma hermética.

### Paso 4 — Recuperación Inmediata (Trunk-Based Development)
Dado que el cambio de Ana es diminuto (< 50 líneas) y aislado, el Tech Lead no pasa horas depurando. Simplemente aplica un revert inmediato para mantener `main` sano:
```bash
git revert HEAD --no-edit
git push origin feature/weather-api-timeout
```
El pipeline de CI vuelve a estar en **verde ✅**. Ahora, Ana puede aplicar el fix correcto (ver `preparacion/demo_alucinacion.py` versión correcta) de forma segura.

---

## 🏆 Las 3 Reglas de Oro de Trunk-Based Development

Para trabajar a escala y gobernar la velocidad de la IA en equipos modernos de datos:

1. 🕐 **Ramas cortas (≤ 24-48 horas):** No acumules código en ramas privadas. Integra rápido para que tus compañeros y el CI detecten las incompatibilidades de inmediato.
2. 📏 **Pull Requests pequeñas (≤ 200 líneas):** El ojo humano no puede auditar con precisión 1,000 líneas generadas por una máquina. Cambios pequeños son audtables y fáciles de revertir.
3. 🛡️ **CI obligatorio y hermético:** Ningún código toca la rama principal sin pasar las pruebas. Las pruebas deben usar *Mocks* y *Seeds* para correr rápido, ser independientes de internet y no costar dinero de APIs.

---

## 🛠️ Solución de Problemas Frecuentes

| Error / Síntoma | Causa probable | Solución |
|-----------------|----------------|----------|
| `ModuleNotFoundError: No module named 'pandas'` | Entorno virtual desactivado o dependencias no instaladas. | Activa tu venv (`venv\Scripts\activate`) y ejecuta `pip install -r requirements.txt`. |
| `dbt command not found` | dbt-core no está instalado en el entorno activo. | Ejecuta `pip install dbt-core dbt-sqlite` con el entorno virtual activado. |
| `API key errors` | Falta el archivo `.env` o las claves son inválidas. | Crea el archivo `.env` en la raíz del proyecto usando el formato indicado en la guía. |
| `No se ha encontrado la orden sqlite3` | sqlite3 no está instalado a nivel del sistema operativo. | En Linux/WSL: `sudo apt install sqlite3`. En macOS: `brew install sqlite`. O corre `./setup.sh`. |
| `Database locked` (en dbt) | Otro proceso o herramienta de base de datos mantiene bloqueado el archivo SQLite. | Cierra clientes de bases de datos que tengan abierta la conexión. Si persiste, borra `dbt/weather_air_quality.db` y ejecuta `dbt run` de nuevo. |

---

## 📚 Recursos Adicionales

* [Guía del Facilitador V3](preparacion/facilitator_guide_v3.md) — Estructura pedagógica del video de 30 minutos.
* [Paso 1 — Guía de Ana](preparacion/paso1_ana_weather_timeout.md) — Instrucciones paso a paso del ejercicio de Ana.
* [Paso 2 — Guía de Bruno](preparacion/paso2_bruno_aqi_calculation.md) — Ejercicio de Bruno y dbt.
* [Sitio Oficial de Trunk-Based Development](https://trunkbaseddevelopment.com) — Buenas prácticas de Git a escala.