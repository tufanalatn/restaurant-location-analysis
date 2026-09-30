from pathlib import Path
import math
import pandas as pd

FEATURE_FILE = Path("data/study_area_candidate_features.csv")
SUBWAY_FILE = Path("data/study_area_subway_mta.csv")
OUTPUT_FILE = Path("data/study_area_candidate_features.csv")

RADIUS_METERS = 500
EARTH_RADIUS_METERS = 6371000


def haversine_m(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return EARTH_RADIUS_METERS * c


def main():

    candidates = pd.read_csv(FEATURE_FILE)
    subway = pd.read_csv(SUBWAY_FILE)

    print("Candidates:", len(candidates))
    print("Subway records:", len(subway))

    subway_counts = []
    nearest_distances = []

    for index, candidate in candidates.iterrows():

        distances = []

        for _, station in subway.iterrows():

            distance = haversine_m(
                candidate["latitude"],
                candidate["longitude"],
                station["latitude"],
                station["longitude"],
            )

            distances.append(distance)

        subway_500m = sum(
            distance <= RADIUS_METERS
            for distance in distances
        )

        nearest_subway_m = min(distances)

        subway_counts.append(subway_500m)
        nearest_distances.append(
            round(nearest_subway_m, 1)
        )

    candidates["subway_500m"] = subway_counts
    candidates["nearest_subway_m"] = nearest_distances

    candidates.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Subway features created")
    print("-----------------------")

    print()
    print("Subway records by borough:")
    print(subway["borough_name"].value_counts())

    print()
    print("Candidate subway statistics:")
    print(
        candidates[
            ["subway_500m", "nearest_subway_m"]
        ].describe()
    )

    print()
    print("Top 10 activity candidates + subway:")
    print(
        candidates.nlargest(
            10,
            "activity_total_500m"
        )[
            [
                "candidate_id",
                "borough",
                "activity_total_500m",
                "subway_500m",
                "nearest_subway_m",
            ]
        ].to_string(index=False)
    )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()