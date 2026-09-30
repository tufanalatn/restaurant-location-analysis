import sys
from pathlib import Path
import pandas as pd

sys.path.append("src")
from osm_client import run_query

OUTPUT_FILE = Path("data/manhattan_subway.csv")
BBOX = "40.7000,-74.0200,40.8800,-73.9000"


def collect_subway():
    query = f"""
    [out:json][timeout:60];

    node
      ["railway"="station"]
      ["station"="subway"]
      ({BBOX});

    out tags;
    """

    data = run_query(query)
    rows = []

    for element in data["elements"]:
        tags = element.get("tags", {})

        rows.append({
            "osm_id": element.get("id"),
            "name": tags.get("name"),
            "latitude": element.get("lat"),
            "longitude": element.get("lon"),
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Downloading Manhattan subway stations...")

    df = collect_subway()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Subway dataset created")
    print("----------------------")
    print("Stations:", len(df))
    print("Named:", df["name"].notna().sum())
    print()
    print(df.sort_values("name").to_string(index=False))
    print()
    print("Saved:", OUTPUT_FILE)
