import pandas as pd

INPUT_FILE = "data/study_area_activity.csv"
OUTPUT_FILE = "data/study_area_turkish_restaurants.csv"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Reproducible v1 definition:
    # OSM restaurant records whose cuisine tag contains "turkish".
    turkish = df[
        (df["amenity"] == "restaurant")
        & (
            df["cuisine"]
            .fillna("")
            .str.lower()
            .str.contains("turkish")
        )
    ].copy()

    # Avoid duplicate OSM objects if any exist
    turkish = turkish.drop_duplicates(
        subset=["osm_type", "osm_id"]
    )

    turkish = turkish.sort_values(
        ["borough", "name"]
    ).reset_index(drop=True)

    turkish.to_csv(OUTPUT_FILE, index=False)

    print("Turkish restaurants:", len(turkish))
    print("\nBY BOROUGH")
    print(turkish["borough"].value_counts())

    print("\nRESTAURANTS")
    print(
        turkish[
            ["borough", "name", "cuisine", "latitude", "longitude"]
        ].to_string(index=False)
    )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()