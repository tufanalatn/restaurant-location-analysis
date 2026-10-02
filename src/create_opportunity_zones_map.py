import pandas as pd
import folium


CANDIDATE_FILE = "data/opportunity_zone_candidates.csv"
ZONE_FILE = "data/opportunity_zones.csv"
OUTPUT_FILE = "outputs/maps/opportunity_zones.html"


# -------------------------------------------------
# Load data
# -------------------------------------------------

candidates = pd.read_csv(CANDIDATE_FILE)
zones = pd.read_csv(ZONE_FILE)

print("Robust candidates:", len(candidates))
print("Opportunity zones:", len(zones))


# -------------------------------------------------
# Base map
# -------------------------------------------------

center_lat = candidates["latitude"].mean()
center_lon = candidates["longitude"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles="OpenStreetMap",
)


# -------------------------------------------------
# Robust candidate grid points
# -------------------------------------------------

for _, row in candidates.iterrows():

    popup = f"""
    <b>{row['candidate_id']}</b><br>
    Zone: {int(row['opportunity_zone'])}<br>
    Borough: {row['borough']}<br><br>

    Pedestrian score: {row['pedestrian_demand_score']:.3f}<br>
    Competition score: {row['turkish_competition_score']:.3f}<br>
    Rent score: {row['rent_score']:.3f}<br>
    Average rank: {row['average_rank']:.1f}
    """

    folium.CircleMarker(
        location=[
            row["latitude"],
            row["longitude"],
        ],
        radius=7,
        weight=2,
        fill=True,
        fill_opacity=0.75,
        tooltip=f"{row['candidate_id']} — Zone {int(row['opportunity_zone'])}",
        popup=folium.Popup(
            popup,
            max_width=300,
        ),
    ).add_to(m)


# -------------------------------------------------
# Opportunity zone centers
# -------------------------------------------------

for _, row in zones.iterrows():

    zone_id = int(row["opportunity_zone"])

    popup = f"""
    <b>Opportunity Zone {zone_id}</b><br>
    Borough: {row['borough']}<br>
    Candidates: {int(row['candidate_count'])}<br><br>

    Mean pedestrian score: {row['mean_pedestrian_score']:.3f}<br>
    Mean competition score: {row['mean_competition_score']:.3f}<br>
    Mean rent score: {row['mean_rent_score']:.3f}<br>
    Mean average rank: {row['mean_average_rank']:.1f}
    """

    folium.Marker(
        location=[
            row["center_latitude"],
            row["center_longitude"],
        ],
        tooltip=f"ZONE {zone_id}",
        popup=folium.Popup(
            popup,
            max_width=300,
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                background: white;
                border: 2px solid black;
                border-radius: 50%;
                width: 34px;
                height: 34px;
                line-height: 30px;
            ">
                {zone_id}
            </div>
            """
        ),
    ).add_to(m)


# -------------------------------------------------
# Fit map to candidate extent
# -------------------------------------------------

m.fit_bounds(
    [
        [
            candidates["latitude"].min(),
            candidates["longitude"].min(),
        ],
        [
            candidates["latitude"].max(),
            candidates["longitude"].max(),
        ],
    ]
)


# -------------------------------------------------
# Save
# -------------------------------------------------

m.save(OUTPUT_FILE)

print("Saved:", OUTPUT_FILE)