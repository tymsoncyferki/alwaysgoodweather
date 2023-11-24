import requests
import json


class WeatherApi:
    api_key = "797dbfda9acd48d6abb182425232111"

    @staticmethod
    def get_response_history(location, date):
        response = requests.get(
            f"https://api.weatherapi.com/v1/history.json?key={WeatherApi.api_key}&q={location}&dt={date}")
        return json.loads(response.text), response.status_code
