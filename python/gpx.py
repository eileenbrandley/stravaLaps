import requests
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime
import gpx_parser as parser
import xml.etree.ElementTree as ET
"""
Script to read and parse Strava tracks
"""

def parse_gpx_file(filename):
    with open(filename, 'r') as gpx_file:
        gpx = parser.parse(gpx_file)
    return gpx


def get_gps_track(gpx):
    return gpx.tracks[0]


def track_to_list(t):
    return [[p.latitude, p.longitude, pd.to_datetime(p.time)] for p in t.points]


def coordinates_list_from_gpx(filename):
    gpx = parse_gpx_file(filename)
    track = get_gps_track(gpx)
    return track_to_list(track)


def coordinates_dataframe_from_gpx(filename):
    return pd.DataFrame(coordinates_list_from_gpx(filename), columns=['latitude', 'longitude', 'time'])


# I don't think this belongs here. TODO: Move over to another script
def get_polygon_coords(polygon):
    tree = ET.parse(polygon)
    root = tree.getroot()
    return [child.attrib for child in root[1]]


def coords_dataframe(polygon):
    return pd.DataFrame(get_polygon_coords(polygon))