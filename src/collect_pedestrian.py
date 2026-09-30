from pathlib import Path
import pandas as pd
import requests
from io import StringIO

URL = "https://data.cityofnewyork.us/resource/cqsj-cfgu.csv?$limit=500"
OUTPUT_FILE = Path("data/nyc_pedestrian_counts.csv")

HEADERS = {
    "User-Agent": "restaurant-location-analysis/1.0"
}


def main():

    print("Downloading NYC DOT pedestrian counts...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Pedestrian dataset created")
    print("--------------------------")
    print("Locations:", len(df))
    print("Columns:", len(df.columns))

    print()
    print("Available columns:")
    print(list(df.columns))

    if "borough" in df.columns:
        print()
        print("Borough distribution:")
        print(df["borough"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
