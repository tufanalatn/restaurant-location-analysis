import pandas as pd
import folium
from pathlib import Path


CANDIDATE_FILE = "data/opportunity_zone_candidates.csv"
ZONE_FILE = "data/final_opportunity_zones.csv"
FEATURE_FILE = "data/study_area_candidate_features.csv"

OUTPUT_FILE = "outputs/maps/final_opportunity_map.html"


# -------------------------------------------------
# Load data
# -------------------------------------------------

candidates = pd.read_csv(CANDIDATE_FILE)
zones = pd.read_csv(ZONE_FILE)
features = pd.read_csv(FEATURE_FILE)

Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# 2019 comparison area
# 59th Street / Central Park South
# -------------------------------------------------

area_2019 = features[
    (features["borough"] == "Manhattan")
    & (features["latitude"].between(40.758, 40.772))
    & (features["longitude"].between(-73.985, -73.970))
].copy()


# -------------------------------------------------
# Base map
# -------------------------------------------------

m = folium.Map(
    location=[40.73, -73.94],
    zoom_start=11,
    tiles="OpenStreetMap",
)


# -------------------------------------------------
# Layer 1 — 2026 robust candidates
# -------------------------------------------------

robust_layer = folium.FeatureGroup(
    name="2026 Robust Candidates",
    show=True,
)

for _, row in candidates.iterrows():

    popup = f"""
    <b>2026 Robust Candidate</b><br>
    Candidate: {row['candidate_id']}<br>
    Technical Zone: {int(row['opportunity_zone'])}<br>
    Borough: {row['borough']}<br><br>

    Pedestrian Demand: {row['pedestrian_demand_score']:.3f}<br>
    Turkish Competition: {row['turkish_competition_score']:.3f}<br>
    Rent Cost: {row['rent_score']:.3f}<br>
    Average Rank: {row['average_rank']:.1f}
    """

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=7,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.75,
        weight=2,
        tooltip=f"2026 — {row['candidate_id']}",
        popup=folium.Popup(popup, max_width=320),
    ).add_to(robust_layer)

robust_layer.add_to(m)


# -------------------------------------------------
# Layer 2 — 2026 opportunity zone centers
# -------------------------------------------------

zone_layer = folium.FeatureGroup(
    name="2026 Opportunity Zones",
    show=True,
)

for _, row in zones.iterrows():

    zone_id = int(row["opportunity_zone"])

    popup = f"""
    <b>2026 Opportunity Zone {zone_id}</b><br>
    {row['area_name']}<br>
    Borough: {row['borough']}<br>
    Robust candidates: {int(row['candidate_count'])}<br><br>

    Mean Pedestrian Demand: {row['mean_pedestrian_score']:.3f}<br>
    Mean Competition: {row['mean_competition_score']:.3f}<br>
    Mean Rent Cost: {row['mean_rent_score']:.3f}<br>
    Mean Average Rank: {row['mean_average_rank']:.1f}
    """

    folium.Marker(
        location=[
            row["center_latitude"],
            row["center_longitude"],
        ],
        tooltip=f"Zone {zone_id} — {row['area_name']}",
        popup=folium.Popup(popup, max_width=350),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 13px;
                font-weight: bold;
                text-align: center;
                background: white;
                border: 2px solid #111;
                border-radius: 50%;
                width: 34px;
                height: 34px;
                line-height: 30px;
            ">
                {zone_id}
            </div>
            """
        ),
    ).add_to(zone_layer)

zone_layer.add_to(m)


# -------------------------------------------------
# Layer 3 — 2019 comparison area
# -------------------------------------------------

comparison_layer = folium.FeatureGroup(
    name="2019 — 59th Street Comparison Area",
    show=True,
)

for _, row in area_2019.iterrows():

    popup = f"""
    <b>2019 Comparison Area</b><br>
    59th Street / Central Park South<br>
    Candidate: {row['candidate_id']}<br><br>

    2026 Pedestrian Demand: {row['pedestrian_demand_score']:.3f}<br>
    Turkish Competition: {row['turkish_competition_score']:.3f}<br>
    Rent Cost: {row['rent_score']:.3f}
    """

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=8,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.55,
        weight=2,
        tooltip="2019 Comparison — 59th Street",
        popup=folium.Popup(popup, max_width=320),
    ).add_to(comparison_layer)


# Highlight the comparison corridor

folium.Rectangle(
    bounds=[
        [40.758, -73.985],
        [40.772, -73.970],
    ],
    color="red",
    weight=2,
    dash_array="6",
    fill=False,
    tooltip="2019 Recommended Area — 59th Street / Central Park South",
).add_to(comparison_layer)

comparison_layer.add_to(m)


# -------------------------------------------------
# Legend
# -------------------------------------------------

legend_html = """
<div style="
    position: fixed;
    bottom: 35px;
    left: 35px;
    width: 280px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    padding: 12px;
    font-size: 13px;
">
<b>Restaurant Location Analysis</b><br><br>

<span style="color:blue;">●</span>
2026 Robust Candidate<br>

<span style="color:black;">●</span>
2026 Opportunity Zone Center<br>

<span style="color:red;">●</span>
2019 Comparison Area<br><br>

<b>2019 → 2026</b><br>
Same location problem,<br>
expanded data and methodology.
</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)


# -------------------------------------------------
# Layer control
# -------------------------------------------------

folium.LayerControl(
    collapsed=False
).add_to(m)


# -------------------------------------------------
# Fit map
# Include both 2026 robust candidates
# and 2019 comparison area
# -------------------------------------------------

all_lat = pd.concat([
    candidates["latitude"],
    area_2019["latitude"],
])

all_lon = pd.concat([
    candidates["longitude"],
    area_2019["longitude"],
])

m.fit_bounds(
    [
        [all_lat.min(), all_lon.min()],
        [all_lat.max(), all_lon.max()],
    ]
)


# -------------------------------------------------
# Save
# -------------------------------------------------

m.save(OUTPUT_FILE)

print("\nFINAL MAP")
print("=" * 70)
print("2026 robust candidates:", len(candidates))
print("2026 opportunity zones:", len(zones))
print("2019 comparison cells:", len(area_2019))
print("Saved:", OUTPUT_FILE)