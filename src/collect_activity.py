from pathlib import Path
import time
import pandas as pd

from osm_client import run_query

OUTPUT_FILE = Path("data/study_area_activity.csv")

BOROUGHS = ["Manhattan", "Brooklyn"]
AMENITIES = ["restaurant", "cafe", "bar", "fast_food"]


def collect_category(borough, amenity):

    print(f"Downloading {borough} / {amenity}...")

    query = f"""
    [out:json][timeout:90];

    area
      ["name"="{borough}"]
      ["boundary"="administrative"]
      ->.searchArea;

    nwr
      ["amenity"="{amenity}"]
      (area.searchArea);

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
            "borough": borough,
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "cuisine": tags.get("cuisine"),
            "latitude": lat,
            "longitude": lon,
        })

    print(f"  -> {len(rows)} POIs")

    return rows


def main():

    all_rows = []

    for borough in BOROUGHS:

        for amenity in AMENITIES:

            try:
                rows = collect_category(
                    borough,
                    amenity
                )

                all_rows.extend(rows)

            except Exception as e:
                print(f"ERROR: {borough} / {amenity}")
                print(e)

            # Be polite to Overpass
            time.sleep(2)

    df = pd.DataFrame(all_rows)

    df = df.drop_duplicates(
        subset=["osm_type", "osm_id"]
    ).copy()

    df = df.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Study-area activity dataset created")
    print("-----------------------------------")
    print("Total POIs:", len(df))

    print()
    print("By borough:")
    print(df["borough"].value_counts())

    print()
    print("By amenity:")
    print(df["amenity"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
