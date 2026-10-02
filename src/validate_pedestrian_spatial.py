import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
)

FILE = "data/study_area_pedestrian_features.csv"

df = pd.read_csv(FILE)

# -------------------------------------------------
# Valid measured pedestrian observations
# -------------------------------------------------

df = df.dropna(subset=["food_activity_raw"]).copy()
df = df.reset_index(drop=True)

print("Valid DOT observations:", len(df))

# -------------------------------------------------
# Create 5 geographic groups
#
# IMPORTANT:
# KMeans is NOT our pedestrian model.
# It is only being used to create spatially coherent
# validation regions.
# -------------------------------------------------

coords = df[["latitude", "longitude"]]

spatial_clusterer = KMeans(
    n_clusters=5,
    random_state=42,
    n_init=20,
)

df["spatial_group"] = spatial_clusterer.fit_predict(coords)

print("\nSpatial groups:")
print(
    df.groupby("spatial_group").agg(
        points=("loc", "count"),
        boroughs=("borough", lambda x: ", ".join(sorted(set(x)))),
        mean_lat=("latitude", "mean"),
        mean_lon=("longitude", "mean"),
        pedestrian_median=("food_activity_raw", "median"),
    )
)

# -------------------------------------------------
# Features
# -------------------------------------------------

numeric_features = [
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
]

categorical_features = ["borough"]

X = df[numeric_features + categorical_features]
y_raw = df["food_activity_raw"].to_numpy()
y_log = np.log1p(y_raw)

groups = df["spatial_group"].to_numpy()

# -------------------------------------------------
# Preprocessing + Ridge
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
        ("model", Ridge(alpha=1.0)),
    ]
)

# -------------------------------------------------
# Leave-One-Spatial-Group-Out validation
# -------------------------------------------------

logo = LeaveOneGroupOut()

predicted = np.zeros(len(df))
benchmark = np.zeros(len(df))

fold_rows = []

for fold, (train_idx, test_idx) in enumerate(
    logo.split(X, y_log, groups),
    start=1,
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train_log = y_log[train_idx]

    model.fit(X_train, y_train_log)

    pred_log = model.predict(X_test)
    pred_raw = np.maximum(np.expm1(pred_log), 0)

    predicted[test_idx] = pred_raw

    # Proper benchmark:
    # median calculated ONLY from training observations
    train_median = np.median(y_raw[train_idx])
    benchmark[test_idx] = train_median

    group_id = groups[test_idx][0]

    fold_rows.append(
        {
            "fold": fold,
            "spatial_group": group_id,
            "train_points": len(train_idx),
            "test_points": len(test_idx),
            "test_boroughs": ", ".join(
                sorted(set(df.iloc[test_idx]["borough"]))
            ),
        }
    )

# -------------------------------------------------
# Overall metrics
# -------------------------------------------------

mae = mean_absolute_error(y_raw, predicted)
rmse = root_mean_squared_error(y_raw, predicted)
r2 = r2_score(y_raw, predicted)

spearman = pd.Series(y_raw).corr(
    pd.Series(predicted),
    method="spearman",
)

benchmark_mae = mean_absolute_error(y_raw, benchmark)
benchmark_rmse = root_mean_squared_error(y_raw, benchmark)
benchmark_r2 = r2_score(y_raw, benchmark)

print("\nSPATIAL CROSS-VALIDATION")
print("------------------------")
print(f"MAE:      {mae:,.1f}")
print(f"RMSE:     {rmse:,.1f}")
print(f"R²:       {r2:.3f}")
print(f"Spearman: {spearman:.3f}")

print("\nTRAIN-MEDIAN BENCHMARK")
print("----------------------")
print(f"MAE:      {benchmark_mae:,.1f}")
print(f"RMSE:     {benchmark_rmse:,.1f}")
print(f"R²:       {benchmark_r2:.3f}")

print("\nIMPROVEMENT VS BENCHMARK")
print("------------------------")
print(
    "MAE improvement:",
    f"{100 * (benchmark_mae - mae) / benchmark_mae:.1f}%"
)
print(
    "RMSE improvement:",
    f"{100 * (benchmark_rmse - rmse) / benchmark_rmse:.1f}%"
)

# -------------------------------------------------
# Fold information
# -------------------------------------------------

print("\nSPATIAL FOLDS")
print("-------------")
print(pd.DataFrame(fold_rows).to_string(index=False))

# -------------------------------------------------
# Per-group performance
# -------------------------------------------------

df["predicted_pedestrian"] = predicted
df["benchmark_prediction"] = benchmark
df["absolute_error"] = np.abs(y_raw - predicted)

print("\nPER-GROUP PERFORMANCE")
print("---------------------")

for group_id in sorted(df["spatial_group"].unique()):

    part = df[df["spatial_group"] == group_id]

    group_mae = mean_absolute_error(
        part["food_activity_raw"],
        part["predicted_pedestrian"],
    )

    group_spearman = part["food_activity_raw"].corr(
        part["predicted_pedestrian"],
        method="spearman",
    )

    print(
        f"Group {group_id}: "
        f"n={len(part)}, "
        f"MAE={group_mae:,.1f}, "
        f"Spearman={group_spearman:.3f}"
    )

# -------------------------------------------------
# Largest errors
# -------------------------------------------------

print("\nLARGEST SPATIAL-CV ERRORS")
print("-------------------------")

print(
    df.nlargest(10, "absolute_error")[
        [
            "loc",
            "borough",
            "street_nam",
            "spatial_group",
            "food_activity_raw",
            "predicted_pedestrian",
            "absolute_error",
        ]
    ].to_string(index=False)
)