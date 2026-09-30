from pathlib import Path

import folium
import pandas as pd


DATA_FILE = Path("data/manhattan_restaurants.csv")
OUTPUT_FILE = Path("outputs/maps/manhattan_turkish_restaurants_2026.html")

BRYANT_PARK = [40.7536, -73.9832]


def main():

    df = pd.read_csv(DATA_FILE)

    turkish = df[
        df["cuisine"]
        .fillna("")
        .str.lower()
        .str.contains("turkish")
    ].copy()

    m = folium.Map(
        location=BRYANT_PARK,
        zoom_start=12,
        tiles="OpenStreetMap",
    )

    # Original 2019 study center
    folium.Marker(
        BRYANT_PARK,
        popup="Bryant Park — 2019 Study Center",
        tooltip="Bryant Park",
        icon=folium.Icon(color="purple", icon="info-sign"),
    ).add_to(m)

    # 2026 Turkish restaurants
    for _, row in turkish.iterrows():

        popup_text = (
            f"<b>{row['name']}</b><br>"
            f"Cuisine: {row['cuisine']}<br>"
            f"OSM ID: {row['osm_id']}"
        )

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            popup=popup_text,
            tooltip=row["name"],
            color="red",
            fill=True,
            fill_opacity=0.8,
        ).add_to(m)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    m.save(OUTPUT_FILE)

    print("Map created")
    print("Turkish restaurants:", len(turkish))
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
