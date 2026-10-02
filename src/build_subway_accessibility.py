import pandas as pd

INPUT_FILE = "data/study_area_candidate_features.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"


def subway_count_score(count):
    if count == 0:
        return 0.00
    elif count == 1:
        return 0.50
    elif count == 2:
        return 0.75
    elif count == 3:
        return 0.90
    else:
        return 1.00


def subway_proximity_score(distance_m):
    """
    0 m   -> 1.0
    250 m -> 0.5
    500 m -> 0.0
    >500m -> 0.0
    """
    return max(0.0, 1.0 - (distance_m / 500.0))


def main():
    df = pd.read_csv(INPUT_FILE)

    df["subway_count_score"] = (
        df["subway_500m"]
        .apply(subway_count_score)
    )

    df["subway_proximity_score"] = (
        df["nearest_subway_m"]
        .apply(subway_proximity_score)
    )

    # Baseline assumption:
    # 50% nearby station count + 50% nearest-station proximity
    df["subway_accessibility_score"] = (
        0.50 * df["subway_count_score"]
        + 0.50 * df["subway_proximity_score"]
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("Candidates:", len(df))

    print("\nSUBWAY ACCESSIBILITY")
    print(df["subway_accessibility_score"].describe())

    print("\nTOP 10")
    print(
        df[
            [
                "candidate_id",
                "borough",
                "subway_500m",
                "nearest_subway_m",
                "subway_count_score",
                "subway_proximity_score",
                "subway_accessibility_score",
            ]
        ]
        .sort_values("subway_accessibility_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()