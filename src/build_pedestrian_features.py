import math
import pandas as pd

PEDESTRIAN_FILE = "data/study_area_pedestrian_2026.csv"
ACTIVITY_FILE = "data/study_area_activity.csv"
CAMPUS_FILE = "data/study_area_campus_demand_2024.csv"
OFFICE_FILE = "data/study_area_office_jobs_2023.csv"
SUBWAY_FILE = "data/study_area_subway_mta.csv"

OUTPUT_FILE = "data/study_area_pedestrian_features.csv"

EARTH_RADIUS_M = 6_371_000.0

ACTIVITY_RADIUS_M = 500.0
SUBWAY_RADIUS_M = 500.0
UNIVERSITY_HALF_LIFE_M = 750.0
OFFICE_HALF_LIFE_M = 750.0


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
        math.sqrt(a),
        math.sqrt(1 - a),
    )


ped = pd.read_csv(PEDESTRIAN_FILE)
activity = pd.read_csv(ACTIVITY_FILE)
campus = pd.read_csv(CAMPUS_FILE)
office = pd.read_csv(OFFICE_FILE)
subway = pd.read_csv(SUBWAY_FILE)

office = office[office["office_jobs"] > 0].copy()

# Same transformation selected for Office Demand
office["office_weight"] = office["office_jobs"].apply(math.sqrt)

# Same transformation used in University Demand
campus["university_weight"] = (
    campus["physical_student_potential"].apply(math.sqrt)
)

results = []

for _, p in ped.iterrows():

    lat = p["latitude"]
    lon = p["longitude"]

    # ---------------------------------------------
    # Activity within 500 m
    # ---------------------------------------------

    activity_count = 0

    for _, a in activity.iterrows():
        d = haversine_m(
            lat, lon,
            a["latitude"], a["longitude"]
        )

        if d <= ACTIVITY_RADIUS_M:
            activity_count += 1

    # ---------------------------------------------
    # University Demand
    # ---------------------------------------------

    university_raw = 0.0

    for _, u in campus.iterrows():
        d = haversine_m(
            lat, lon,
            u["LATITUDE"], u["LONGITUD"]
        )

        decay = 2 ** (-d / UNIVERSITY_HALF_LIFE_M)

        university_raw += (
            u["university_weight"] * decay
        )

    # ---------------------------------------------
    # Office Demand
    # ---------------------------------------------

    office_raw = 0.0

    for _, o in office.iterrows():
        d = haversine_m(
            lat, lon,
            o["latitude"], o["longitude"]
        )

        decay = 2 ** (-d / OFFICE_HALF_LIFE_M)

        office_raw += (
            o["office_weight"] * decay
        )

    # ---------------------------------------------
    # Subway
    # ---------------------------------------------

    subway_distances = []

    for _, s in subway.iterrows():
        d = haversine_m(
            lat, lon,
            s["latitude"], s["longitude"]
        )

        subway_distances.append(d)

    nearest_subway_m = min(subway_distances)

    subway_500m = sum(
        d <= SUBWAY_RADIUS_M
        for d in subway_distances
    )

    # Same count rule as candidate model
    if subway_500m == 0:
        count_score = 0.0
    elif subway_500m == 1:
        count_score = 0.50
    elif subway_500m == 2:
        count_score = 0.75
    elif subway_500m == 3:
        count_score = 0.90
    else:
        count_score = 1.0

    proximity_score = max(
        0.0,
        1.0 - nearest_subway_m / SUBWAY_RADIUS_M
    )

    subway_accessibility = (
        0.50 * count_score
        + 0.50 * proximity_score
    )

    results.append(
        {
            **p.to_dict(),
            "activity_total_500m": activity_count,
            "university_demand_raw": university_raw,
            "office_demand_sqrt_raw": office_raw,
            "subway_500m": subway_500m,
            "nearest_subway_m": nearest_subway_m,
            "subway_accessibility_score": subway_accessibility,
        }
    )


out = pd.DataFrame(results)

out.to_csv(OUTPUT_FILE, index=False)

print("DOT points:", len(out))

print("\nFeature summary:")
print(
    out[
        [
            "food_activity_raw",
            "activity_total_500m",
            "university_demand_raw",
            "office_demand_sqrt_raw",
            "subway_accessibility_score",
        ]
    ].describe()
)

print("\nSpearman correlation with REAL pedestrian count:")

cols = [
    "food_activity_raw",
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
]

corr = (
    out[cols]
    .corr(method="spearman")
    ["food_activity_raw"]
    .sort_values(ascending=False)
)

print(corr.round(3))

print("\nBy borough:")

for borough in ["Manhattan", "Brooklyn"]:

    part = out[out["borough"] == borough]

    print("\n", borough, "-", len(part), "DOT points")

    corr = (
        part[cols]
        .corr(method="spearman")
        ["food_activity_raw"]
        .sort_values(ascending=False)
    )

    print(corr.round(3))


print("\nSaved:", OUTPUT_FILE)