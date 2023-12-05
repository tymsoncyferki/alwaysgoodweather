import os

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame

data_path = os.environ.get("LOC_DATA")

"""
Set of functions to create dataframe 
"""


def add_data(df, variables, columns=None):
    if columns is None:
        columns = ['city', 'country', 'continent', 'latitude', 'longitude', 'mintemp_his', 'maxtemp_his', 'avgtemp_his']
    row = pd.DataFrame([variables], columns=columns)
    df = pd.concat([df, row])
    return df


def get_historical_data(location_name):
    """
    This function analyzes the last year of weather in the provided location. It aggregates data - extracts max, min
    and average temperature.
    :param location_name:
    :return: aggregated temperature and location data
    """
    from app.weather_api import WeatherApi
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
    df.to_csv(data_path, index=False)
    return df


def allocate_data(df, continent, mintemp, maxtemp, avgtemp):
    df.loc[df['continent'] == continent, 'mintemp'] = mintemp
    df.loc[df['continent'] == continent, 'maxtemp'] = maxtemp
    df.loc[df['continent'] == continent, 'avgtemp'] = avgtemp
    return df


def generate_points(num_points, index, model):
    latitudes = np.linspace(-90, 90, int(np.sqrt(num_points)))
    longitudes = np.linspace(-180, 180, int(2 * np.sqrt(num_points)))

    points = []
    for lat in latitudes:
        for lon in longitudes:
            point = (lat, lon)
            temperature = model.predict(np.array([[lat, lon]]))
            points.append((point[0], point[1], temperature[0][index]))

    return points


def plot_map(num_points, index, model, marker_size):

    points = generate_points(num_points, index, model)
    df = pd.DataFrame(points, columns=['latitude', 'longitude', 'temperature'])

    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)

    world = gpd.read_file('data/maps/ne_110m_admin_0_countries.shp')

    ax = world.plot(figsize=(10, 6))
    gdf.plot(ax=ax, marker='s', c=gdf['temperature'], markersize=marker_size, legend=True, alpha=0.4)
