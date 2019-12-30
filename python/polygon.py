import pandas as pd
import numpy as np

# Methodology for checking if point is in polygon taken from:
# https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
# http://www.dcs.gla.ac.uk/~pat/52233/slides/Geometry1x1.pdf

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def list_to_points(points):
    return [Point(p[0], p[1]) for p in points]


def onSegment(p, q, r):
    """Given three colinear points p, q, r, the function checks if point q lies on line segment 'pr'"""
    if (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y)):
        return True
    else:
        return False


def orientation(p, q, r):
    """To find orientation of ordered triplet (p, q, r).
    The function returns following values
    0 --> p, q and r are colinear
    1 --> Clockwise
    2 --> Counterclockwise"""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if (val == 0):
        return 0
    elif (val > 0):
        return 1
    else:
        return 2


def doIntersect(p1, q1, p2, q2):
    """The function that returns true if line segment 'p1q1' and 'p2q2' intersect."""
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    #p1, q1 and p2 are colinear and p2 lies on seqment p1q1
    elif (o1 == 0) and onSegment(p1, p2, q1):
        return True

    # p1, q1 and p2 are colinear and q2 lies on segment p1q1
    elif (o2 == 0) and onSegment(p1, q2, q1):
        return True

    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    elif (o3 == 0) and onSegment(p2, p1, q2):
        return True

    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    elif (o4 == 0) and onSegment(p2, q1, q2):
        return True

    else:
        return False


def isInside(polygon, n, p):
    """
    Returns true if the point p lines inside the polygon[] with n vertices
    :param polygon: List of Points(lat, long) that make up the perimeter of interest
    :param n: number of vertices in polygon
    :param p: Point
    :return: Boolean indicating is point p lines inside the perimeter
    """

    # Polygon must have at least 3 vertices
    if (n < 3):
        return False

    # Create a point for line segment from p to infinite
    extreme = Point(1E8, p.y)


    # Count intersections of the above line with sides of polygon
    count = 0

    for i in range(n - 1):

        # Check if the line segment from 'p' to 'extreme' intersects
        # with the line segment from 'polygon[i]' to 'polygon[next]'
        if (doIntersect(polygon[i], polygon[i + 1], p, extreme)):
            # If the point 'p' is colinear with line segment 'i-next',
            # then check if it lies on segment. If it lies, return true,
            # otherwise false
            if (orientation(polygon[i], p, polygon[i + 1]) == 0):
                return onSegment(polygon[i], p, polygon[i + 1])

            count += 1
            #Return true if count is odd, false otherwise
    return (count % 2 != 0)


def row_inside_polygon(p, perimeter):
    """
    Function to return if a point is inside the polygon
    :param p: row from a dataframe or dictionary that includes latitude and longitude
    :param perimeter: List of [latitude, longitude] that makes up a perimeter
    :return: Boolean
    """
    pp = [Point(d[1], d[0]) for d in perimeter]
    return isInside(pp, len(pp), Point(p.latitude, p.longitude))

def run_inside_polygon(perimeter, gps_points):
    data = []
    for p in gps_points:
        i = isInside(perimeter, len(perimeter), Point(p.latitude, p.longitude))
        data.append([p.latitude, p.longitude, p.timestamp, i])
    return pd.DataFrame(data, columns=['latitude', 'longitude', 'time', 'inside'])


def totals_inside_polygon(df):
    return (
        df
        .join(df[['time', 'latitude', 'longitude', 'elevation']].shift(1), rsuffix='_previous')
        .dropna()
        .assign(time_delta=lambda d: (d['time'] - d['time_previous']))
        .assign(distance=lambda d:
                    threeD_distance_between_coordinates(
                    (d['latitude'], d['longitude'], d['elevation']),
                    (d['latitude_previous'], d['longitude_previous'], d['elevation_previous'])))
        .loc[lambda d: d['inside'] == True]
        [['time_delta', 'distance']]
        .sum()
    )


def twoD_total_inside_polygon(df):
    return (
        df
        .join(df[['time', 'latitude', 'longitude']].shift(1), rsuffix='_previous')
        .dropna()
        .assign(time_delta=lambda d: (d['time'] - d['time_previous']))
        .assign(distance=lambda d:
                    twoD_distance_between_coordinates_in_metres(
                    d['latitude'], d['longitude'],
                    d['latitude_previous'], d['longitude_previous']))
        .loc[lambda d: d['inside'] == True]
        [['time_delta', 'distance']]
        .sum()
    )

def twoD_distance_between_coordinates_in_metres(lat1, lon1, lat2, lon2, R=6371):
    dLat = np.deg2rad(lat2 - lat1)
    dLon = np.deg2rad(lon2 - lon1)
    lat1 = np.deg2rad(lat1)
    lat2 = np.deg2rad(lat2)
    a = np.sin(dLat/2) * np.sin(dLat/2) + np.sin(dLon/2) * np.sin(dLon/2) * np.cos(lat1) * np.cos(lat2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c * 1000


def threeD_distance_between_coordinates(p1, p2):
    lat1, lon1, e1 = p1
    lat2, lon2, e2 = p2
    twoD_distance = twoD_distance_between_coordinates_in_metres(lat1, lon1, lat2, lon2)
    return np.sqrt(np.square(twoD_distance) + np.square(e2 - e1))

