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

    @staticmethod
    def get_response_weather(location, key=api_key):
        response = requests.get(
            f"https://api.weatherapi.com/v1/current.json?key={key}&q={location}&aqi=no")
        return json.loads(response.text), response.status_code

    @staticmethod
    def get_response_forecast(location, days, key=api_key):
        assert days in [1, 2, 3]
        response = requests.get(
            f"https://api.weatherapi.com/v1/forecast.json?key={key}&q={location}&days={days}&aqi=no&alerts=no")
        return json.loads(response.text), response.status_code
