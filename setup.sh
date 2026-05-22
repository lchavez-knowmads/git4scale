#!/usr/bin/env bash
# =============================================================================
# setup.sh — Configuración del entorno para el pipeline ETL Clima + Calidad del Aire
# =============================================================================
# Uso:
#   chmod +x setup.sh
#   ./setup.sh
# =============================================================================

set -euo pipefail

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "============================================================"
echo "  Setup: Pipeline ETL Clima + Calidad del Aire"
echo "============================================================"
echo ""

# -----------------------------------------------------------------------------
# 1. Dependencias del sistema
# -----------------------------------------------------------------------------
info "Verificando dependencias del sistema..."

# Python
if ! command -v python3 &>/dev/null; then
    error "Python 3 no está instalado. Instálalo desde https://www.python.org/ o con: sudo apt install python3"
fi
info "Python $(python3 --version) ✓"

# SQLite3 (CLI)
if ! command -v sqlite3 &>/dev/null; then
    warning "sqlite3 CLI no encontrado. Intentando instalar..."
    if command -v apt &>/dev/null; then
        sudo apt update -qq && sudo apt install -y sqlite3
        info "sqlite3 instalado ✓"
    elif command -v brew &>/dev/null; then
        brew install sqlite
        info "sqlite3 instalado ✓"
    else
        error "No se pudo instalar sqlite3 automáticamente. Instálalo manualmente: sudo apt install sqlite3"
    fi
else
    info "sqlite3 $(sqlite3 --version | cut -d' ' -f1) ✓"
fi

# Git
if ! command -v git &>/dev/null; then
    error "Git no está instalado. Instálalo desde https://git-scm.com/"
fi
info "Git $(git --version | cut -d' ' -f3) ✓"

# -----------------------------------------------------------------------------
# 2. Entorno virtual de Python
# -----------------------------------------------------------------------------
echo ""
info "Configurando entorno virtual de Python..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    info "Entorno virtual creado en ./venv ✓"
else
    info "Entorno virtual ya existe en ./venv ✓"
fi

# Activar entorno virtual
# shellcheck disable=SC1091
source venv/bin/activate
info "Entorno virtual activado ✓"

# -----------------------------------------------------------------------------
# 3. Dependencias de Python
# -----------------------------------------------------------------------------
echo ""
info "Instalando dependencias de Python..."

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
info "Dependencias de Python instaladas ✓"

# Verificar importaciones clave
python3 -c "import pandas, requests, dotenv; print('  pandas, requests, dotenv OK')" \
    && info "Verificación de paquetes Python ✓" \
    || error "Algún paquete de Python falló al importarse"

# -----------------------------------------------------------------------------
# 4. Configuración de dbt
# -----------------------------------------------------------------------------
echo ""
info "Configurando dbt..."

cd dbt
dbt deps --quiet 2>&1 | grep -v "^$" | head -5 || true
info "dbt deps completado ✓"
cd ..

# -----------------------------------------------------------------------------
# 5. Archivo .env
# -----------------------------------------------------------------------------
echo ""
if [ ! -f ".env" ]; then
    warning "No se encontró el archivo .env"
    echo ""
    echo "  Crea el archivo .env en la raíz del proyecto con:"
    echo ""
    echo "    OPENWEATHER_API_KEY=tu_clave_aqui"
    echo "    AIRVISUAL_API_KEY=tu_clave_aqui"
    echo ""
    echo "  Obtén tus claves en:"
    echo "    - https://openweathermap.org/api"
    echo "    - https://dashboard.iqair.com/personal/api-keys"
    echo ""
else
    info "Archivo .env encontrado ✓"
fi

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "============================================================"
info "¡Setup completado!"
echo ""
echo "  Próximos pasos:"
echo "    1. Asegúrate de tener el archivo .env con tus API keys"
echo "    2. Activa el entorno virtual: source venv/bin/activate"
echo "    3. Extrae datos:              python src/extract_weather.py"
echo "                                  python src/extract_air_quality.py"
echo "    4. Transforma con dbt:        cd dbt && dbt run"
echo "    5. Verifica resultados:       sqlite3 dbt/weather_air_quality.db"
echo "============================================================"
echo ""
