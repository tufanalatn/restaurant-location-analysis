import pandas as pd

FEATURE_FILE = "data/study_area_candidate_features.csv"
ROBUST_FILE = "data/opportunity_zone_candidates.csv"

df = pd.read_csv(FEATURE_FILE)
robust = pd.read_csv(ROBUST_FILE)

# Robust candidate IDs
ids = robust["candidate_id"].tolist()

qa = df[df["candidate_id"].isin(ids)].copy()

columns = [
    "candidate_id",
    "borough",
    "latitude",
    "longitude",
    "rent_monthly_sqft_2024",
    "rent_monthly_sqft_2024_model",
    "rent_source",
    "rent_estimation_distance_m",
    "rent_score",
]

qa = qa[columns].sort_values(
    ["rent_score", "candidate_id"]
)

print("\nROBUST CANDIDATE — RENT QA")
print("=" * 110)

print(qa.to_string(index=False))

print("\nRENT SOURCE SUMMARY")
print("=" * 70)

print(
    qa["rent_source"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nMODEL RENT SUMMARY")
print("=" * 70)

print(
    qa["rent_monthly_sqft_2024_model"]
    .describe()
    .to_string()
)

print("\nESTIMATION DISTANCE — ESTIMATED ONLY")
print("=" * 70)

estimated = qa[
    qa["rent_source"].astype(str).str.lower().str.contains("estim")
]

if len(estimated) > 0:
    print(
        estimated["rent_estimation_distance_m"]
        .describe()
        .to_string()
    )
else:
    print("No estimated rents found.")

# -------------------------------------------------
# Inspect raw rent / tract information
# for the three $1 direct-rent candidates
# -------------------------------------------------

CHECK_IDS = ["C0398", "C0902", "C0906"]

print("\n$1 DIRECT RENT — RAW / TRACT QA")
print("=" * 100)

qa_columns = [
    col for col in df.columns
    if (
        "rent" in col.lower()
        or "tract" in col.lower()
        or "boro" in col.lower()
        or "geoid" in col.lower()
    )
]

display_columns = ["candidate_id", "latitude", "longitude"]

for col in qa_columns:
    if col not in display_columns:
        display_columns.append(col)

print(
    df[df["candidate_id"].isin(CHECK_IDS)][display_columns]
    .to_string(index=False)
)