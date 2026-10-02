import pandas as pd

FILE = "data/study_area_candidate_features.csv"

df = pd.read_csv(FILE)

# -------------------------------------------------
# Three business scenarios
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


# -------------------------------------------------
# Calculate opportunity scores
# Higher is always better
# -------------------------------------------------

for name, weights in scenarios.items():

    df[f"opportunity_{name}"] = (
        weights["demand"]
        * df["pedestrian_demand_score"]

        + weights["competition"]
        * (1 - df["turkish_competition_score"])

        + weights["rent"]
        * (1 - df["rent_score"])
    )


# -------------------------------------------------
# Ranking
# -------------------------------------------------

for name in scenarios:

    df[f"rank_{name}"] = (
        df[f"opportunity_{name}"]
        .rank(
            ascending=False,
            method="min",
        )
    )


# -------------------------------------------------
# Rank correlations
# -------------------------------------------------

print("\nSCENARIO RANK CORRELATIONS")
print("--------------------------")

rank_columns = [
    "rank_balanced",
    "rank_demand_led",
    "rank_commercial",
]

print(
    df[rank_columns]
    .corr(method="spearman")
    .round(3)
)


# -------------------------------------------------
# Top 20 overlap
# -------------------------------------------------

top_sets = {}

for name in scenarios:

    top_sets[name] = set(
        df.nsmallest(
            20,
            f"rank_{name}",
        )["candidate_id"]
    )

print("\nTOP-20 OVERLAP")
print("--------------")

scenario_names = list(scenarios.keys())

for i in range(len(scenario_names)):
    for j in range(i + 1, len(scenario_names)):

        a = scenario_names[i]
        b = scenario_names[j]

        overlap = len(
            top_sets[a] & top_sets[b]
        )

        print(
            f"{a:12s} vs {b:12s}: "
            f"{overlap}/20"
        )


# -------------------------------------------------
# Candidates appearing in ALL three Top 20 lists
# -------------------------------------------------

stable_top = set.intersection(
    *top_sets.values()
)

print("\nCANDIDATES IN TOP 20 OF ALL 3 SCENARIOS")
print("---------------------------------------")
print("Count:", len(stable_top))


stable = df[
    df["candidate_id"].isin(stable_top)
].copy()

stable["average_rank"] = stable[
    rank_columns
].mean(axis=1)

stable = stable.sort_values(
    "average_rank"
)


print(
    stable[
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "pedestrian_demand_score",
            "turkish_competition_score",
            "rent_score",
            "rank_balanced",
            "rank_demand_led",
            "rank_commercial",
            "average_rank",
        ]
    ].to_string(index=False)
)


# -------------------------------------------------
# Top 10 for each scenario
# -------------------------------------------------

for name in scenarios:

    print(
        f"\nTOP 10 — {name.upper()}"
    )
    print("-" * 60)

    print(
        df.nsmallest(
            10,
            f"rank_{name}",
        )[
            [
                "candidate_id",
                "borough",
                "pedestrian_demand_score",
                "turkish_competition_score",
                "rent_score",
                f"opportunity_{name}",
                f"rank_{name}",
            ]
        ].to_string(index=False)
    )


# -------------------------------------------------
# Save
# -------------------------------------------------

df.to_csv(
    FILE,
    index=False,
)

print("\nSaved:", FILE)