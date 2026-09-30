import json
from pathlib import Path

import pandas as pd
from shapely.geometry import Point, shape
from shapely.prepared import prep


FEATURE_FILE = Path("data/study_area_candidate_features.csv")
RENT_FILE = Path("data/nyc_storefront_rents.csv")
TRACT_FILE = Path("data/nyc_census_tracts_2020.geojson")

OUTPUT_FILE = FEATURE_FILE


def main():

    candidates = pd.read_csv(FEATURE_FILE)
    rents = pd.read_csv(RENT_FILE)

    # -------------------------------------------------
    # 2024 Census Tract rent data
    # -------------------------------------------------

    rent_2024 = rents[
        (rents["reporting_year"] == 2024)
        & (
            rents["aggregate_level_citywide"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "census tract"
        )
    ].copy()

    rent_2024["boroct2020"] = (
        rent_2024["aggregate_level_id"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    rent_2024["rent_monthly_sqft_2024"] = pd.to_numeric(
        rent_2024["median_monthly_rent_per_square"],
        errors="coerce",
    )

    rent_lookup = (
        rent_2024
        .drop_duplicates("boroct2020")
        .set_index("boroct2020")["rent_monthly_sqft_2024"]
        .to_dict()
    )

    print("2024 Census Tract rent records:", len(rent_2024))
    print(
        "Rent records with numeric rent:",
        rent_2024["rent_monthly_sqft_2024"].notna().sum(),
    )

    # -------------------------------------------------
    # Census tract geometries
    # -------------------------------------------------

    with open(TRACT_FILE) as f:
        geojson = json.load(f)

    tracts = []

    for feature in geojson["features"]:

        props = feature["properties"]

        if props["boroname"] not in ["Manhattan", "Brooklyn"]:
            continue

        geometry = shape(feature["geometry"])

        tracts.append(
            {
                "boroct2020": str(props["boroct2020"]),
                "borough": props["boroname"],
                "geometry": geometry,
                "prepared": prep(geometry),
            }
        )

    print("Manhattan/Brooklyn tract polygons:", len(tracts))

    # -------------------------------------------------
    # Candidate -> Census Tract
    # -------------------------------------------------

    candidate_tracts = []

    for _, candidate in candidates.iterrows():

        point = Point(
            candidate["longitude"],
            candidate["latitude"],
        )

        matched_tract = None

        # Search only candidate's borough
        for tract in tracts:

            if tract["borough"] != candidate["borough"]:
                continue

            if tract["prepared"].covers(point):
                matched_tract = tract["boroct2020"]
                break

        candidate_tracts.append(matched_tract)

    candidates["boroct2020"] = candidate_tracts

    # -------------------------------------------------
    # Attach rent
    # -------------------------------------------------

    candidates["rent_monthly_sqft_2024"] = (
        candidates["boroct2020"].map(rent_lookup)
    )

    # Approximate annual $/sqft — useful for reporting
    candidates["rent_annual_sqft_2024"] = (
        candidates["rent_monthly_sqft_2024"] * 12
    )

    candidates.to_csv(OUTPUT_FILE, index=False)

    # -------------------------------------------------
    # QA
    # -------------------------------------------------

    print()
    print("Candidate tract matching")
    print("------------------------")
    print("Candidates:", len(candidates))
    print(
        "Matched to census tract:",
        candidates["boroct2020"].notna().sum(),
    )
    print(
        "Candidates with rent:",
        candidates["rent_monthly_sqft_2024"].notna().sum(),
    )

    print()
    print("Rent by borough:")
    print(
        candidates.groupby("borough")[
            "rent_monthly_sqft_2024"
        ].describe()
    )

    print()
    print("Top activity candidates:")
    print(
        candidates.nlargest(
            10,
            "activity_total_500m",
        )[
            [
                "candidate_id",
                "borough",
                "activity_total_500m",
                "subway_500m",
                "turkish_restaurants_500m",
                "boroct2020",
                "rent_monthly_sqft_2024",
            ]
        ].to_string(index=False)
    )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()