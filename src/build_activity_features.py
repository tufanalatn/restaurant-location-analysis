from pathlib import Path
import math
import pandas as pd

GRID_FILE = Path("data/study_area_candidate_grid.csv")
ACTIVITY_FILE = Path("data/study_area_activity.csv")
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

    grid = pd.read_csv(GRID_FILE)
    activity = pd.read_csv(ACTIVITY_FILE)

    feature_rows = []

    print("Candidates:", len(grid))
    print("Activity POIs:", len(activity))
    print("Radius:", RADIUS_METERS, "meters")
    print()

    for index, candidate in grid.iterrows():

        counts = {
            "restaurant": 0,
            "cafe": 0,
            "bar": 0,
            "fast_food": 0,
        }

        for _, poi in activity.iterrows():

            distance = haversine_m(
                candidate["latitude"],
                candidate["longitude"],
                poi["latitude"],
                poi["longitude"],
            )

            if distance <= RADIUS_METERS:

                amenity = poi["amenity"]

                if amenity in counts:
                    counts[amenity] += 1

        activity_total = sum(counts.values())

        feature_rows.append({
            "candidate_id": candidate["candidate_id"],
            "borough": candidate["borough"],
            "latitude": candidate["latitude"],
            "longitude": candidate["longitude"],
            "restaurants_500m": counts["restaurant"],
            "cafes_500m": counts["cafe"],
            "bars_500m": counts["bar"],
            "fast_food_500m": counts["fast_food"],
            "activity_total_500m": activity_total,
        })

        if (index + 1) % 100 == 0:
            print(
                f"Processed {index + 1} / "
                f"{len(grid)} candidates"
            )

    result = pd.DataFrame(feature_rows)

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Activity features created")
    print("-------------------------")
    print("Candidates:", len(result))

    print()
    print("Top 10 activity candidates:")
    print(
        result.sort_values(
            "activity_total_500m",
            ascending=False
        )[
            [
                "candidate_id",
                "borough",
                "restaurants_500m",
                "cafes_500m",
                "bars_500m",
                "fast_food_500m",
                "activity_total_500m",
            ]
        ].head(10).to_string(index=False)
    )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
