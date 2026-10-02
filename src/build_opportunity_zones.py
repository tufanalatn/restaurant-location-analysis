import pandas as pd
import numpy as np

from sklearn.cluster import DBSCAN


FILE = "data/study_area_candidate_features.csv"

df = pd.read_csv(FILE)


# -------------------------------------------------
# Robust candidates
# Top 20 in ALL three sensitivity scenarios
# -------------------------------------------------

robust = df[
    (df["rank_balanced"] <= 20)
    & (df["rank_demand_led"] <= 20)
    & (df["rank_commercial"] <= 20)
].copy()

print("Robust candidates:", len(robust))


# -------------------------------------------------
# Geographic clustering
#
# Candidate grid spacing is approximately 500m.
# eps = 750m allows directly neighboring grid cells
# to form the same opportunity zone.
# -------------------------------------------------

EARTH_RADIUS_KM = 6371.0088
EPS_METERS = 750

coords_radians = np.radians(
    robust[["latitude", "longitude"]].to_numpy()
)

eps_radians = (
    EPS_METERS / 1000
) / EARTH_RADIUS_KM


clusterer = DBSCAN(
    eps=eps_radians,
    min_samples=1,
    metric="haversine",
)

robust["opportunity_zone"] = (
    clusterer.fit_predict(coords_radians) + 1
)


# -------------------------------------------------
# Average sensitivity rank
# -------------------------------------------------

robust["average_rank"] = robust[
    [
        "rank_balanced",
        "rank_demand_led",
        "rank_commercial",
    ]
].mean(axis=1)


# -------------------------------------------------
# Zone summary
# -------------------------------------------------

zones = (
    robust.groupby(
        ["opportunity_zone", "borough"]
    )
    .agg(
        candidate_count=("candidate_id", "count"),

        center_latitude=("latitude", "mean"),
        center_longitude=("longitude", "mean"),

        mean_pedestrian_score=(
            "pedestrian_demand_score",
            "mean",
        ),

        mean_competition_score=(
            "turkish_competition_score",
            "mean",
        ),

        mean_rent_score=(
            "rent_score",
            "mean",
        ),

        mean_average_rank=(
            "average_rank",
            "mean",
        ),

        best_average_rank=(
            "average_rank",
            "min",
        ),
    )
    .reset_index()
)


zones = zones.sort_values(
    [
        "candidate_count",
        "mean_average_rank",
    ],
    ascending=[
        False,
        True,
    ],
)


# -------------------------------------------------
# Print zones
# -------------------------------------------------

print("\nOPPORTUNITY ZONES")
print("-----------------")

print(
    zones.to_string(
        index=False,
        formatters={
            "center_latitude": "{:.5f}".format,
            "center_longitude": "{:.5f}".format,
            "mean_pedestrian_score": "{:.3f}".format,
            "mean_competition_score": "{:.3f}".format,
            "mean_rent_score": "{:.3f}".format,
            "mean_average_rank": "{:.1f}".format,
            "best_average_rank": "{:.1f}".format,
        },
    )
)


# -------------------------------------------------
# Candidates by zone
# -------------------------------------------------

print("\nCANDIDATES BY ZONE")
print("------------------")

for zone_id in sorted(
    robust["opportunity_zone"].unique()
):

    part = robust[
        robust["opportunity_zone"] == zone_id
    ].sort_values("average_rank")

    print(f"\nZONE {zone_id}")

    print(
        part[
            [
                "candidate_id",
                "borough",
                "latitude",
                "longitude",
                "pedestrian_demand_score",
                "turkish_competition_score",
                "rent_score",
                "average_rank",
            ]
        ].to_string(index=False)
    )


# -------------------------------------------------
# Save
# -------------------------------------------------

robust.to_csv(
    "data/opportunity_zone_candidates.csv",
    index=False,
)

zones.to_csv(
    "data/opportunity_zones.csv",
    index=False,
)

print(
    "\nSaved:"
    "\ndata/opportunity_zone_candidates.csv"
    "\ndata/opportunity_zones.csv"
)