from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
from pyproj import Transformer


APP_DIR = Path(__file__).parent
crashes = pd.read_csv(APP_DIR / "CAS_Data_public.csv")

# filter the data we needed
crashes = crashes[["X", "Y", "crashYear", "crashSeverity", "pedestrian", "light"]]

# year filter--choose 2023 to 2026
crashes = crashes[(crashes["crashYear"] >= 2023) & (crashes["crashYear"] <= 2026)]
crashes["light"] = crashes["light"].fillna("Unknown")
# change the data type
crashes["pedestrian"] = crashes["pedestrian"].fillna(0).astype(int)

#（NZTM → WGS84）
transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
crashes["lon"], crashes["lat"] = transformer.transform(
    crashes["X"].values, crashes["Y"].values
)

# define severity colours
SEVERITY_COLORS = {
    "Fatal Crash": "#d73027",
    "Serious Crash": "#fc8d59",
    "Minor Crash": "#91bfdb",
    "Non-Injury Crash": "#4575b4",
}

#ui
app_ui = ui.page_fluid(
    ui.include_css(APP_DIR / "style.css"),
    ui.head_content(
        ui.tags.title("Auckland Crash Dashboard"),
        ui.tags.link(rel="icon", href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚧</text></svg>"),
        ui.tags.link(rel="stylesheet", href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"),
        ui.tags.script(src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"),
    ),
    #title
    ui.div(
        ui.h2("Auckland Crash Severity Dashboard (2023 - 2026)"),
        ui.p(
            "Explore crash patterns across Auckland between 2023 to 2026, with a focus on pedestrian crashes, using interactive maps and charts.",
            class_="dashboard-subtitle",
        ),
    ),
    ui.layout_columns(
        # left sidebar
        ui.div(
            ui.div(
                ui.h4("Filters"),
                ui.input_select("year", "Year", [2023, 2024, 2025, 2026]),
                ui.input_select(
                    "severity",
                    "Severity",
                    ["All", "Non-Injury Crash", "Minor Crash", "Serious Crash", "Fatal Crash"],
                ),
                ui.input_radio_buttons("user", "Road User", ["Pedestrian", "All"]),
                ui.div(
                    ui.div("Summary", class_="summary-title"),
                    ui.output_text("summary"),
                    class_="summary-box",
                ),
                class_="card filter-card",
            ),
            ui.div(
                {"class": "help-card"},
                ui.h4("How to use this dashboard"),
                ui.p("Use the filters above to explore crash patterns across Auckland by year, severity, and road user type."),
                ui.p("The map shows where crashes occurred, while the chart compares pedestrian crash severity under different lighting conditions."),
                ui.p("Selecting different filters will automatically update the visualisations."),
            ),
        ),
        # right side
        ui.div(
            ui.div(
                ui.output_ui("map"),
                class_="card map-card",
            ),
            ui.div(
                ui.output_plot("trend"),
                class_="card chart-card",
            ),
        ),
        col_widths=(3, 9),
    )
)


def server(input, output, session):
    @reactive.calc
    def filtered():
        df = crashes.copy()
        df = df[df["crashYear"] == int(input.year())]
        if input.severity() != "All":
            df = df[df["crashSeverity"] == input.severity()]
        if input.user() == "Pedestrian":
            df = df[df["pedestrian"] == 1]
        return df

    @render.text
    def summary():
        df = filtered()
        if len(df) == 0:
            return "No crashes match the current filters."
        most_common = df["crashSeverity"].mode().iloc[0]
        return f"{len(df)} crashes selected, with the majority classified as {most_common}."

    @render.ui
    def map():
        df = filtered().dropna(subset=["lat", "lon"])
        if len(df) > 1000:
            df = df.sample(1000, random_state=1)

        points = df[["lat", "lon", "crashSeverity", "light", "crashYear"]].to_dict(orient="records")
        points_json = json.dumps(points)
        colors_json = json.dumps(SEVERITY_COLORS)

        map_id = "leaflet-map"
        html = f"""
        <div id="{map_id}" style="width:100%;height:500px;border-radius:16px;"></div>
        <script>
        (function() {{
            var existing = L.DomUtil.get('{map_id}');
            if (existing && existing._leaflet_id) {{
                existing._leaflet_id = null;
                existing.innerHTML = '';
            }}
            var map = L.map('{map_id}').setView([-36.85, 174.76], 11);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                maxZoom: 19
            }}).addTo(map);

            var points = {points_json};
            var colors = {colors_json};

            points.forEach(function(p) {{
                L.circleMarker([p.lat, p.lon], {{
                    radius: 5,
                    color: colors[p.crashSeverity] || '#4575b4',
                    fillColor: colors[p.crashSeverity] || '#4575b4',
                    fillOpacity: 0.7,
                    weight: 0
                }}).bindPopup(
                    '<b>' + p.crashSeverity + '</b><br>' +
                    'Year: ' + p.crashYear + '<br>' +
                    'Light: ' + (p.light || 'Unknown')
                ).addTo(map);
            }});

            var legend = L.control({{position: 'topright'}});
            legend.onAdd = function() {{
                var div = L.DomUtil.create('div', 'leaflet-legend');
                div.style.background = 'white';
                div.style.padding = '10px 14px';
                div.style.borderRadius = '8px';
                div.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
                div.style.fontSize = '13px';
                div.innerHTML =
                    '<b>Crash Severity</b><br>' +
                    '<span style="color:#d73027">&#9679;</span> Fatal<br>' +
                    '<span style="color:#fc8d59">&#9679;</span> Serious<br>' +
                    '<span style="color:#91bfdb">&#9679;</span> Minor<br>' +
                    '<span style="color:#4575b4">&#9679;</span> Non-injury';
                return div;
            }};
            legend.addTo(map);
        }})();
        </script>
        """
        return ui.HTML(html)

    @render.plot
    def trend():
        df = filtered()
        df = df[df["pedestrian"] == 1]
        df = df[df["light"].notna()]

        counts = df.groupby(["light", "crashSeverity"]).size().unstack(fill_value=0)
        light_order = ["Bright sun", "Overcast", "Dark", "Twilight"]
        counts = counts.reindex(light_order)
        severity_order = ["Non-Injury Crash", "Minor Crash", "Serious Crash", "Fatal Crash"]
        counts = counts.reindex(columns=severity_order, fill_value=0)

        if input.severity() == "All":
            proportion = counts.div(counts.sum(axis=1), axis=0)
            ax = proportion.plot(kind="bar")
            plt.ylabel("Proportion of Crashes")
            for container in ax.containers:
                labels = [f"{v*100:.1f}%" if v > 0 else "" for v in container.datavalues]
                ax.bar_label(container, labels=labels, fontsize=7)
        else:
            ax = counts.plot(kind="bar")
            plt.ylabel("Number of Crashes")
            for container in ax.containers:
                labels = [f"{int(v)}" if v > 0 else "" for v in container.datavalues]
                ax.bar_label(container, labels=labels, fontsize=7)

        plt.title("Pedestrian Crash Severity by Light Condition")
        plt.xlabel("Light Condition")
        plt.xticks(rotation=0)
        plt.legend(title="Crash Severity")
        plt.tight_layout()


app = App(app_ui, server)
