from pathlib import Path
import math
import pandas as pd

FEATURE_FILE = Path("data/study_area_candidate_features.csv")
ACTIVITY_FILE = Path("data/study_area_activity.csv")
OUTPUT_FILE = FEATURE_FILE

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
    activity = pd.read_csv(ACTIVITY_FILE)

    restaurants = activity[
        activity["amenity"] == "restaurant"
    ].copy()

    turkish = restaurants[
        restaurants["cuisine"]
        .fillna("")
        .str.lower()
        .str.contains("turkish")
    ].copy()

    print("Candidates:", len(candidates))
    print("Turkish-tagged restaurants:", len(turkish))
    print()
    print(turkish["borough"].value_counts())

    competition_counts = []
    nearest_distances = []

    for _, candidate in candidates.iterrows():

        distances = []

        for _, restaurant in turkish.iterrows():

            distance = haversine_m(
                candidate["latitude"],
                candidate["longitude"],
                restaurant["latitude"],
                restaurant["longitude"],
            )

            distances.append(distance)

        competition_counts.append(
            sum(
                distance <= RADIUS_METERS
                for distance in distances
            )
        )

        nearest_distances.append(
            round(min(distances), 1)
        )

    candidates["turkish_restaurants_500m"] = competition_counts
    candidates["nearest_turkish_m"] = nearest_distances

    candidates.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Turkish competition features created")
    print("------------------------------------")

    print(
        candidates[
            [
                "turkish_restaurants_500m",
                "nearest_turkish_m",
            ]
        ].describe()
    )

    print()
    print("Candidates with no Turkish restaurant within 500m:")
    print(
        (candidates["turkish_restaurants_500m"] == 0).sum()
    )

    print()
    print("Top activity candidates:")
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
                "turkish_restaurants_500m",
                "nearest_turkish_m",
            ]
        ].to_string(index=False)
    )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()


