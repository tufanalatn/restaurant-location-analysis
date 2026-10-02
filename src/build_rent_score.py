import pandas as pd

INPUT_FILE = "data/study_area_candidate_features.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Percentile/rank normalization.
    # Higher rent = higher cost = worse for opportunity.
    df["rent_score"] = (
        df["rent_monthly_sqft_2024_model"]
        .rank(method="average", pct=True)
    )

    # Rescale so minimum = 0 and maximum = 1
    min_score = df["rent_score"].min()
    max_score = df["rent_score"].max()

    df["rent_score"] = (
        df["rent_score"] - min_score
    ) / (max_score - min_score)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Candidates:", len(df))

    print("\nRENT SCORE")
    print(df["rent_score"].describe())

    print("\nSAMPLE - FOUR MODEL DIMENSIONS")
    print(
        df[
            [
                "candidate_id",
                "borough",
                "activity_score",
                "subway_accessibility_score",
                "turkish_competition_score",
                "rent_monthly_sqft_2024_model",
                "rent_score",
            ]
        ]
        .sort_values("activity_score", ascending=False)
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()