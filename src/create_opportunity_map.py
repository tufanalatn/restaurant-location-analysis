from pathlib import Path
import pandas as pd
import folium

PEDESTRIAN_FILE = Path("data/manhattan_pedestrian_2026.csv")
RESTAURANT_FILE = Path("data/manhattan_restaurants.csv")
OUTPUT_FILE = Path("outputs/maps/manhattan_opportunity_2026.html")

MANHATTAN_CENTER = [40.7580, -73.9855]


def main():

    pedestrian = pd.read_csv(PEDESTRIAN_FILE)
    restaurants = pd.read_csv(RESTAURANT_FILE)

    turkish = restaurants[
        restaurants["cuisine"]
        .fillna("")
        .str.lower()
        .str.contains("turkish")
    ].copy()

    m = folium.Map(
        location=MANHATTAN_CENTER,
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # Pedestrian count layer
    pedestrian_layer = folium.FeatureGroup(
        name="NYC DOT Pedestrian Activity"
    )

    max_activity = pedestrian["food_activity_raw"].max()

    for _, row in pedestrian.iterrows():

        # Scale circle size relative to highest measured activity
        radius = 5 + (row["food_activity_raw"] / max_activity) * 18

        popup = (
            f"<b>{row['street_nam']}</b><br>"
            f"{row['from_stree']} → {row['to_street']}<br><br>"
            f"AM: {row['may26_am']:,.0f}<br>"
            f"MD: {row['may26_md']:,.0f}<br>"
            f"PM: {row['may26_pm']:,.0f}<br>"
            f"<b>MD/PM Activity: {row['food_activity_raw']:,.0f}</b>"
        )

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            popup=popup,
            tooltip=f"{row['street_nam']} — {row['food_activity_raw']:,.0f}",
            fill=True,
            fill_opacity=0.45,
            weight=2,
        ).add_to(pedestrian_layer)

    pedestrian_layer.add_to(m)

    # Turkish restaurant layer
    turkish_layer = folium.FeatureGroup(
        name="Turkish Restaurants"
    )

    for _, row in turkish.iterrows():

        popup = (
            f"<b>{row['name']}</b><br>"
            f"Cuisine: {row['cuisine']}"
        )

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup,
            tooltip=row["name"],
            icon=folium.Icon(
                color="red",
                icon="cutlery",
                prefix="fa"
            ),
        ).add_to(turkish_layer)

    turkish_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    m.save(OUTPUT_FILE)

    print("Opportunity map created")
    print("-----------------------")
    print("Pedestrian locations:", len(pedestrian))
    print("Turkish restaurants:", len(turkish))
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
