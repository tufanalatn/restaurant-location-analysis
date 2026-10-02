import pandas as pd

FILE = "data/study_area_candidate_features.csv"

df = pd.read_csv(FILE)


def rank_score(series):
    ranks = series.rank(method="average", pct=True)

    # Rescale so actual minimum = 0 and maximum = 1
    return (ranks - ranks.min()) / (ranks.max() - ranks.min())


# -------------------------------------------------
# Normalize University and Office demand
# -------------------------------------------------

df["university_demand_score"] = rank_score(
    df["university_demand_raw"]
)

df["office_demand_score"] = rank_score(
    df["office_demand_sqrt_raw"]
)

# -------------------------------------------------
# Exploratory Population Generator Score
#
# 50/50 is NOT a final business weight.
# It prevents University + Office from entering
# the final model as two independent dimensions.
# -------------------------------------------------

df["population_generator_score"] = (
    0.50 * df["university_demand_score"]
    + 0.50 * df["office_demand_score"]
)

df.to_csv(FILE, index=False)


# -------------------------------------------------
# QA
# -------------------------------------------------

print("Population Generator Score:")
print(df["population_generator_score"].describe())

print("\nSpearman correlations:")
print(
    df[
        [
            "activity_score",
            "university_demand_score",
            "office_demand_score",
            "population_generator_score",
        ]
    ]
    .corr(method="spearman")
    .round(3)
)

# -------------------------------------------------
# White-space exploration
#
# High population generators, relatively low
# existing food/social activity.
# -------------------------------------------------

white_space = df[
    (df["population_generator_score"] >= 0.75)
    & (df["activity_score"] <= 0.50)
].copy()

white_space = white_space.sort_values(
    ["population_generator_score", "activity_score"],
    ascending=[False, True],
)

print("\nHigh Population Generator + Low Activity:")
print("Candidates:", len(white_space))

print(
    white_space[
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "activity_total_500m",
            "activity_score",
            "university_demand_score",
            "office_demand_score",
            "population_generator_score",
            "subway_accessibility_score",
            "turkish_competition_score",
            "rent_score",
        ]
    ]
    .head(30)
    .to_string(index=False)
)

# C0398 sanity check
print("\nC0398:")
print(
    df[df["candidate_id"] == "C0398"][
        [
            "candidate_id",
            "borough",
            "activity_score",
            "university_demand_score",
            "office_demand_score",
            "population_generator_score",
        ]
    ].to_string(index=False)
)

print("\nSaved:", FILE)