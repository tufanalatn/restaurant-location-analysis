import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge


# -------------------------------------------------
# Files
# -------------------------------------------------

PEDESTRIAN_FILE = "data/study_area_pedestrian_features.csv"
CANDIDATE_FILE = "data/study_area_candidate_features.csv"
OUTPUT_FILE = "data/study_area_candidate_features.csv"


# -------------------------------------------------
# Load data
# -------------------------------------------------

pedestrian = pd.read_csv(PEDESTRIAN_FILE)
candidates = pd.read_csv(CANDIDATE_FILE)

# Only DOT locations with an actual pedestrian measurement
pedestrian = pedestrian.dropna(
    subset=["food_activity_raw"]
).copy()

print("Training DOT observations:", len(pedestrian))
print("Candidate locations:", len(candidates))

print("\nCandidate columns:")
print(candidates.columns.tolist())


# -------------------------------------------------
# Model features
# -------------------------------------------------

numeric_features = [
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
]

categorical_features = ["borough"]

X_train = pedestrian[
    numeric_features + categorical_features
]

X_candidates = candidates[
    numeric_features + categorical_features
]

y_raw = pedestrian["food_activity_raw"].to_numpy()
y_log = np.log1p(y_raw)


# -------------------------------------------------
# Final Ridge model
# -------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features,
        ),
        (
            "borough",
            OneHotEncoder(
                drop="first",
                handle_unknown="ignore",
            ),
            categorical_features,
        ),
    ]
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", Ridge(alpha=15)),
    ]
)

model.fit(X_train, y_log)

print("\nFinal Ridge model trained.")
print("Alpha: 15")

# -------------------------------------------------
# Predict pedestrian demand for all candidate cells
# -------------------------------------------------

pred_log = model.predict(X_candidates)

candidates["predicted_pedestrian_demand"] = np.maximum(
    np.expm1(pred_log),
    0,
)

print("\nPredicted pedestrian demand:")
print(
    candidates["predicted_pedestrian_demand"].describe()
)

print("\nTOP 20 PREDICTED PEDESTRIAN DEMAND")
print("----------------------------------")

print(
    candidates.nlargest(
        20,
        "predicted_pedestrian_demand",
    )[
        [
            "candidate_id",
            "borough",
            "latitude",
            "longitude",
            "predicted_pedestrian_demand",
            "activity_total_500m",
            "university_demand_raw",
            "office_demand_sqrt_raw",
            "subway_accessibility_score",
        ]
    ].to_string(index=False)
)

# Check our old anomaly
print("\nC0398 CHECK")
print("-----------")

print(
    candidates.loc[
        candidates["candidate_id"] == "C0398",
        [
            "candidate_id",
            "borough",
            "predicted_pedestrian_demand",
            "activity_total_500m",
            "university_demand_raw",
            "office_demand_sqrt_raw",
            "subway_accessibility_score",
        ],
    ].to_string(index=False)
)

# Save
candidates.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\nSaved:", OUTPUT_FILE)