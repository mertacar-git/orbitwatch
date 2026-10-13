# OrbitWatch

Fetch ISS orbital elements from CelesTrak or paste any valid three-line TLE. View predicted positions and observer horizon events.

## Features

- Fetch and cache TLE data by NORAD catalog number from CelesTrak.
- Validate checksums, satellite identifiers and key orbital fields.
- Offline example with reproducible predictions at the element epoch.
- Three-hour sampled ground track and observer elevation, azimuth and slant range.
- Configurable observer location, elevation threshold and 1–72 hour horizon-event window.
- TLE, ground-track and event CSV exports; stale-element and network-failure messages.

## Example workflow

Click **Load offline example**. The historical synthetic ISS-like elements are evaluated at their epoch, not today. Change observer coordinates or the minimum elevation, then inspect the horizon events. For a current prediction, fetch catalog 25544 and disable epoch mode. Fetch results are cached for one hour to reduce service load. A failed fetch preserves the existing text.

No ephemeris download or API key is required for the offline example. A rise or set indicates crossing the selected elevation threshold; it does not establish visual visibility. Events at a window boundary may represent only part of a pass. This tool is not a collision predictor or mission-navigation system.

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

## Checks and license

GitHub Actions runs core and Streamlit interaction tests on every push and pull request. The UI tests cover offline operation and primary controls. External data-service availability is not guaranteed by offline tests. MIT licensed; see `LICENSE`.
