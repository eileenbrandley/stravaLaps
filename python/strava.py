import pandas as pd
import time

def get_stream_from_activity(client, activity_id, strava_run):
    types = ['time', 'latlng', 'altitude']

    streams = client.get_activity_streams(activity_id, types=types, resolution='high')
    data = streams['latlng'].data
    time = streams['time'].data
    altitude = streams['altitude'].data

    return [
        {'track_id': strava_run, 'latitude': d[0], 'longitude': d[1], 'timestamp': t, 'elevation': e}
        for (d, t, e) in zip(data, time, altitude)
    ]


def get_activities_since_date(client, date=None, limit=5):
    if date is None:
        return client.get_activities(after="2013-01-01T00:00:00Z",  limit=limit)
    else:
        return client.get_activities(after=date, limit=limit)


def timestamp_to_epoch(t):
    return time.mktime(t.timetuple())


def epoch_to_timestamp(t):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(t))


def throttle_request(wait=15):
    time.sleep(wait)