from pathlib import Path
import requests
import pandas as pd
from io import StringIO

URL = "https://data.ny.gov/resource/5f5g-n3cz.csv?$limit=1000"

OUTPUT_FILE = Path("data/study_area_subway_mta.csv")

HEADERS = {
    "User-Agent": "restaurant-location-analysis/1.0"
}


def main():

    print("Downloading MTA subway stations and complexes...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    print("MTA records downloaded:", len(df))

    # 2026 study area: Manhattan + Brooklyn
    study_area = df[
        df["borough"].astype(str).str.upper().isin(["M", "BK"])
    ].copy()

    study_area["borough_name"] = (
        study_area["borough"]
        .astype(str)
        .str.upper()
        .map({
            "M": "Manhattan",
            "BK": "Brooklyn",
        })
    )

    columns = [
        "complex_id",
        "stop_name",
        "display_name",
        "daytime_routes",
        "latitude",
        "longitude",
        "borough_name",
        "cbd",
        "ada",
    ]

    study_area = study_area[columns].copy()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    study_area.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Study-area MTA subway dataset created")
    print("-------------------------------------")
    print("Stations / complexes:", len(study_area))
    print("Missing coordinates:",
          study_area[["latitude", "longitude"]]
          .isna()
          .any(axis=1)
          .sum())

    print()
    print("By borough:")
    print(study_area["borough_name"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
