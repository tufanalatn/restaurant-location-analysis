import pandas as pd

INPUT_FILE = "data/study_area_candidate_features.csv"

df = pd.read_csv(INPUT_FILE)

# -------------------------------------------------
# 2019 comparison area
#
# Report result:
# "59th Street, close to Central Park"
#
# We therefore use the Central Park South / 59th Street
# corridor rather than inventing a single 2019 coordinate.
#
# Approximate bounding box:
# latitude  : 40.758 - 40.772
# longitude : -73.985 - -73.970
# -------------------------------------------------

area = df[
    (df["borough"] == "Manhattan")
    & (df["latitude"].between(40.758, 40.772))
    & (df["longitude"].between(-73.985, -73.970))
].copy()

print("\n2019 AREA — 59th Street / Central Park South")
print("=" * 70)

print("Grid candidates:", len(area))

columns = [
    "candidate_id",
    "latitude",
    "longitude",
    "pedestrian_demand_score",
    "turkish_competition_score",
    "rent_score",
]

print(
    area[columns]
    .sort_values("pedestrian_demand_score", ascending=False)
    .to_string(index=False)
)

print("\nAREA SUMMARY")
print("=" * 70)

for col in [
    "pedestrian_demand_score",
    "turkish_competition_score",
    "rent_score",
]:
    print(
        f"{col:30s}"
        f" mean={area[col].mean():.3f}"
        f" min={area[col].min():.3f}"
        f" max={area[col].max():.3f}"
    )

# -------------------------------------------------
# 2026 Opportunity comparison
# -------------------------------------------------

scenarios = {
    "balanced": {
        "demand": 1 / 3,
        "competition": 1 / 3,
        "rent": 1 / 3,
    },
    "demand_led": {
        "demand": 0.50,
        "competition": 0.25,
        "rent": 0.25,
    },
    "commercial": {
        "demand": 0.40,
        "competition": 0.20,
        "rent": 0.40,
    },
}

print("\n2026 OPPORTUNITY RANKING")
print("=" * 70)

for scenario_name, weights in scenarios.items():

    score_col = f"{scenario_name}_score"
    rank_col = f"{scenario_name}_rank"

    # Higher demand is good.
    # Higher competition and higher rent are bad.
    df[score_col] = (
        weights["demand"] * df["pedestrian_demand_score"]
        + weights["competition"] * (1 - df["turkish_competition_score"])
        + weights["rent"] * (1 - df["rent_score"])
    )

    df[rank_col] = (
        df[score_col]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # Get the same 2019-area candidates from the fully ranked dataframe
    area_ranked = df[df["candidate_id"].isin(area["candidate_id"])].copy()

    best = area_ranked.loc[area_ranked[rank_col].idxmin()]

    mean_rank = area_ranked[rank_col].mean()
    median_rank = area_ranked[rank_col].median()

    best_percentile = (
        1 - ((best[rank_col] - 1) / (len(df) - 1))
    ) * 100

    print(f"\n{scenario_name.upper()}")
    print(f"  Best candidate : {best['candidate_id']}")
    print(f"  Best score     : {best[score_col]:.3f}")
    print(f"  Best rank      : {int(best[rank_col])} / {len(df)}")
    print(f"  Percentile     : {best_percentile:.1f}%")
    print(f"  Mean area rank : {mean_rank:.1f}")
    print(f"  Median rank    : {median_rank:.1f}")