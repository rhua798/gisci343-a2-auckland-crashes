## 1. Motivation and Audience

### 1.1 What problem does your dashboard address?

<!-- State the specific question your dashboard helps someone answer. -->
<!-- Example: "How has public transport patronage in Auckland recovered since 2020?" -->

This dashboard investigates where severe road crashes occur in Auckland and how crash patterns vary across different speed limits between 2024 and 2026.

The aim is to explore the spatial distribution of crashes and examine whether higher speed limits are associated with more severe crash outcomes. By combining location, time, and road characteristics, the dashboard helps identify patterns in road safety risks.

### 1.2 Who is it for?

<!-- Describe one or two realistic users — their role and the decision this dashboard informs. -->

This dashboard is designed for transport planners, road safety analysts in Auckland.

These users can use the dashboard to identify high-risk areas and better understand how speed limits relate to crash severity. The insights can support decisions about speed management, road design, and safety interventions.

### 1.3 What insight does it enable?

<!-- One sentence: the single most important thing a user should take away. -->
<!-- This sentence might become the title or subtitle of your app. -->

Severe crashes are more likely to occur on roads with higher speed limits and are concentrated in specific areas of Auckland.


## 2. Data and Preparation

### 2.1 Datasets used
Dataset: CAS_Data_public
Source URL: https://opendata-nzta.opendata.arcgis.com/search
Format: CSV
Rows(approx.): ~60000. (60812)
Key variables: X, Y, crashYear, crashSeverity,speedLimit

### 2.2 Cleaning and preparation steps

<!-- List the steps needed to get each dataset ready. One line each. -->
1. Selected relevant variables (X, Y, crashYear, crashSeverity, speedLimit) and removed unnecessary columns.
2. Filtered the dataset to include only crashes between 2024 and 2026.
3. Removed rows with missing values using dropna().
4. Checked coordinate fields (X, Y) and ensured they are suitable for mapping.
5. Converted data types where necessary (e.g. crashYear as integer).
6. Prepared filtered datasets for use in reactive functions in the Shiny app.

### 2.3 Limitations

<!-- Every dataset has gaps. Note at least two. -->

- The dataset only includes crashes recorded in the CAS system, so minor or unreported incidents may be missing.
- The data is limited to the years 2024–2026, which may not capture longer-term trends.
- Speed limit data reflects posted limits, not actual driving speeds, which may affect interpretation.
- Spatial accuracy depends on recorded coordinates, which may contain small positional errors.



## Section 3: Technical Planning. --- 修改所有 ！！！
When the user opens the dashboard, they see a clean layout with a title at the top and a set of filters on the left. The title reads “Auckland Crash Severity Dashboard (2024–2026)”, followed by a short description explaining that the dashboard explores crash patterns by year, crash severity, and speed limit.

In the control panel, the user can interact with three inputs. A slider allows the user to select a specific year between 2024 and 2026. A dropdown menu lets the user choose a crash severity level (All, Non-Injury Crash, Minor Crash, Serious Crash, or Fatal Crash). A second slider allows the user to filter crashes by speed limit range. These inputs can be adjusted independently, and all visual outputs update automatically in response.

Below the filters, the dashboard displays a text summary showing how many crashes match the current selection and a brief description of the most common crash type. On the right, a bar chart shows the number of crashes by speed limit, helping users compare how crash frequency varies across different speed zones. An interactive map (ipyleaflet) displays the spatial distribution of crashes as clustered points, allowing users to see where crashes are concentrated geographically.

When the user changes any input (year, severity, or speed limit), all outputs update reactively. The filtering logic is handled by a shared reactive calculation (@reactive.calc), which ensures that both the chart and the map use the same filtered dataset. This avoids redundant computation and keeps the application efficient. Additional reactive behaviour could be implemented using @reactive.effect if needed, for example to reset inputs or update UI elements dynamically.

Overall, the dashboard allows users to explore how crash severity and speed limits interact across time and space, providing a clear and interactive view of road safety patterns in Auckland.