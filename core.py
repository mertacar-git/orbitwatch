from datetime import timezone
import math
from skyfield.api import EarthSatellite, load, wgs84

def parse_tle(text, ts):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 3 or not lines[1].startswith('1 ') or not lines[2].startswith('2 '):
        raise ValueError('Provide a satellite name followed by two TLE lines.')
    for line in lines[1:]:
        if len(line) != 69 or not line[-1].isdigit():
            raise ValueError('TLE lines must have 69 characters and a checksum.')
        checksum = sum(int(c) if c.isdigit() else 1 if c == '-' else 0 for c in line[:68]) % 10
        if checksum != int(line[-1]): raise ValueError('TLE checksum mismatch.')
    if lines[1][2:7] != lines[2][2:7]:
        raise ValueError('Both TLE lines must identify the same satellite.')
    try:
        inclination, eccentricity, motion = float(lines[2][8:16]), float('0.'+lines[2][26:33]), float(lines[2][52:63])
    except ValueError as exc:
        raise ValueError('Invalid orbital fields.') from exc
    if not 0 <= inclination <= 180 or not 0 <= eccentricity < 1 or not 0 < motion < 20:
        raise ValueError('Orbital fields are outside supported bounds.')
    sat = EarthSatellite(lines[1], lines[2], lines[0], ts)
    if sat.model.satnum <= 0: raise ValueError('Invalid satellite identifier.')
    return sat

def position(satellite, time):
    geo = satellite.at(time)
    if geo.message: raise ValueError(geo.message)
    point = wgs84.subpoint(geo)
    return dict(lat=point.latitude.degrees, lon=point.longitude.degrees, altitude_km=point.elevation.km)

def events(satellite, ts, latitude, longitude, start, end, elevation=10):
    if not all(math.isfinite(v) for v in [latitude,longitude,elevation]) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180 or not 0 <= elevation <= 90:
        raise ValueError('Invalid observer coordinates or elevation.')
    if start.tzinfo is None or end.tzinfo is None or not 0 < (end-start).total_seconds() <= 7*86400:
        raise ValueError('Provide timezone-aware times with a window of at most seven days.')
    observer = wgs84.latlon(latitude, longitude)
    times, kinds = satellite.find_events(observer, ts.from_datetime(start), ts.from_datetime(end), altitude_degrees=elevation)
    return [dict(time_utc=t.utc_datetime().astimezone(timezone.utc).isoformat(), event=['Rise', 'Culmination', 'Set'][int(kind)]) for t, kind in zip(times, kinds)]

def look_angle(satellite, ts, latitude, longitude, when):
    difference = satellite - wgs84.latlon(latitude, longitude)
    altitude, azimuth, distance = difference.at(ts.from_datetime(when)).altaz()
    return dict(elevation_deg=altitude.degrees, azimuth_deg=azimuth.degrees, range_km=distance.km)
