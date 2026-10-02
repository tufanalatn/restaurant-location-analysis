import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
)

FILE = "data/study_area_pedestrian_features.csv"

df = pd.read_csv(FILE)

# -------------------------------------------------
# Only DOT observations with real pedestrian count
# -------------------------------------------------

df = df.dropna(subset=["food_activity_raw"]).copy()

print("Valid DOT observations:", len(df))

# -------------------------------------------------
# Features / target
# -------------------------------------------------

numeric_features = [
    "activity_total_500m",
    "university_demand_raw",
    "office_demand_sqrt_raw",
    "subway_accessibility_score",
]

categorical_features = [
    "borough",
]

X = df[numeric_features + categorical_features]

# Pedestrian counts are strongly right-skewed.
# Predict log traffic rather than raw traffic.
y = np.log1p(df["food_activity_raw"])

# -------------------------------------------------
# Preprocessing
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

# -------------------------------------------------
# Simple regularized regression
# -------------------------------------------------

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", Ridge(alpha=1.0)),
    ]
)

# -------------------------------------------------
# 5-fold cross-validation
# -------------------------------------------------

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

pred_log = cross_val_predict(
    model,
    X,
    y,
    cv=cv,
)

# Convert predictions back to pedestrian counts
actual = df["food_activity_raw"].to_numpy()
predicted = np.expm1(pred_log)

# Prevent impossible negative traffic predictions
predicted = np.maximum(predicted, 0)

# -------------------------------------------------
# Metrics
# -------------------------------------------------

mae = mean_absolute_error(actual, predicted)
rmse = root_mean_squared_error(actual, predicted)
r2 = r2_score(actual, predicted)

spearman = pd.Series(actual).corr(
    pd.Series(predicted),
    method="spearman",
)

print("\n5-FOLD CROSS-VALIDATION")
print("-----------------------")
print(f"MAE:      {mae:,.1f}")
print(f"RMSE:     {rmse:,.1f}")
print(f"R²:       {r2:.3f}")
print(f"Spearman: {spearman:.3f}")

# -------------------------------------------------
# Naive benchmark
# Predict training-independent global median
# -------------------------------------------------

median_prediction = np.repeat(
    np.median(actual),
    len(actual),
)

benchmark_mae = mean_absolute_error(
    actual,
    median_prediction,
)

benchmark_rmse = root_mean_squared_error(
    actual,
    median_prediction,
)

benchmark_r2 = r2_score(
    actual,
    median_prediction,
)

print("\nMEDIAN BENCHMARK")
print("----------------")
print(f"MAE:      {benchmark_mae:,.1f}")
print(f"RMSE:     {benchmark_rmse:,.1f}")
print(f"R²:       {benchmark_r2:.3f}")

# -------------------------------------------------
# Improvement vs simple benchmark
# -------------------------------------------------

print("\nIMPROVEMENT VS MEDIAN")
print("---------------------")

print(
    "MAE improvement:",
    f"{100 * (benchmark_mae - mae) / benchmark_mae:.1f}%"
)

print(
    "RMSE improvement:",
    f"{100 * (benchmark_rmse - rmse) / benchmark_rmse:.1f}%"
)

# -------------------------------------------------
# Show actual vs predicted
# -------------------------------------------------

results = df[
    [
        "loc",
        "borough",
        "street_nam",
        "latitude",
        "longitude",
        "food_activity_raw",
    ]
].copy()

results["predicted_pedestrian"] = predicted

results["absolute_error"] = (
    results["food_activity_raw"]
    - results["predicted_pedestrian"]
).abs()

print("\nLARGEST ERRORS")
print("--------------")

print(
    results.nlargest(
        10,
        "absolute_error",
    )[
        [
            "loc",
            "borough",
            "street_nam",
            "food_activity_raw",
            "predicted_pedestrian",
            "absolute_error",
        ]
    ].to_string(index=False)
)