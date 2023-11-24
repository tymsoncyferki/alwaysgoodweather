import unittest
from weather_api import WeatherApi
from datetime import datetime, timedelta


class TestWeatherApi(unittest.TestCase):

    def test_get_response_history(self):
        today = datetime.now() - timedelta(days=3)
        date = today.strftime('%Y-%m-%d')
        response, code = WeatherApi.get_response_history("piaseczno", date)

        self.assertEqual(code, 200)

        self.assertEqual(response['location']['lat'], 52.08)
        self.assertEqual(response['location']['lon'], 21.03)
        self.assertEqual(response['location']['name'], "Piaseczno")
