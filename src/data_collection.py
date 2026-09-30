import sys
from pathlib import Path

import pandas as pd

sys.path.append("src")
from osm_client import run_query


OUTPUT_FILE = Path("data/manhattan_restaurants.csv")


def get_manhattan_restaurants():

    query = """
    [out:json][timeout:120];

    area
      ["name"="Manhattan"]
      ["boundary"="administrative"]
      ->.searchArea;

    (
      node["amenity"="restaurant"](area.searchArea);
      way["amenity"="restaurant"](area.searchArea);
      relation["amenity"="restaurant"](area.searchArea);
    );

    out center tags;
    """

    data = run_query(query)

    rows = []

    for element in data["elements"]:
        tags = element.get("tags", {})

        # Nodes contain lat/lon directly.
        # Ways and relations return a calculated center.
        lat = element.get("lat")
        lon = element.get("lon")

        if "center" in element:
            lat = element["center"].get("lat")
            lon = element["center"].get("lon")

        rows.append(
            {
                "osm_type": element.get("type"),
                "osm_id": element.get("id"),
                "name": tags.get("name"),
                "cuisine": tags.get("cuisine"),
                "latitude": lat,
                "longitude": lon,
                "address": tags.get("addr:street"),
                "website": tags.get("website"),
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":

    print("Downloading Manhattan restaurants from OpenStreetMap...")

    df = get_manhattan_restaurants()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Dataset created")
    print("-----------------------")
    print("Restaurants:", len(df))
    print("Cuisine known:", df["cuisine"].notna().sum())
    print("Cuisine unknown:", df["cuisine"].isna().sum())
    print("Unique cuisines:", df["cuisine"].nunique())
    print()
    print("Saved:", OUTPUT_FILE)
