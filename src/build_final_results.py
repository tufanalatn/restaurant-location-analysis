import pandas as pd
from pathlib import Path


INPUT_FILE = "data/opportunity_zones.csv"
OUTPUT_FILE = "data/final_opportunity_zones.csv"


# -------------------------------------------------
# Load technical opportunity zones
# -------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# -------------------------------------------------
# Human-readable area names
# Technical DBSCAN zone IDs remain unchanged.
# -------------------------------------------------

AREA_NAMES = {
    1: "Brownsville / East New York",
    2: "Brownsville / East New York",
    3: "Brownsville / East New York",
    4: "East New York / Cypress Hills",
    5: "East New York / Cypress Hills",
    6: "East New York / Cypress Hills",
    7: "East Harlem",
    8: "Morningside Heights / Manhattanville",
    9: "Upper East Harlem / Harlem River",
}

df["area_name"] = df["opportunity_zone"].map(AREA_NAMES)


# -------------------------------------------------
# Keep final reporting fields
# -------------------------------------------------

final = df[
    [
        "opportunity_zone",
        "area_name",
        "borough",
        "candidate_count",
        "center_latitude",
        "center_longitude",
        "mean_pedestrian_score",
        "mean_competition_score",
        "mean_rent_score",
        "mean_average_rank",
        "best_average_rank",
    ]
].copy()


# -------------------------------------------------
# Reporting order
#
# This is NOT a new opportunity ranking.
# We display zones according to their best robust
# candidate rank, then mean rank.
# -------------------------------------------------

final = final.sort_values(
    ["best_average_rank", "mean_average_rank"]
).reset_index(drop=True)


# -------------------------------------------------
# Round reporting values
# -------------------------------------------------

score_columns = [
    "mean_pedestrian_score",
    "mean_competition_score",
    "mean_rent_score",
    "mean_average_rank",
    "best_average_rank",
]

final[score_columns] = final[score_columns].round(3)


# -------------------------------------------------
# Save
# -------------------------------------------------

Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

final.to_csv(
    OUTPUT_FILE,
    index=False,
)


# -------------------------------------------------
# Display
# -------------------------------------------------

print("\nFINAL OPPORTUNITY ZONES")
print("=" * 140)

print(final.to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
print("Zones:", len(final))
print("Robust candidates:", int(final["candidate_count"].sum()))