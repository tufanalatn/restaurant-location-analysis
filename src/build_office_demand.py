import math
import pandas as pd

CANDIDATE_FILE = "data/study_area_candidate_features.csv"
OFFICE_FILE = "data/study_area_office_jobs_2023.csv"
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

    return EARTH_RADIUS_M * 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )


candidates = pd.read_csv(CANDIDATE_FILE)
office = pd.read_csv(
    OFFICE_FILE,
    dtype={"w_geocode": str},
)

# Blocks with zero office employment contribute nothing.
office = office[office["office_jobs"] > 0].copy()

office["weight_linear"] = office["office_jobs"]
office["weight_sqrt"] = office["office_jobs"].apply(math.sqrt)
office["weight_log"] = office["office_jobs"].apply(math.log1p)

print("Candidates:", len(candidates))
print("Office blocks with jobs:", len(office))
print("Office jobs:", office["office_jobs"].sum())

linear_results = []
sqrt_results = []
log_results = []

for _, candidate in candidates.iterrows():

    linear_raw = 0.0
    sqrt_raw = 0.0
    log_raw = 0.0

    for _, block in office.iterrows():

        distance_m = haversine_m(
            candidate["latitude"],
            candidate["longitude"],
            block["latitude"],
            block["longitude"],
        )

        decay = 2 ** (-distance_m / HALF_LIFE_METERS)

        linear_raw += block["weight_linear"] * decay
        sqrt_raw += block["weight_sqrt"] * decay
        log_raw += block["weight_log"] * decay

    linear_results.append(linear_raw)
    sqrt_results.append(sqrt_raw)
    log_results.append(log_raw)


candidates["office_demand_linear_raw"] = linear_results
candidates["office_demand_sqrt_raw"] = sqrt_results
candidates["office_demand_log_raw"] = log_results

candidates.to_csv(OUTPUT_FILE, index=False)


for col in [
    "office_demand_linear_raw",
    "office_demand_sqrt_raw",
    "office_demand_log_raw",
]:
    print(f"\n{col}")
    print(candidates[col].describe())

    print("\nPercentiles:")
    print(
        candidates[col].quantile(
            [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
        )
    )


print("\nSpearman correlations:")
print(
    candidates[
        [
            "activity_score",
            "university_demand_raw",
            "office_demand_linear_raw",
            "office_demand_sqrt_raw",
            "office_demand_log_raw",
        ]
    ]
    .corr(method="spearman")
    .round(3)
)


print("\nTop 20 by LINEAR office demand:")
print(
    candidates.nlargest(20, "office_demand_linear_raw")[
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "activity_score",
            "university_demand_raw",
            "office_demand_linear_raw",
            "office_demand_sqrt_raw",
            "office_demand_log_raw",
        ]
    ].to_string(index=False)
)


print("\nC0398:")
print(
    candidates[
        candidates["candidate_id"] == "C0398"
    ][
        [
            "candidate_id",
            "borough",
            "activity_score",
            "university_demand_raw",
            "office_demand_linear_raw",
            "office_demand_sqrt_raw",
            "office_demand_log_raw",
        ]
    ].to_string(index=False)
)

print("\nSaved:", OUTPUT_FILE)