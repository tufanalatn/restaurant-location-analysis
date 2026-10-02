import pandas as pd
import numpy as np


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
# Create borough-aware balanced spatial groups
# -------------------------------------------------

df["spatial_group"] = -1

group_id = 0

for borough in ["Manhattan", "Brooklyn"]:

    mask = df["borough"] == borough

    borough_df = df.loc[mask].sort_values("latitude")

    # Divide each borough into 3 approximately equal
    # north-south geographic bands
    bands = pd.qcut(
        borough_df["latitude"],
        q=3,
        labels=False,
        duplicates="drop",
    )

    df.loc[borough_df.index, "spatial_group"] = (
        bands + group_id
    )

    group_id += 3

df["spatial_group"] = df["spatial_group"].astype(int)

print("\nSpatial groups:")

print(
    df.groupby("spatial_group").agg(
        points=("loc", "count"),
        borough=("borough", "first"),
        min_lat=("latitude", "min"),
        max_lat=("latitude", "max"),
        pedestrian_median=("food_activity_raw", "median"),
    )
)
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


# -------------------------------------------------
# Alpha sweep with identical spatial CV
# -------------------------------------------------

alphas = [10, 15, 20, 25, 30, 35, 40, 45, 50]

logo = LeaveOneGroupOut()

sweep_results = []

for alpha in alphas:

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", Ridge(alpha=alpha)),
        ]
    )

    predicted = np.zeros(len(df))
    benchmark = np.zeros(len(df))

    for train_idx, test_idx in logo.split(X, y_log, groups):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train_log = y_log[train_idx]

        model.fit(X_train, y_train_log)

        pred_log = model.predict(X_test)
        pred_raw = np.maximum(np.expm1(pred_log), 0)

        predicted[test_idx] = pred_raw

        train_median = np.median(y_raw[train_idx])
        benchmark[test_idx] = train_median

    mae = mean_absolute_error(y_raw, predicted)
    rmse = root_mean_squared_error(y_raw, predicted)
    r2 = r2_score(y_raw, predicted)

    spearman = pd.Series(y_raw).corr(
        pd.Series(predicted),
        method="spearman",
    )

    sweep_results.append(
        {
            "alpha": alpha,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
            "Spearman": spearman,
        }
    )

results_df = pd.DataFrame(sweep_results)

print("\nRIDGE ALPHA SWEEP")
print("-----------------")

print(
    results_df.to_string(
        index=False,
        formatters={
            "MAE": "{:,.1f}".format,
            "RMSE": "{:,.1f}".format,
            "R2": "{:.3f}".format,
            "Spearman": "{:.3f}".format,
        },
    )
)

best_mae = results_df.loc[
    results_df["MAE"].idxmin()
]

print("\nBEST MAE")
print("--------")
print(best_mae.to_string())

