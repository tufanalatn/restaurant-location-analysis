import pandas as pd
import shapefile
from shapely.geometry import shape

WAC_FILE = "data/ny_wac_S000_JT00_2023.csv.gz"
BLOCK_DIR = "data/blocks_2020"
OUTPUT_FILE = "data/study_area_office_jobs_2023.csv"

OFFICE_COLS = [
    "CNS09",  # Information
    "CNS10",  # Finance & Insurance
    "CNS11",  # Real Estate
    "CNS12",  # Professional / Scientific / Technical
    "CNS13",  # Management of Companies
    "CNS14",  # Administrative & Support
]

COUNTIES = {
    "36047": "Brooklyn",
    "36061": "Manhattan",
}

# -------------------------------------------------
# Load LODES workplace data
# -------------------------------------------------

wac = pd.read_csv(
    WAC_FILE,
    dtype={"w_geocode": str},
)

wac["county"] = wac["w_geocode"].str[:5]

wac = wac[
    wac["county"].isin(COUNTIES)
].copy()

wac["borough"] = wac["county"].map(COUNTIES)

wac["office_jobs"] = wac[OFFICE_COLS].sum(axis=1)

# -------------------------------------------------
# Load Census Block geometries
# and create one representative point per block
# -------------------------------------------------

block_points = []

for county, borough in COUNTIES.items():

    shp_file = (
        f"{BLOCK_DIR}/"
        f"tl_2020_{county}_tabblock20.shp"
    )

    sf = shapefile.Reader(shp_file)

    fields = [f[0] for f in sf.fields[1:]]
    geoid_index = fields.index("GEOID20")

    for sr in sf.iterShapeRecords():

        geoid = str(sr.record[geoid_index])

        geom = shape(sr.shape.__geo_interface__)

        point = geom.representative_point()

        block_points.append(
            {
                "w_geocode": geoid,
                "latitude": point.y,
                "longitude": point.x,
            }
        )

blocks = pd.DataFrame(block_points)

# -------------------------------------------------
# Join workplace jobs to block locations
# -------------------------------------------------

office = wac.merge(
    blocks,
    on="w_geocode",
    how="left",
    validate="one_to_one",
)

# Keep useful fields
office = office[
    [
        "w_geocode",
        "borough",
        "latitude",
        "longitude",
        "C000",
        "office_jobs",
        "CE03",
    ]
].rename(
    columns={
        "C000": "total_jobs",
        "CE03": "higher_earning_jobs",
    }
)

office.to_csv(
    OUTPUT_FILE,
    index=False,
)

# -------------------------------------------------
# QA
# -------------------------------------------------

print("Workplace blocks:", len(office))
print("Missing coordinates:",
      office["latitude"].isna().sum())

print("\nBy borough:")
print(
    office.groupby("borough").agg(
        blocks=("w_geocode", "count"),
        total_jobs=("total_jobs", "sum"),
        office_jobs=("office_jobs", "sum"),
        higher_earning_jobs=("higher_earning_jobs", "sum"),
    )
)

print("\nOffice jobs distribution:")
print(office["office_jobs"].describe())

print("\nTop 20 office blocks:")
print(
    office.nlargest(20, "office_jobs")[
        [
            "w_geocode",
            "borough",
            "latitude",
            "longitude",
            "total_jobs",
            "office_jobs",
            "higher_earning_jobs",
        ]
    ].to_string(index=False)
)

print("\nSaved:", OUTPUT_FILE)