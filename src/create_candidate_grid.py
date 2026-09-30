from pathlib import Path
import json

import pandas as pd
from shapely.geometry import shape, Point

BOUNDARY_FILE = Path("data/nyc_borough_boundaries.geojson")
OUTPUT_FILE = Path("data/study_area_candidate_grid.csv")

BOROUGHS = ["Manhattan", "Brooklyn"]

# Approx. 500 meters at NYC latitude
LAT_STEP = 0.00450
LON_STEP = 0.00595


def load_boroughs():

    with open(BOUNDARY_FILE) as f:
        data = json.load(f)

    boroughs = {}

    for feature in data["features"]:

        name = feature["properties"]["boroname"]

        if name in BOROUGHS:
            boroughs[name] = shape(feature["geometry"])

    return boroughs


def create_grid(borough_name, polygon):

    min_lon, min_lat, max_lon, max_lat = polygon.bounds

    rows = []

    lat = min_lat

    while lat <= max_lat:

        lon = min_lon

        while lon <= max_lon:

            point = Point(lon, lat)

            if polygon.contains(point):

                rows.append({
                    "borough": borough_name,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                })

            lon += LON_STEP

        lat += LAT_STEP

    return rows


def main():

    boroughs = load_boroughs()

    all_rows = []

    for borough_name, polygon in boroughs.items():

        rows = create_grid(
            borough_name,
            polygon
        )

        print(
            f"{borough_name}: "
            f"{len(rows)} candidate points"
        )

        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    df.insert(
        0,
        "candidate_id",
        [
            f"C{i:04d}"
            for i in range(1, len(df) + 1)
        ]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Candidate grid created")
    print("----------------------")
    print("Total candidates:", len(df))

    print()
    print("By borough:")
    print(df["borough"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
