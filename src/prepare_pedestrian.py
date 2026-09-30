from pathlib import Path
import re
import pandas as pd

INPUT_FILE = Path("data/nyc_pedestrian_counts.csv")
OUTPUT_FILE = Path("data/study_area_pedestrian_2026.csv")


def extract_coordinates(value):
    match = re.search(
        r"POINT \(([-0-9.]+) ([-0-9.]+)\)",
        str(value)
    )

    if not match:
        return pd.Series([None, None])

    longitude = float(match.group(1))
    latitude = float(match.group(2))

    return pd.Series([latitude, longitude])


def main():

    df = pd.read_csv(INPUT_FILE)

    # 2026 study area: Manhattan + Brooklyn
    study_area = df[
        df["borough"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["manhattan", "brooklyn"])
    ].copy()

    study_area[["latitude", "longitude"]] = (
        study_area["the_geom"].apply(extract_coordinates)
    )

    result = study_area[
        [
            "loc",
            "borough",
            "street_nam",
            "from_stree",
            "to_street",
            "latitude",
            "longitude",
            "may26_am",
            "may26_md",
            "may26_pm",
        ]
    ].copy()

    result["food_activity_raw"] = (
        result["may26_md"] +
        result["may26_pm"]
    ) / 2

    result.to_csv(OUTPUT_FILE, index=False)

    print("Study-area pedestrian dataset created")
    print("-------------------------------------")
    print("Locations:", len(result))
    print("Missing coordinates:",
          result[["latitude", "longitude"]]
          .isna()
          .any(axis=1)
          .sum())

    print()
    print("By borough:")
    print(result["borough"].value_counts())

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
