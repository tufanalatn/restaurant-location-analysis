import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


PEDESTRIAN_FILE = "data/study_area_pedestrian_features.csv"
CANDIDATE_FILE = "data/study_area_candidate_features.csv"


# -------------------------------------------------
# Load data
# -------------------------------------------------

pedestrian = pd.read_csv(PEDESTRIAN_FILE)
candidates = pd.read_csv(CANDIDATE_FILE)

pedestrian = pedestrian.dropna(
    subset=["food_activity_raw"]
).copy()


# -------------------------------------------------
# Model features
# -------------------------------------------------

features = [
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
]


# -------------------------------------------------
# Get C0398
# -------------------------------------------------

target = candidates.loc[
    candidates["candidate_id"] == "C0398"
].iloc[0]

print("C0398")
print("-----")

for feature in features:
    print(f"{feature}: {target[feature]:,.3f}")


# -------------------------------------------------
# Standardize using DOT training distribution
# -------------------------------------------------

scaler = StandardScaler()

dot_scaled = scaler.fit_transform(
    pedestrian[features]
)

target_scaled = scaler.transform(
    pd.DataFrame(
        [target[features].to_dict()]
    )
)[0]


# -------------------------------------------------
# Euclidean distance in standardized feature space
# -------------------------------------------------

pedestrian["feature_distance"] = np.sqrt(
    np.sum(
        (dot_scaled - target_scaled) ** 2,
        axis=1,
    )
)


# -------------------------------------------------
# Closest real DOT observations
# -------------------------------------------------

print("\n10 MOST SIMILAR DOT LOCATIONS")
print("-----------------------------")

columns = [
    "loc",
    "borough",
    "street_nam",
    "food_activity_raw",
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
    "feature_distance",
]

print(
    pedestrian.nsmallest(
        10,
        "feature_distance",
    )[columns].to_string(index=False)
)