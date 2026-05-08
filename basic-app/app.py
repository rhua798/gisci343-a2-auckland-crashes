from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
from ipyleaflet import Map, CircleMarker,basemaps,LegendControl
from shinywidgets import output_widget, register_widget
from pyproj import Transformer
from pathlib import Path


APP_DIR = Path(__file__).parent
crashes = pd.read_csv(APP_DIR / "CAS_Data_public.csv")
# crashes = pd.read_csv('basic-app/CAS_Data_public.csv')

# filter the data we needed
crashes = crashes[["X", "Y", "crashYear", "crashSeverity", 'pedestrian','light']]
print(crashes.columns)

# year filter--choose 2023 to 2026
crashes = crashes[(crashes["crashYear"] >= 2023) & (crashes["crashYear"] <= 2026)]

crashes["light"] = crashes["light"].fillna("Unknown")

# change the data type
crashes["pedestrian"] = crashes["pedestrian"].fillna(0).astype(int)
crashes.shape

#（NZTM → WGS84）
transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
crashes["lon"], crashes["lat"] = transformer.transform(
    crashes["X"].values, crashes["Y"].values
)


# ui 
app_ui = ui.page_fluid(
    ui.include_css(APP_DIR / "style.css"),
    # Title
    ui.div(
        ui.h2("Auckland Crash Severity Dashboard (2023 - 2026)"),
        ui.p( "Explore crash patterns across Auckland between 2023 to 2026, with a focus on pedestrian crashes, using interactive maps and charts.",
            class_="dashboard-subtitle"),
    ),

    # Main layout
    ui.layout_columns(
        # LEFT SIDEBAR
        ui.div(
            ui.div(
                ui.h4("Filters"),
                ui.input_select("year","Year",[2023, 2024, 2025, 2026] ),
                ui.input_select( "severity","Severity",["All","Non-Injury Crash","Minor Crash","Serious Crash","Fatal Crash"]),
                ui.input_radio_buttons("user", "Road User",["Pedestrian", "All"]),
                ui.div(
                    ui.div(
                        "Summary",
                        class_="summary-title"
                    ),
                    ui.output_text("summary"),
                    class_="summary-box"
                ),

                class_="card filter-card"

            ),
            ui.div(
                {"class": "help-card"},
                ui.h4("How to use this dashboard"),
                ui.p(
                    "Use the filters above to explore crash patterns across Auckland by year, severity, and road user type."
                ),
                ui.p(
                    "The map shows where crashes occurred, while the chart compares pedestrian crash severity under different lighting conditions."
                ),
                ui.p(
                    "Selecting different filters will automatically update the visualisations."
                )
                        )
            ),

        # RIGHT SIDE
        ui.div(
            # MAP
            ui.div(
                output_widget("map"),
                class_="card map-card"
            ),
            # CHART
            ui.div(
                ui.output_plot("trend"),
                class_="card chart-card"
            ),
        ),
        
        col_widths=(3, 9)
    )
)

def server(input, output, session):
    @reactive.calc
    def filtered():
        df = crashes
        # year filter
        df = df[df["crashYear"] == int(input.year())]
        # severity filter
        if input.severity() != "All":
            df = df[df["crashSeverity"] == input.severity()]
        # pedestrain filter
        if input.user () == "Pedestrian":
            df = df[df["pedestrian"] == 1]
        
        return df  

    @render.text
    def summary():
        df = filtered()
        if len(df) == 0:
            return "No crashes match the current filters."
        most_common = df["crashSeverity"].mode().iloc[0]
        return f"{len(df)} crashes selected, with the majority classified as {most_common}."

    def get_color(severity):
        if severity == "Fatal Crash":
            return "#d73027"  
        elif severity == "Serious Crash":
            return "#fc8d59"   
        elif severity == "Minor Crash":
            return "#91bfdb"   
        else:
            return "#4575b4" 
    
    @render.plot
    def trend():
        df = filtered()
        df = df[df["pedestrian"] == 1]
        df = df[df["light"].notna()]

        # Group and count
        counts = df.groupby(["light", "crashSeverity"]).size().unstack(fill_value=0)

        # Order light conditions
        light_order = [
            "Bright sun",
            "Overcast",
            "Dark",
            "Twilight"
        ]

        counts = counts.reindex(light_order)

        # Order severity categories
        severity_order = [ "Non-Injury Crash", "Minor Crash", "Serious Crash", "Fatal Crash" ]
        counts = counts.reindex(columns=severity_order,fill_value=0)

        # If severity = All → show proportion chart
        if input.severity() == "All":
            proportion = counts.div(
                counts.sum(axis=1),
                axis=0
            )
            ax = proportion.plot(kind="bar")
            plt.ylabel("Proportion of Crashes")

            # Percentage labels
            for container in ax.containers:
                labels = [
                    f"{v*100:.1f}%"
                    if v > 0 else ""
                    for v in container.datavalues
                ]
                ax.bar_label(container,labels=labels,fontsize=7)

        # Otherwise show count chart
        else:
            ax = counts.plot(kind="bar")
            plt.ylabel("Number of Crashes")

            # Count labels
            for container in ax.containers:
                labels = [
                    f"{int(v)}"
                    if v > 0 else ""
                    for v in container.datavalues
                ]

                ax.bar_label(container,labels=labels,fontsize=7)

        # Shared formatting
        plt.title("Pedestrian Crash Severity by Light Condition")
        plt.xlabel("Light Condition")
        plt.xticks(rotation=0)
        plt.legend(title="Crash Severity")
        plt.tight_layout()
    
    m = Map(
        center=(-36.85, 174.76),
        zoom=11,
        basemap=basemaps.CartoDB.Positron
    )
    register_widget("map", m)

    @reactive.effect
    def update_map():

        df = filtered()

        # clear old layers
        while len(m.layers) > 1:
            m.remove(m.layers[-1])

        # remove missing coordinates
        df = df.dropna(subset=["lat", "lon"])

        # no data
        if len(df) == 0:
            return

        # sample large datasets
        if len(df) > 1000:
            df = df.sample(1000, random_state=1)

        markers = []

        for row in df.itertuples():

            marker = CircleMarker(
                location=(row.lat, row.lon),
                radius=5,
                color=get_color(row.crashSeverity),
                fill_color=get_color(row.crashSeverity),
                fill_opacity=0.7,
                stroke=False
            )

            markers.append(marker)

        for marker in markers:
            m.add(marker)     

        # add legend once
        if not any(isinstance(c, LegendControl) for c in m.controls):

            legend = LegendControl(
                {
                    "Fatal": "#d73027",
                    "Serious": "#fc8d59",
                    "Minor": "#91bfdb",
                    "Non-injury": "#4575b4"
                },
                name="Crash Severity",
                position="topright"
            )

            m.add(legend)

app = App(app_ui, server)
