import sys
from pathlib import Path

import pandas as pd

sys.path.append("src")
from osm_client import run_query

OUTPUT_FILE = Path("data/manhattan_activity.csv")

# Approximate Manhattan study bounding box
BBOX = "40.7000,-74.0200,40.8800,-73.9000"


def collect_activity():

    query = f"""
    [out:json][timeout:120];

    (
      nwr["amenity"="restaurant"]({BBOX});
      nwr["amenity"="cafe"]({BBOX});
      nwr["amenity"="bar"]({BBOX});
      nwr["amenity"="fast_food"]({BBOX});
    );

    out center tags;
    """

    data = run_query(query)

    rows = []

    for element in data["elements"]:

        tags = element.get("tags", {})

        lat = element.get("lat")
        lon = element.get("lon")

        if "center" in element:
            lat = element["center"].get("lat")
            lon = element["center"].get("lon")

        rows.append({
            "osm_type": element.get("type"),
            "osm_id": element.get("id"),
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "cuisine": tags.get("cuisine"),
            "latitude": lat,
            "longitude": lon,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":

    print("Downloading Manhattan activity POIs...")

    df = collect_activity()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Activity dataset created")
    print("-------------------------")
    print("Total POIs:", len(df))
    print()
    print(df["amenity"].value_counts())
    print()
    print("Saved:", OUTPUT_FILE)
