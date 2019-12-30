import os
import tqdm
import sys
import json
import datetime
from stravalib.client import Client
import pandas as pd
import argparse

import polygon
import model

SECRET = os.getenv("STRAVA")
TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
CLIENT_ID = 24270
TYPES = ['time', 'latlng', 'altitude']
ATHLETE = 'benjamin'

cp_filepath = "data/geojson/the_bridle.json"


def get_geojson(filepath):
    file = open(filepath, "r")
    return json.load(file)


def get_coordinates_json(filepath):
    data = get_geojson(filepath)
    return data


def get_coordinates_list(filepath, p=True):
    data = get_coordinates_json(filepath)['features'][0]['geometry']['coordinates']
    if p:
        return data[0]
    return data


def get_strava_gpx_dataframe(activity_id, strava_client, TYPES=['time', 'latlng', 'altitude']):
    streams = strava_client.get_activity_streams(activity_id, resolution='medium', types=TYPES)
    if not streams:
        return pd.DataFrame([])
    elif 'latlng' not in streams.keys():
        return pd.DataFrame([])
    latlng = pd.DataFrame(streams['latlng'].data, columns=['latitude', 'longitude'])
    time = pd.DataFrame(streams['time'].data, columns=['time'])
    if 'altitude' in streams.keys():
        altitude = pd.DataFrame(streams['altitude'].data, columns=['elevation'])
        return pd.concat([latlng, altitude, time], axis=1)
    return pd.concat([latlng, time])


def strava_run_totals(activity_id, client):
    df = get_strava_gpx_dataframe(activity_id, client)
    if len(df) > 0:
        df = df.assign(inside=lambda d: d.apply(polygon.row_inside_polygon, args=[data], axis=1))
        if 'elevation' in df.columns:
            return polygon.totals_inside_polygon(df)
        else:
            return polygon.twoD_total_inside_polygon(df)
    else:
        return pd.Series()


def calculate_epoch(year, month, day):
    return int(datetime.datetime(year, month, day, 0, 0, tzinfo=datetime.timezone.utc).timestamp())


def get_strava_date(date):
    """There is a nicer way to do this but this is fine for now"""
    return calculate_epoch(*[int(d) for d in date.split("T")[0].split("-")])

def get_before_or_after_date(date):
    return datetime.datetime.strptime(date, '%Y_%m_%d') if date else None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Date arguments.')
    parser.add_argument('--after', help='After date')
    parser.add_argument('--before', help='Before date')
    parser.add_argument('--athlete', default=ATHLETE)
    args = parser.parse_args()

    # Setting up some information for
    client = Client(access_token=TOKEN)
    data = get_coordinates_list(cp_filepath)

    date_before = get_before_or_after_date(args.before)
    date_after = get_before_or_after_date(args.after)
    activities = list(client.get_activities(before=date_before, after=date_after))  # TODO: Do this properly

    for a in tqdm.tqdm(activities):
        i = a.id
        s = strava_run_totals(i, client)
        if len(s) > 0:
            time = int(s['time_delta'])
            distance = int(s['distance'])
            start_date = get_strava_date(a.to_dict()['start_date'])
            model.add_run_from_athlete(ATHLETE, start_date, distance, time)
