import pandas as pd

INPUT_FILE = "data/study_area_universities_2024.csv"
OUTPUT_FILE = "data/study_area_campus_demand_2024.csv"

NYU_UNITID = 193900
COLUMBIA_UNITID = 190150

df = pd.read_csv(INPUT_FILE)

rows = []

for _, row in df.iterrows():

    # -------------------------------------------------
    # NYU: split into two NYC campus demand centers
    # -------------------------------------------------
    if row["UNITID"] == NYU_UNITID:

        total = row["physical_student_potential"]

        brooklyn_share = 0.1323
        manhattan_share = 1.0 - brooklyn_share

        # Washington Square
        manhattan = row.copy()
        manhattan["INSTNM"] = "New York University - Washington Square"
        manhattan["borough"] = "Manhattan"
        manhattan["physical_student_potential"] = total * manhattan_share
        manhattan["campus_allocation"] = "estimated_split"
        rows.append(manhattan)

        # Downtown Brooklyn / MetroTech
        brooklyn = row.copy()
        brooklyn["INSTNM"] = "New York University - Downtown Brooklyn"
        brooklyn["borough"] = "Brooklyn"
        brooklyn["physical_student_potential"] = total * brooklyn_share

        # Approximate campus demand center:
        # NYU Tandon / MetroTech
        brooklyn["LATITUDE"] = 40.6943
        brooklyn["LONGITUD"] = -73.9866
        brooklyn["campus_allocation"] = "estimated_split"
        rows.append(brooklyn)
        # -------------------------------------------------
    # Columbia: split into two Manhattan demand centers
    # -------------------------------------------------
    elif row["UNITID"] == COLUMBIA_UNITID:

        total = row["physical_student_potential"]

        medical_share = 0.1275
        main_share = 1.0 - medical_share

        # Morningside / Manhattanville
        main = row.copy()
        main["INSTNM"] = "Columbia University - Morningside / Manhattanville"
        main["borough"] = "Manhattan"
        main["physical_student_potential"] = total * main_share
        main["campus_allocation"] = "estimated_split"
        rows.append(main)

        # Columbia University Irving Medical Center
        medical = row.copy()
        medical["INSTNM"] = "Columbia University - Medical Center"
        medical["borough"] = "Manhattan"

        # CUIMC / 168th Street
        medical["LATITUDE"] = 40.8421
        medical["LONGITUD"] = -73.9419

        medical["physical_student_potential"] = total * medical_share
        medical["campus_allocation"] = "estimated_split"
        rows.append(medical)
    else:
        normal = row.copy()
        normal["campus_allocation"] = "IPEDS"
        rows.append(normal)


campus_df = pd.DataFrame(rows)

campus_df.to_csv(OUTPUT_FILE, index=False)

print("Original institutions:", len(df))
print("Campus demand records:", len(campus_df))

print()
print("Original physical potential:",
      df["physical_student_potential"].sum())

print("Campus physical potential:",
      campus_df["physical_student_potential"].sum())

print()
print(
    campus_df[
        campus_df["UNITID"].isin([NYU_UNITID, COLUMBIA_UNITID])
    ][
        [
            "UNITID",
            "INSTNM",
            "borough",
            "LATITUDE",
            "LONGITUD",
            "physical_student_potential",
            "campus_allocation",
        ]
    ].to_string(index=False)
)