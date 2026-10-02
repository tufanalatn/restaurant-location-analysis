import math
import pandas as pd

CANDIDATE_FILE = "data/study_area_candidate_features.csv"
TURKISH_FILE = "data/study_area_turkish_restaurants.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"

DECAY_DISTANCE_METERS = 500.0


def haversine_m(lat1, lon1, lat2, lon2):
    """
    Great-circle distance between two coordinates in meters.
    """
    earth_radius_m = 6371000.0

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

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_m * c


def competition_decay(distance_m):
    """
    Competition influence halves every 500 meters.

    0 m    -> 1.00
    500 m  -> 0.50
    1000 m -> 0.25
    1500 m -> 0.125
    """
    return 2 ** (-distance_m / DECAY_DISTANCE_METERS)


def main():
    candidates = pd.read_csv(CANDIDATE_FILE)
    turkish = pd.read_csv(TURKISH_FILE)

    competition_scores = []

    for _, candidate in candidates.iterrows():

        raw_score = 0.0

        for _, restaurant in turkish.iterrows():

            distance = haversine_m(
                candidate["latitude"],
                candidate["longitude"],
                restaurant["latitude"],
                restaurant["longitude"],
            )

            raw_score += competition_decay(distance)

        competition_scores.append(raw_score)

    candidates["turkish_competition_raw"] = competition_scores
    # Percentile/rank normalization:
    # lowest competition -> close to 0
    # highest competition -> 1
    candidates["turkish_competition_score"] = (
        candidates["turkish_competition_raw"]
        .rank(method="average", pct=True)
    )

    # Make the minimum exactly 0 and maximum exactly 1
    min_score = candidates["turkish_competition_score"].min()
    max_score = candidates["turkish_competition_score"].max()

    candidates["turkish_competition_score"] = (
        candidates["turkish_competition_score"] - min_score
    ) / (max_score - min_score)

    candidates.to_csv(OUTPUT_FILE, index=False)

    print("Candidates:", len(candidates))
    print("Turkish restaurants:", len(turkish))

    print("\nCOMPETITION RAW")
    print(candidates["turkish_competition_raw"].describe())

    print("\nPERCENTILES")
    print(
        candidates["turkish_competition_raw"].quantile(
            [0, .10, .25, .50, .75, .90, .95, .99, 1]
        )
    )
    print("\nNORMALIZED COMPETITION SCORE")
    print(candidates["turkish_competition_score"].describe())

    print("\nTOP 15 COMPETITION")
    print(
        candidates[
            [
                "candidate_id",
                "borough",
                "turkish_restaurants_500m",
                "nearest_turkish_m",
                "turkish_competition_raw",
            ]
        ]
        .sort_values("turkish_competition_raw", ascending=False)
        .head(15)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()