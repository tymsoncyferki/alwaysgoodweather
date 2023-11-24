import requests
import json
from datetime import datetime, timedelta
import pandas as pd


class WeatherApi:
    api_key = "797dbfda9acd48d6abb182425232111"

    @staticmethod
    def get_response_history(location, date, key=api_key):
        response = requests.get(
            f"https://api.weatherapi.com/v1/history.json?key={key}&q={location}&dt={date}")
        return json.loads(response.text), response.status_code


def add_data(df, variables, columns=None):
    if columns is None:
        columns = ['city', 'country', 'continent', 'latitude', 'longitude', 'mintemp_his', 'maxtemp_his', 'avgtemp_his']
    row = pd.DataFrame([variables], columns=columns)
    df = pd.concat([df, row])
    return df


def get_historical_data(location_name):
    maxtemp_his = -50
    mintemp_his = 50
    avgtemp_his = 0
    city = ''
    country = ''
    continent = ''
    latitude = 0
    longitude = 0

    variables = []
    error = False
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    current_date = start_date

    while current_date <= end_date:
        if current_date.day == 1:
            print(current_date.strftime('%Y-%m-%d'))

        response, code = WeatherApi.get_response_history(location_name, current_date)

        if code != 200:
            print(f'status code {code}')
            if current_date == start_date:
                print(response)
                error = True
                break
            continue

        if current_date == start_date:
            location = response["location"]
            city = location["name"]
            country = location["country"]
            continent = location["tz_id"].split('/')[0]
            latitude = location['lat']
            longitude = location['lon']
            print(city)

        day = response["forecast"]["forecastday"][0]["day"]

        if day['maxtemp_c'] > maxtemp_his:
            maxtemp_his = day['maxtemp_c']
        if day['mintemp_c'] < mintemp_his:
            mintemp_his = day['mintemp_c']
        avgtemp_his += day['avgtemp_c']

        current_date = current_date + timedelta(days=1)

    avgtemp_his = round(avgtemp_his / 365, 1)

    if not error:
        variables = [city, country, continent, latitude, longitude, mintemp_his, maxtemp_his, avgtemp_his]

    return variables


def save_historical_data(df, location):
    variables = get_historical_data(location)
    df = add_data(df, variables)
    df.reset_index(drop=True)
    df.to_csv("locations.csv")


