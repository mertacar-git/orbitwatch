# OrbitWatch

Fetch ISS orbital elements from CelesTrak or paste any valid three-line TLE. View predicted positions and observer horizon events.

## Quick start

Python 3.12 recommended. Run commands inside this repository.

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Validation

```sh
python -m unittest discover -v
```

## Model and limitations

Uses Skyfield SGP4 propagation and WGS84 coordinates. Events are UTC and use a configurable minimum elevation. Rise/set events at the edges of the 24-hour window may be incomplete. Predictions depend on the age and quality of orbital elements. Optical visibility, maneuvers and collision analysis are outside this model. Internet is required to fetch elements, but pasted elements use bundled timescale data. Source: https://celestrak.org/NORAD/documentation/gp-data-formats.php

## Repository structure

- `core.py`: numerical/data processing functions
- `app.py`: interactive Streamlit interface
- `test_core.py`: checks for model behavior and invalid input

## Development

Built with AI assistance. Model assumptions and validation are documented so the implementation can be reviewed and extended.
