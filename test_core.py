import unittest
from skyfield.api import load
from core import parse_tle, position
from core import events, look_angle
from datetime import timedelta
from pathlib import Path

def checked(line):
    body = line[:68].ljust(68)
    return body + str(sum(int(c) if c.isdigit() else 1 if c == '-' else 0 for c in body)%10)

class OrbitTests(unittest.TestCase):
    def test_reference_orbit(self):
        ts = load.timescale(builtin=True)
        text = 'ISS\n'+checked('1 25544U 98067A   24001.50000000  .00016717  00000+0  30134-3 0  999')+'\n'+checked('2 25544  51.6416  20.0000 0005000  40.0000  80.0000 15.5000000043000')
        satellite = parse_tle(text, ts)
        p = position(satellite, satellite.epoch)
        self.assertTrue(-90 <= p['lat'] <= 90)
        self.assertTrue(300 < p['altitude_km'] < 500)
    def test_reject_malformed(self):
        with self.assertRaises(ValueError): parse_tle('invalid', load.timescale(builtin=True))
    def test_checksum(self):
        ts = load.timescale(builtin=True)
        text = Path('sample.tle').read_text().replace('51.6416','51.6417')
        with self.assertRaises(ValueError): parse_tle(text,ts)
    def test_events_geometry(self):
        ts = load.timescale(builtin=True)
        satellite = parse_tle(Path('sample.tle').read_text(),ts)
        start = satellite.epoch.utc_datetime()
        result = events(satellite,ts,41,29,start,start+timedelta(days=1))
        self.assertTrue(result)
        self.assertEqual([r['time_utc'] for r in result],sorted(r['time_utc'] for r in result))
        from datetime import datetime
        for event in result:
            if event['event'] in ['Rise','Set']:
                angle = look_angle(satellite,ts,41,29,datetime.fromisoformat(event['time_utc']))
                self.assertAlmostEqual(angle['elevation_deg'],10,delta=0.1)
    def test_invalid_window(self):
        ts = load.timescale(builtin=True)
        satellite = parse_tle(Path('sample.tle').read_text(),ts)
        start = satellite.epoch.utc_datetime()
        with self.assertRaises(ValueError): events(satellite,ts,41,29,start,start)

if __name__ == '__main__': unittest.main()
