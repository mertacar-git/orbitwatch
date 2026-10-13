import unittest
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_offline_prediction(self):
        app = AppTest.from_file('app.py').run(timeout=30)
        app.sidebar.button[1].click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.metric),4)
        app.sidebar.slider[1].set_value(48).run(timeout=30)
        self.assertFalse(app.exception)
    def test_bad_tle_message(self):
        app = AppTest.from_file('app.py').run(timeout=30)
        app.sidebar.text_area[0].set_value('invalid').run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
