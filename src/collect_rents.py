from pathlib import Path
import requests
import pandas as pd
from io import StringIO

URL = "https://data.cityofnewyork.us/resource/dxru-eun8.csv?$limit=10000"

OUTPUT_FILE = Path("data/nyc_storefront_rents.csv")

HEADERS = {
    "User-Agent": "restaurant-location-analysis/1.0"
}


def main():

    print("Downloading NYC storefront rent data...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Storefront rent dataset created")
    print("--------------------------------")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print()
    print("Reporting years:")
    print(df["reporting_year"].value_counts().sort_index())

    print()
    print("Aggregate levels:")
    print(df["aggregate_level_citywide"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
