from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.request
import pandas as pd
import streamlit as st
from skyfield.api import load
from core import parse_tle, position, events, look_angle

st.set_page_config(page_title='OrbitWatch', page_icon='🛰️', layout='wide')
st.title('OrbitWatch')
st.caption('SGP4 orbital predictions · WGS84 observer geometry · UTC timestamps')
@st.cache_data(ttl=3600)
def fetch_tle(catalog):
    request = urllib.request.Request(f'https://celestrak.org/NORAD/elements/gp.php?CATNR={catalog}&FORMAT=TLE',headers={'User-Agent':'OrbitWatch/1.0'})
    with urllib.request.urlopen(request,timeout=15) as response:
        return response.read(4096).decode('utf-8')
catalog = st.sidebar.number_input('NORAD catalog number', min_value=1, max_value=99999, value=25544)
if st.sidebar.button('Fetch current orbital elements'):
    try: st.session_state['tle'] = fetch_tle(catalog)
    except (OSError,UnicodeError) as exc: st.sidebar.error(f'Could not fetch elements: {exc}. You can paste a TLE instead.')
if st.sidebar.button('Load offline example'):
    st.session_state['tle'] = Path(__file__).with_name('sample.tle').read_text()
    st.session_state['epoch_mode'] = True
text = st.sidebar.text_area('Name + two TLE lines',key='tle',height=140)
epoch_mode = st.sidebar.checkbox('Predict at TLE epoch (offline example)',key='epoch_mode')
lat = st.sidebar.number_input('Observer latitude',-90.0,90.0,41.0082)
lon = st.sidebar.number_input('Observer longitude',-180.0,180.0,28.9784)
elevation = st.sidebar.slider('Minimum elevation (degrees)',0,60,10)
hours = st.sidebar.slider('Prediction window (hours)',1,72,24)
if not text:
    st.info('Fetch current elements, paste a three-line TLE, or load the offline example. The example uses historical synthetic elements and its epoch for a reproducible demonstration.'); st.stop()
ts = load.timescale(builtin=True)
try:
    sat = parse_tle(text,ts)
    now = sat.epoch.utc_datetime() if epoch_mode else datetime.now(timezone.utc)
    age = abs((now-sat.epoch.utc_datetime()).total_seconds()/86400)
    st.write(f'{sat.name} · element epoch {sat.epoch.utc_iso()} · prediction time {now.isoformat()}')
    if epoch_mode: st.info('Historical demonstration at element epoch; this view does not show the current satellite location.')
    if age > 7: st.warning('Elements are more than seven days from the prediction time. Refresh them before interpreting this prediction.')
    point = position(sat,ts.from_datetime(now))
    angles = look_angle(sat,ts,lat,lon,now)
    cols = st.columns(4)
    for col,label,value in zip(cols,['Altitude','Observer elevation','Azimuth','Slant range'],[f'{point["altitude_km"]:.1f} km',f'{angles["elevation_deg"]:.1f}°',f'{angles["azimuth_deg"]:.1f}°',f'{angles["range_km"]:.1f} km']): col.metric(label,value)
    tabs = st.tabs(['Ground track','Horizon events','Export'])
    track = pd.DataFrame([dict(time_utc=(now+timedelta(minutes=m)).isoformat(),**position(sat,ts.from_datetime(now+timedelta(minutes=m)))) for m in range(181)])
    event_data = pd.DataFrame(events(sat,ts,lat,lon,now,now+timedelta(hours=hours),elevation),columns=['time_utc','event'])
    with tabs[0]:
        st.map(track[['lat','lon']]); st.caption('Sampled sub-satellite positions for the next three hours, at one-minute intervals.')
    with tabs[1]:
        if event_data.empty: st.info('No horizon events found in this window.')
        else: st.dataframe(event_data,width='stretch')
        st.caption('Rise and set refer to the selected elevation threshold. Culmination is a local elevation maximum. The window can start or end during a pass. Optical visibility is not modeled.')
    with tabs[2]:
        st.download_button('Ground track CSV',track.to_csv(index=False),'ground_track.csv','text/csv')
        st.download_button('Horizon events CSV',event_data.to_csv(index=False),'events.csv','text/csv')
        st.download_button('Orbital elements',text,'satellite.tle','text/plain')
except (ValueError,IndexError,OverflowError) as exc:
    st.error(str(exc))
