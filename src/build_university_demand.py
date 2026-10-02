import math
import pandas as pd

CANDIDATE_FILE = "data/study_area_candidate_features.csv"
CAMPUS_FILE = "data/study_area_campus_demand_2024.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"

HALF_LIFE_METERS = 750.0
EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


candidates = pd.read_csv(CANDIDATE_FILE)
campuses = pd.read_csv(CAMPUS_FILE)

print("Candidates:", len(candidates))
print("Campus demand points:", len(campuses))
print(
    "Physical student potential:",
    campuses["physical_student_potential"].sum(),
)

# -------------------------------------------------
# Pre-calculate campus demand weights
#
# sqrt(enrollment) prevents very large institutions
# from dominating the model.
# -------------------------------------------------

campuses["student_weight"] = (
    campuses["physical_student_potential"]
    .fillna(0)
    .clip(lower=0)
    .apply(math.sqrt)
)

university_demand = []

# -------------------------------------------------
# University demand
#
# Each campus contributes:
#
# sqrt(student potential) * 2^(-distance / 750m)
#
# Therefore:
#     0m    -> 100%
#     750m  -> 50%
#     1500m -> 25%
#     2250m -> 12.5%
# -------------------------------------------------

for _, candidate in candidates.iterrows():

    demand_raw = 0.0

    for _, campus in campuses.iterrows():

        distance_m = haversine_m(
            candidate["latitude"],
            candidate["longitude"],
            campus["LATITUDE"],
            campus["LONGITUD"],
        )

        decay = 2 ** (-distance_m / HALF_LIFE_METERS)

        demand_raw += campus["student_weight"] * decay

    university_demand.append(demand_raw)


candidates["university_demand_raw"] = university_demand

candidates.to_csv(OUTPUT_FILE, index=False)

print()
print("University demand raw distribution:")
print(candidates["university_demand_raw"].describe())

print()
print("Percentiles:")
print(
    candidates["university_demand_raw"].quantile(
        [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    )
)

print()
print("Top 20 university demand candidates:")
print(
    candidates.nlargest(20, "university_demand_raw")[
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "activity_total_500m",
            "activity_score",
            "university_demand_raw",
        ]
    ].to_string(index=False)
)

print()
print("C0398:")
print(
    candidates[
        candidates["candidate_id"] == "C0398"
    ][
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "activity_total_500m",
            "activity_score",
            "university_demand_raw",
        ]
    ].to_string(index=False)
)

print()
print("Saved:", OUTPUT_FILE)