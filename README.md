# Auckland Crash Severity Dashboard

An interactive GIS dashboard for exploring the spatial and temporal patterns of road crashes in Auckland. The project focuses on crash severity, pedestrian involvement, road-user type and light conditions.

[Open the live dashboard](https://rhua798.github.io/gisci343-a2-auckland-crashes/) · [View the source code](https://github.com/rhua798/gisci343-a2-auckland-crashes)

## What the dashboard does

- Filters crashes by year, severity and road-user group
- Maps crash locations interactively with Leaflet
- Compares severity patterns across different light conditions
- Highlights pedestrian-related crashes for closer investigation
- Runs entirely in the browser through Shinylive

## Data and method

The analysis uses Waka Kotahi Crash Analysis System (CAS) records for Auckland from 2023–2026. Coordinates are transformed from NZTM (EPSG:2193) to WGS84 for web mapping. The dashboard then uses reactive filters to update both the map and the comparative chart.

## Technology

- Python
- Shiny for Python and Shinylive
- Pandas
- ipyleaflet
- Matplotlib
- pyproj

## Run locally

```bash
cd basic-app
pip install shiny pandas matplotlib pyproj ipyleaflet
shiny run --reload app.py
```

## Project structure

- `basic-app/app.py` — dashboard application
- `basic-app/style.css` — dashboard styles
- `basic-app/data/` — project data used by the app
- `docs/` — exported Shinylive site used by GitHub Pages
- `image/` — project screenshots

## Limitations

This is an educational GIS project. Results depend on the completeness and coding of CAS records, and apparent spatial patterns should not be interpreted as causal relationships.

## Author

Ruoxuan Huang (Spencer) — Computer Science and Geographic Information Science student at the University of Auckland.

[Portfolio](https://ruoxuan-huang-portfolio.huangruoxuan0208.chatgpt.site/) · [GitHub profile](https://github.com/rhua798)
