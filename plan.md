## 1. Motivation and Audience    

### 1.1 What problem does your dashboard address?

<!-- State the specific question your dashboard helps someone answer. -->
<!-- Example: "How has public transport patronage in Auckland recovered since 2020?" -->

This dashboard investigates how crash severity patterns vary across Auckland between 2023 and 2026, with a particular focus on pedestrian-related crashes under different light conditions.

The dashboard combines spatial crash locations with severity and lighting information to explore where serious and fatal crashes are concentrated and whether pedestrian crashes are more severe during darker conditions. By integrating interactive maps and charts, the dashboard helps users identify potential road safety risks and understand how environmental conditions may influence crash outcomes.

### 1.2 Who is it for?

<!-- Describe one or two realistic users — their role and the decision this dashboard informs. -->

This dashboard is designed for transport planners, road safety analysts, and local government decision-makers in Auckland.

These users can use the dashboard to identify high-risk locations, examine pedestrian crash patterns, and better understand how lighting conditions relate to crash severity. The insights may support decisions about pedestrian safety improvements, street lighting, traffic calming measures, and future road safety planning.

### 1.3 What insight does it enable?

<!-- One sentence: the single most important thing a user should take away. -->
<!-- This sentence might become the title or subtitle of your app. -->

Pedestrian crashes in Auckland are concentrated in specific locations, and crashes occurring under darker light conditions are more likely to result in serious or fatal outcomes.


## 2. Data and Preparation

### 2.1 Datasets used
Dataset: CAS_Data_public
Source URL: https://opendata-nzta.opendata.arcgis.com/search
Format: CSV
Rows(approx.): ~28000. (28584)
Key variables: X, Y, crashYear, crashSeverity,pedestrian,light

### 2.2 Cleaning and preparation steps

<!-- List the steps needed to get each dataset ready. One line each. -->
1. Selected the variables needed for the dashboard, including X, Y, crash year, crash severity, pedestrian involvement, and light conditions.
2. Filtered the dataset to include crashes occurring between 2023 and 2026.
3. Filled missing light condition values with "Unknown".
4. Filled missing pedestrian values with 0 and converted the variable to integer format.
5. Converted crash coordinates from NZTM (EPSG:2193) to WGS84 (EPSG:4326) for use in the interactive map.
6. Created latitude and longitude fields (lat, lon) for mapping in ipyleaflet.
7. Prepared reactive filtered datasets for use in the Shiny dashboard outputs.

### 2.3 Limitations

<!-- Every dataset has gaps. Note at least two. -->

- The dashboard only focuses on selected variables related to pedestrian crashes and does not include other possible factors such as weather, traffic volume, driver behaviour, or road conditions.
- The dataset only includes crashes recorded between 2023 and 2026, so longer-term crash trends cannot be analysed.


## Section 3: Technical Planning. 
When users open the dashboard, they first see the title “Auckland Crash Severity Dashboard (2023–2026)” together with a short description explaining that the dashboard explores crash severity patterns in Auckland, with a focus on pedestrian-related crashes. The layout is organised into two main sections: a filter panel on the left and the visual outputs on the right. A help card below the filters explains how to use the dashboard and how the visualisations should be interpreted.

The left sidebar contains three user inputs. A dropdown menu allows the user to select a crash year between 2023 and 2026. Another dropdown menu allows the user to filter crash severity levels, including Non-Injury, Minor, Serious, and Fatal crashes. A radio button input allows the user to choose between viewing pedestrian crashes only or all crashes. Below the filters, a text summary dynamically reports how many crashes match the current filters and identifies the most common crash severity.

On the right side of the dashboard, users see two visual outputs. The first output is an interactive ipyleaflet map that displays crash locations across Auckland as coloured point markers. Different colours represent different crash severity levels. Users can zoom and pan around the map to explore where crashes are concentrated. The second output is a quantitative bar chart showing how pedestrian crash severity varies under different light conditions, such as bright sun, overcast, dark, and twilight conditions. When users change the filters, both the map and chart update automatically to reflect the selected crash data.