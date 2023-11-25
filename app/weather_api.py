import requests
import json
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class WeatherApi:
    api_key = os.environ.get("API_KEY")

    @staticmethod
    def get_response_history(location, date, key=api_key):
        response = requests.get(
            f"https://api.weatherapi.com/v1/history.json?key={key}&q={location}&dt={date}")
        return json.loads(response.text), response.status_code
