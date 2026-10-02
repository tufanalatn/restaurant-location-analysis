import pandas as pd

INPUT_FILE = "data/study_area_candidate_features.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Percentile/rank normalization.
    # Higher activity = better location opportunity.
    df["activity_score"] = (
        df["activity_total_500m"]
        .rank(method="average", pct=True)
    )

    # Rescale so minimum = 0 and maximum = 1
    min_score = df["activity_score"].min()
    max_score = df["activity_score"].max()

    df["activity_score"] = (
        df["activity_score"] - min_score
    ) / (max_score - min_score)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Candidates:", len(df))

    print("\nACTIVITY SCORE")
    print(df["activity_score"].describe())

    print("\nTOP 15 ACTIVITY")
    print(
        df[
            [
                "candidate_id",
                "borough",
                "activity_total_500m",
                "activity_score",
                "subway_accessibility_score",
                "turkish_competition_score",
                "rent_monthly_sqft_2024_model",
            ]
        ]
        .sort_values("activity_score", ascending=False)
        .head(15)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()