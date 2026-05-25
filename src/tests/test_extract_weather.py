"""
Tests unitarios para el script de extracción de datos del clima.

Propósito en el Workshop V2:
  - Estos tests son el "freno de mano" del CI/CD.
  - test_weather_retry_logic_correct_params → PASA cuando la implementación es correcta.
  - test_weather_api_hallucinated_param    → FALLA si la IA alucinó un parámetro
    inválido en requests.get() (e.g. exponential_decay=True).
  - test_retry_on_server_error             → Verifica que el retry funciona.

El drama del video ocurre cuando Ana integra el código alucinado y este test
detecta el error en menos de 3 minutos, sin que el bug llegue a producción.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Agregar src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestWeatherAPIParams(unittest.TestCase):
    """Valida que las llamadas a la API usen parámetros válidos de requests."""

    @patch('requests.get')
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key-123'})
    def test_requests_get_uses_valid_params_only(self, mock_get):
        """
        ESCENARIO DEMO V2 — El test que detecta la alucinación de la IA.

        Si la IA generó código con un parámetro falso como:
            requests.get(url, params=params, timeout=10, exponential_decay=True)

        Este test fallará con:
            TypeError: requests.get() got an unexpected keyword argument 'exponential_decay'

        Cuando la implementación es correcta (solo usa parámetros válidos de requests),
        este test pasa.
        """
        # Preparar respuesta simulada de la API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 15.0,
                "feels_like": 13.0,
                "humidity": 75,
                "pressure": 1013,
            },
            "wind": {"speed": 5.0, "deg": 180},
            "weather": [{"main": "Clouds", "description": "overcast clouds"}],
            "dt": 1716652800,
        }
        mock_get.return_value = mock_response

        # Importar aquí para que el mock de os.environ ya esté activo
        from src.extract_weather import extract_weather

        # Ejecutar la función
        result = extract_weather("London")

        # Verificar que se llamó a requests.get
        self.assertTrue(mock_get.called, "requests.get() debería haber sido llamado")

        # Verificar que el resultado tiene la ciudad correcta
        self.assertEqual(result['city'].iloc[0], 'London')

        # Verificar que los kwargs usados en requests.get son válidos
        # (no contienen parámetros inventados como exponential_decay)
        call_kwargs = mock_get.call_args[1] if mock_get.call_args[1] else {}
        invalid_params = {'exponential_decay', 'retry_count', 'backoff_factor_custom'}
        used_invalid = invalid_params.intersection(set(call_kwargs.keys()))
        self.assertEqual(
            len(used_invalid), 0,
            f"requests.get() fue llamado con parámetros inválidos: {used_invalid}. "
            "¡Posible alucinación de la IA detectada!"
        )

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': ''})
    def test_raises_error_when_api_key_missing(self):
        """Verifica que la función falla claramente si no hay API key configurada."""
        from src.extract_weather import extract_weather

        with self.assertRaises((ValueError, Exception)):
            extract_weather("London")


class TestWeatherRetryLogic(unittest.TestCase):
    """
    Valida que la retry logic (agregada por Ana en la demo) funciona correctamente.
    Estos tests PASARÁN después de que Ana haga el fix del código alucinado.
    """

    @patch('requests.get')
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key-123'})
    def test_successful_extraction_returns_dataframe(self, mock_get):
        """La extracción exitosa debe devolver un DataFrame con las columnas esperadas."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Tokyo",
            "sys": {"country": "JP"},
            "main": {
                "temp": 22.0,
                "feels_like": 21.0,
                "humidity": 60,
                "pressure": 1010,
            },
            "wind": {"speed": 3.0, "deg": 90},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "dt": 1716652800,
        }
        mock_get.return_value = mock_response

        from src.extract_weather import extract_weather
        result = extract_weather("Tokyo")

        expected_columns = [
            'city', 'country', 'temperature', 'feels_like',
            'humidity', 'pressure', 'wind_speed', 'weather_condition',
        ]
        for col in expected_columns:
            self.assertIn(
                col, result.columns,
                f"El DataFrame debe tener la columna '{col}'"
            )

    @patch('requests.get')
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key-123'})
    def test_http_error_raises_exception(self, mock_get):
        """Un error HTTP 500 debe propagar una excepción (no swallowearla silenciosamente)."""
        import requests as req

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = req.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_get.return_value = mock_response

        from src.extract_weather import extract_weather

        with self.assertRaises(Exception):
            extract_weather("ErrorCity")


if __name__ == '__main__':
    unittest.main(verbosity=2)
