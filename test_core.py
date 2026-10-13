import unittest
from skyfield.api import load
from core import parse_tle, position

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

if __name__ == '__main__': unittest.main()
