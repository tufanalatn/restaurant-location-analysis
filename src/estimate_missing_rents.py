import json
from pathlib import Path

import pandas as pd
from shapely.geometry import shape


FEATURE_FILE = Path("data/study_area_candidate_features.csv")
TRACT_FILE = Path("data/nyc_census_tracts_2020.geojson")

K_NEIGHBORS = 5


def main():

    candidates = pd.read_csv(FEATURE_FILE)

    # IDs must be strings
    candidates["boroct2020"] = (
        candidates["boroct2020"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )

    # -------------------------------------------------
    # Load Census Tract geometries and centroids
    # -------------------------------------------------

    with open(TRACT_FILE) as f:
        geojson = json.load(f)

    tract_locations = {}

    for feature in geojson["features"]:

        props = feature["properties"]

        if props["boroname"] not in ["Manhattan", "Brooklyn"]:
            continue

        geometry = shape(feature["geometry"])

        # representative_point is guaranteed to lie inside
        # the tract and is safer than centroid for irregular polygons
        p = geometry.representative_point()

        tract_locations[str(props["boroct2020"])] = {
            "borough": props["boroname"],
            "latitude": p.y,
            "longitude": p.x,
        }

    # -------------------------------------------------
    # One record per tract represented in our grid
    # -------------------------------------------------

    tracts = (
        candidates[
            [
                "boroct2020",
                "borough",
                "rent_monthly_sqft_2024",
            ]
        ]
        .drop_duplicates("boroct2020")
        .copy()
    )

    tracts["latitude"] = tracts["boroct2020"].map(
        lambda x: tract_locations.get(x, {}).get("latitude")
    )

    tracts["longitude"] = tracts["boroct2020"].map(
        lambda x: tract_locations.get(x, {}).get("longitude")
    )

    # -------------------------------------------------
    # Estimate missing rent
    # -------------------------------------------------

    estimated_rents = {}
    estimation_distances = {}

    for _, target in tracts[
        tracts["rent_monthly_sqft_2024"].isna()
    ].iterrows():

        available = tracts[
            (tracts["borough"] == target["borough"])
            & tracts["rent_monthly_sqft_2024"].notna()
        ].copy()

        # Approximate NYC distance.
        # 1 degree latitude ~111 km
        # 1 degree longitude ~84 km
        available["distance_m"] = (
            (
                (available["latitude"] - target["latitude"])
                * 111000
            ) ** 2
            +
            (
                (available["longitude"] - target["longitude"])
                * 84000
            ) ** 2
        ) ** 0.5

        nearest = available.nsmallest(
            K_NEIGHBORS,
            "distance_m",
        )

        tract_id = target["boroct2020"]

        estimated_rents[tract_id] = (
            nearest["rent_monthly_sqft_2024"].median()
        )

        # Distance to nearest tract actually used
        estimation_distances[tract_id] = (
            nearest["distance_m"].min()
        )

    # -------------------------------------------------
    # Build model rent
    # -------------------------------------------------

    candidates["rent_monthly_sqft_2024_model"] = (
        candidates["rent_monthly_sqft_2024"]
    )

    missing = candidates[
        "rent_monthly_sqft_2024_model"
    ].isna()

    candidates.loc[
        missing,
        "rent_monthly_sqft_2024_model",
    ] = candidates.loc[
        missing,
        "boroct2020",
    ].map(estimated_rents)

    candidates["rent_source"] = "direct"

    candidates.loc[
        missing,
        "rent_source",
    ] = "estimated_nearby"

    candidates["rent_estimation_distance_m"] = 0.0

    candidates.loc[
        missing,
        "rent_estimation_distance_m",
    ] = candidates.loc[
        missing,
        "boroct2020",
    ].map(estimation_distances)

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    candidates.to_csv(
        FEATURE_FILE,
        index=False,
    )

    # -------------------------------------------------
    # QA
    # -------------------------------------------------

    print("Rent model completed")
    print("--------------------")

    print("\nRent source:")
    print(candidates["rent_source"].value_counts())

    print(
        "\nMissing model rent:",
        candidates[
            "rent_monthly_sqft_2024_model"
        ].isna().sum(),
    )

    print("\nModel rent by borough:")
    print(
        candidates.groupby("borough")[
            "rent_monthly_sqft_2024_model"
        ].describe()
    )

    estimated = candidates[
        candidates["rent_source"] == "estimated_nearby"
    ]

    print("\nEstimation distance (meters):")
    print(
        estimated[
            "rent_estimation_distance_m"
        ].describe()
    )

    print("\nEstimated rent examples:")
    print(
        estimated[
            [
                "candidate_id",
                "borough",
                "boroct2020",
                "rent_monthly_sqft_2024_model",
                "rent_estimation_distance_m",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("\nSaved:", FEATURE_FILE)


if __name__ == "__main__":
    main()