from pathlib import Path
import pandas as pd
import folium

INPUT_FILE = Path("data/study_area_candidate_grid.csv")
OUTPUT_FILE = Path("outputs/maps/study_area_candidate_grid.html")


def main():

    df = pd.read_csv(INPUT_FILE)

    m = folium.Map(
        location=[40.72, -73.96],
        zoom_start=10,
        tiles="CartoDB positron"
    )

    for _, row in df.iterrows():

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=2,
            weight=1,
            fill=True,
            fill_opacity=0.65,
            tooltip=(
                f'{row["candidate_id"]} | '
                f'{row["borough"]}'
            )
        ).add_to(m)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    m.save(OUTPUT_FILE)

    print("Candidate grid map created")
    print("Candidates:", len(df))
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
