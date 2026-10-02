import json
import zipfile

import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import unary_union


# --------------------------------------------------
# Study area polygon
# --------------------------------------------------
with open("data/nyc_borough_boundaries.geojson") as f:
    geo = json.load(f)

polygons = [
    shape(feature["geometry"])
    for feature in geo["features"]
    if feature["properties"].get("boroname")
    in ["Manhattan", "Brooklyn"]
]

study_area = unary_union(polygons)


# --------------------------------------------------
# IPEDS institution directory
# --------------------------------------------------
with zipfile.ZipFile("data/HD2024.zip") as z:
    hd = pd.read_csv(
        z.open("hd2024.csv"),
        encoding="utf-8-sig",
    )

hd = hd[
    hd["COUNTYNM"].isin(
        ["New York County", "Kings County"]
    )
].copy()

hd["inside_study_area"] = hd.apply(
    lambda r: study_area.covers(
        Point(r["LONGITUD"], r["LATITUDE"])
    ),
    axis=1,
)

hd = hd[hd["inside_study_area"]].copy()

hd["borough"] = hd["COUNTYNM"].map({
    "New York County": "Manhattan",
    "Kings County": "Brooklyn",
})


# --------------------------------------------------
# IPEDS Fall 2024 enrollment
# --------------------------------------------------
with zipfile.ZipFile("data/EF2024A_DIST.zip") as z:
    ef = pd.read_csv(
        z.open("ef2024a_dist.csv")
    )

# Institution-level total
ef = ef[ef["EFDELEV"] == 1].copy()

ef["physical_student_potential"] = (
    ef["EFDETOT"] - ef["EFDEEXC"].fillna(0)
)


# --------------------------------------------------
# Join
# --------------------------------------------------
universities = hd.merge(
    ef[
        [
            "UNITID",
            "EFDETOT",
            "EFDEEXC",
            "EFDESOM",
            "EFDENON",
            "physical_student_potential",
        ]
    ],
    on="UNITID",
    how="inner",
)

universities = universities[
    [
        "UNITID",
        "INSTNM",
        "borough",
        "CITY",
        "LATITUDE",
        "LONGITUD",
        "EFDETOT",
        "EFDEEXC",
        "EFDESOM",
        "EFDENON",
        "physical_student_potential",
    ]
].copy()

universities = universities.sort_values(
    "physical_student_potential",
    ascending=False,
)

universities.to_csv(
    "data/study_area_universities_2024.csv",
    index=False,
)


# --------------------------------------------------
# QA
# --------------------------------------------------
print("Institutions:", len(universities))

print("\nBY BOROUGH")
print(
    universities.groupby("borough")
    .agg(
        institutions=("UNITID", "count"),
        total_enrollment=("EFDETOT", "sum"),
        exclusively_online=("EFDEEXC", "sum"),
        physical_student_potential=(
            "physical_student_potential",
            "sum",
        ),
    )
)

print("\nTOP 15")
print(
    universities[
        [
            "INSTNM",
            "borough",
            "EFDETOT",
            "EFDEEXC",
            "physical_student_potential",
        ]
    ]
    .head(15)
    .to_string(index=False)
)

print(
    "\nSaved: data/study_area_universities_2024.csv"
)
