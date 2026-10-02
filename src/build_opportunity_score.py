import pandas as pd

INPUT_FILE = "data/study_area_candidate_features.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Baseline opportunity model
    #
    # Positive dimensions:
    #   activity_score
    #   subway_accessibility_score
    #
    # Negative dimensions:
    #   turkish_competition_score
    #   rent_score
    #
    # Baseline weights are intentionally equal.
    df["opportunity_score"] = (
        0.25 * df["activity_score"]
        + 0.25 * df["subway_accessibility_score"]
        + 0.25 * (1.0 - df["turkish_competition_score"])
        + 0.25 * (1.0 - df["rent_score"])
    )

    df.to_csv(OUTPUT_FILE, index=False)

    columns = [
        "candidate_id",
        "borough",
        "latitude",
        "longitude",
        "activity_score",
        "subway_accessibility_score",
        "turkish_competition_score",
        "rent_monthly_sqft_2024_model",
        "rent_score",
        "opportunity_score",
    ]

    print("Candidates:", len(df))

    print("\nOPPORTUNITY SCORE")
    print(df["opportunity_score"].describe())

    print("\nTOP 20 OVERALL")
    print(
        df[columns]
        .sort_values("opportunity_score", ascending=False)
        .head(20)
        .to_string(index=False)
    )

    print("\nTOP 10 MANHATTAN")
    print(
        df[df["borough"] == "Manhattan"][columns]
        .sort_values("opportunity_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTOP 10 BROOKLYN")
    print(
        df[df["borough"] == "Brooklyn"][columns]
        .sort_values("opportunity_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()