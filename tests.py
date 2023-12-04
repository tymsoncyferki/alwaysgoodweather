import unittest
from app.data.data import get_historical_data
from app.weather_api import WeatherApi
from datetime import datetime, timedelta


class TestWeatherApi(unittest.TestCase):

    def test_get_response_history(self):
        today = datetime.now() - timedelta(days=3)
        date = today.strftime('%Y-%m-%d')
        response, code = WeatherApi.get_response_history("piaseczno", date)

        self.assertEqual(code, 200)
        self.assertEqual(response['location']['name'], "Piaseczno")
        self.assertEqual(response['location']['lat'], 52.08)
        self.assertEqual(response['location']['lon'], 21.03)

    def test_get_response_forecast(self):
        response, code = WeatherApi.get_response_forecast("Warszawa", days=3)
        today = datetime.now() + timedelta(days=2)
        date = today.strftime('%Y-%m-%d')

        self.assertEqual(code, 200)
        self.assertEqual(response['forecast']['forecastday'][2]['date'], date)

    def test_get_response_weather(self):
        response, code = WeatherApi.get_response_weather("40,20")

        self.assertEqual(code, 200)
        self.assertEqual(response['location']['name'], 'Delvine')


class TestData(unittest.TestCase):

    def test_add_data(self):
        pass

    def test_get_historical_data(self):
        """
        This function requires premium weatherapi key
        """
        variables = get_historical_data('miejsce_ktore_nie_istnieje')

        self.assertEqual(variables, [])

    def test_allocate_data(self):
        pass
