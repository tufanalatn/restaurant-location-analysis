from pathlib import Path

import pandas as pd
import folium
from folium.plugins import HeatMap

INPUT_FILE = Path("data/study_area_candidate_features.csv")
OUTPUT_FILE = Path("outputs/maps/study_area_activity_heatmap.html")


def main():

    df = pd.read_csv(INPUT_FILE)

    m = folium.Map(
        location=[40.72, -73.96],
        zoom_start=11,
        tiles="OpenStreetMap",
    )

    # Heatmap: food/social activity density
    heat_data = [
        [
            row["latitude"],
            row["longitude"],
            row["activity_total_500m"],
        ]
        for _, row in df.iterrows()
    ]

    HeatMap(
        heat_data,
        radius=18,
        blur=22,
        min_opacity=0.25,
    ).add_to(m)

    # Top 20 candidate points
    top20 = df.nlargest(
        20,
        "activity_total_500m"
    )

    for _, row in top20.iterrows():

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=5,
            weight=2,
            fill=True,
            fill_opacity=0.8,
            tooltip=(
                f'{row["candidate_id"]} | '
                f'{row["borough"]} | '
                f'Activity: {row["activity_total_500m"]}'
            ),
        ).add_to(m)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    m.save(OUTPUT_FILE)

    print("Activity heatmap created")
    print("Candidates:", len(df))
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()