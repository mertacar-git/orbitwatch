from datetime import datetime, timedelta, timezone
import urllib.request
import pandas as pd
import streamlit as st
from skyfield.api import load
from core import parse_tle, position, events

st.set_page_config(page_title='OrbitWatch', layout='wide')
st.title('OrbitWatch')
st.caption('Predicted satellite positions from orbital elements, with geometric horizon events.')
st.sidebar.markdown('Fetch ISS elements or paste a three-line TLE below.')
if st.sidebar.button('Fetch latest ISS TLE'):
    try:
        request = urllib.request.Request('https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE', headers={'User-Agent':'OrbitWatch/1.0'})
        with urllib.request.urlopen(request, timeout=15) as response:
            st.session_state['tle'] = response.read(4096).decode('utf-8')
    except (OSError, UnicodeError) as exc: st.sidebar.error(f'Data unavailable: {exc}')
text = st.sidebar.text_area('Name + TLE', key='tle', height=140)
lat = st.sidebar.number_input('Observer latitude', -90.0, 90.0, 41.0082)
lon = st.sidebar.number_input('Observer longitude', -180.0, 180.0, 28.9784)
elevation = st.sidebar.slider('Minimum elevation (degrees)', 0, 60, 10)
if not text:
    st.info('Fetch orbital elements or paste a TLE to begin. Internet access is only required for fetching.')
    st.stop()
ts = load.timescale(builtin=True)
try:
    sat = parse_tle(text, ts)
    now = datetime.now(timezone.utc)
    age = abs((now-sat.epoch.utc_datetime()).total_seconds()/86400)
    st.write(f'{sat.name} · epoch {sat.epoch.utc_iso()} · element age {age:.1f} days')
    if age > 7: st.warning('Elements are more than seven days from the selected time. Refresh for more useful predictions.')
    point = position(sat, ts.from_datetime(now))
    st.metric('Predicted altitude', f'{point["altitude_km"]:.1f} km')
    track = pd.DataFrame([position(sat, ts.from_datetime(now+timedelta(minutes=m))) for m in range(91)])
    st.map(track[['lat','lon']])
    st.subheader('Horizon events over the next 24 hours (UTC)')
    result = pd.DataFrame(events(sat, ts, lat, lon, now, now+timedelta(days=1), elevation))
    st.dataframe(result, width='stretch')
    st.caption('Events do not imply optical visibility: daylight and satellite illumination are not modeled. The map shows sampled positions for 90 minutes.')
except (ValueError, IndexError) as exc:
    st.error(str(exc))
