import pandas as pd

FILE = "data/study_area_candidate_features.csv"

df = pd.read_csv(FILE)

# -------------------------------------------------
# Rank-normalize predicted pedestrian demand
# -------------------------------------------------

rank = df["predicted_pedestrian_demand"].rank(
    method="average"
)

df["pedestrian_demand_score"] = (
    (rank - rank.min()) /
    (rank.max() - rank.min())
)

# -------------------------------------------------
# Save
# -------------------------------------------------

df.to_csv(FILE, index=False)

print(
    df["pedestrian_demand_score"].describe()
)

print("\nTOP 20 PEDESTRIAN DEMAND SCORES")
print("--------------------------------")

print(
    df.nlargest(
        20,
        "pedestrian_demand_score",
    )[
        [
            "candidate_id",
            "borough",
            "predicted_pedestrian_demand",
            "pedestrian_demand_score",
        ]
    ].to_string(index=False)
)