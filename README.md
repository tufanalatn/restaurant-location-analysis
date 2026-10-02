# Restaurant Location Analysis — 2019 → 2026

## Overview

In 2019, as a final project for a Data Science course, I created a hypothetical business case:

> Where should an investor open a new Turkish restaurant in Manhattan?

The original analysis focused on areas with strong concentrations of business centers and universities, examined nearby venues within a 500-meter radius, and evaluated the presence of competing Turkish restaurants.

The 2019 analysis identified the **59th Street / Central Park area** as a promising location.

Seven years later, I revisited exactly the same business problem.

The objective was not simply to repeat the analysis with newer tools, but to examine how the problem itself could be modeled differently using open data, geospatial analytics, and supervised machine learning.

The 2026 study expands the geography to **Manhattan and Brooklyn** and evaluates **939 candidate locations** on an approximately 500-meter grid.

---

# 1. Business Question

The core question remains:

> Where is there sufficient customer demand for a Turkish restaurant, while avoiding excessive competition and occupancy cost?

This leads to three primary dimensions:

```text
DEMAND
  ↓
Turkish Competition
  ↓
Occupancy Cost
  ↓
LOCATION OPPORTUNITY
```

Demand itself is estimated from several observable signals.

---

# 2. Study Area

The 2026 study covers:

- Manhattan
- Brooklyn

A candidate grid with approximately 500-meter spacing was generated inside the borough boundaries.

Total candidate locations:

**939**

---

# 3. Data Sources

The project uses reproducible public/open datasets.

## Food & Social Activity

OpenStreetMap / Overpass data was used to collect:

- Restaurants
- Cafes
- Bars
- Fast-food locations

Total activity POIs:

**11,408**

These locations provide a measure of the existing food and social commercial ecosystem around each candidate.

---

## Universities

Fall 2024 enrollment data was obtained from the U.S. Department of Education / NCES IPEDS datasets.

After geographic filtering:

- 121 institutions
- 123 campus demand points after selected campus splits
- 321,547 non-exclusively-online student enrollment potential

A distance-decay model was used to estimate university-generated demand around each candidate location.

The student population variable is treated as a **physical student potential proxy**, not as daily campus attendance.

---

## Office Employment

Workplace employment data comes from:

**U.S. Census LEHD / LODES WAC 2023**

Office-oriented employment sectors include:

- Information
- Finance & Insurance
- Real Estate
- Professional / Scientific / Technical Services
- Management of Companies
- Administrative & Support Services

Total office-oriented jobs in the study area:

**1,401,624**

Office demand was modeled using workplace block locations and distance decay.

---

## Subway Accessibility

Official MTA station complex data was used.

Study-area subway complexes:

**277**

Accessibility combines:

- Number of subway complexes within 500 meters
- Distance to the nearest subway complex

---

## Turkish Restaurant Competition

OpenStreetMap restaurants explicitly tagged with Turkish cuisine were used as the reproducible competition dataset.

Study-area Turkish restaurants:

**36**

Competition is modeled continuously using distance decay rather than a simple yes/no 500-meter threshold.

Higher values indicate stronger nearby Turkish restaurant competition.

---

## Storefront Rent

NYC storefront statistics were used as a relative occupancy-cost signal.

The model uses 2024 census-tract storefront rent statistics.

Where direct tract data was unavailable, nearby same-borough tract information was used to estimate missing values.

Important:

> Rent values in this project should be interpreted as relative location-cost signals, not as current asking rents for a specific storefront.

---

## Pedestrian Counts

NYC DOT pedestrian count observations were used to calibrate the demand model.

For restaurant relevance, the target variable uses the average of:

- May 2026 midday pedestrian count
- May 2026 PM pedestrian count

There were **61 observations with valid target values** available for model training and validation.

---

# 4. Demand Feature Engineering

Four major signals were created for pedestrian demand estimation:

```text
Food / Social Activity
        +
University Demand
        +
Office Demand
        +
Subway Accessibility
        ↓
Predicted Pedestrian Demand
```

### Food Activity

Counts restaurants, cafes, bars, and fast-food locations within 500 meters.

### University Demand

Uses:

```text
sqrt(student potential) × distance decay
```

A 750-meter half-life is used.

### Office Demand

Uses:

```text
sqrt(office jobs) × distance decay
```

A 750-meter half-life is also used.

The square-root transformation prevents extremely large institutions or employment blocks from dominating the model.

### Subway Accessibility

Combines nearby station-complex count with walking-distance proximity.

---

# 5. Supervised Machine Learning

Instead of manually assigning weights to the four demand variables, the 2026 model uses actual NYC DOT pedestrian observations.

The predictive model is:

**Ridge Regression**

with:

**alpha = 15**

The target is modeled as:

```text
log(1 + pedestrian count)
```

The model uses:

```text
Activity
University Demand
Office Demand
Subway Accessibility
Borough
        ↓
Ridge Regression
        ↓
Predicted Pedestrian Demand
```

This is a **supervised machine-learning regression model**.

It is not a generative-AI or LLM model.

Generative AI was used during the development workflow as a coding and analytical assistant, but not as the scoring engine.

---

# 6. Model Validation

Random cross-validation initially produced encouraging results, but geographic data can suffer from spatial leakage.

For that reason, the final evaluation uses **borough-aware spatial cross-validation**.

With Ridge alpha = 15:

| Metric | Result |
|---|---:|
| MAE | 1,655 |
| RMSE | 2,563 |
| R² | 0.432 |
| Spearman Rank Correlation | **0.735** |

For this project, Spearman correlation is particularly important because the primary objective is not to predict an exact pedestrian count.

The objective is to **rank candidate locations relative to one another**.

The pedestrian model should therefore be interpreted as a relative demand model rather than a precise pedestrian forecasting system.

---

# 7. Opportunity Model

The machine-learning model produces a normalized:

**Pedestrian Demand Score**

This is then combined with two commercial dimensions:

```text
Pedestrian Demand
        +
Low Turkish Competition
        +
Low Occupancy Cost
        ↓
Location Opportunity
```

Activity, university, office, and subway variables are **not added again** to the final opportunity score because they are already embedded in the pedestrian-demand model.

This avoids double counting.

---

# 8. Sensitivity Analysis

There is no objectively correct business weight for demand, competition, and cost.

Instead of selecting one arbitrary weighting scheme, three scenarios were tested.

### Balanced

```text
Demand       33.3%
Competition  33.3%
Rent         33.3%
```

### Demand-Led

```text
Demand       50%
Competition  25%
Rent         25%
```

### Commercial

```text
Demand       40%
Competition  20%
Rent         40%
```

The three scenarios produced strongly overlapping results.

**16 candidate locations appeared in the Top 20 under all three scenarios.**

These are treated as the project's:

**Robust Candidates**

---

# 9. Opportunity Zones

The 16 robust candidate grid cells were geographically grouped using DBSCAN with a 750-meter neighborhood distance.

This produced:

**9 technical opportunity zones**

The zone IDs are technical cluster identifiers, not a ranking of neighborhoods.

Broad reporting areas include:

- Brownsville / East New York
- East New York / Cypress Hills
- East Harlem
- Morningside Heights / Manhattanville
- Upper East Harlem / Harlem River

The final analysis therefore moves from individual grid cells toward broader geographic opportunity areas.

---

# 10. 2019 vs 2026

The original 2019 project identified the **59th Street / Central Park area**.

Because the original study did not preserve an exact candidate coordinate, the 2026 comparison evaluates the surrounding 59th Street / Central Park South area rather than inventing a precise historical point.

Nine 2026 grid cells fall inside the comparison area.

Their average scores are:

| Dimension | Mean Score |
|---|---:|
| Pedestrian Demand | **0.958** |
| Turkish Competition | **0.941** |
| Rent Cost | **0.961** |

This produces an interesting result.

The 2019 location still has exceptionally strong estimated demand.

However, it also has very high Turkish restaurant competition and very high relative occupancy cost.

Under the 2026 opportunity scenarios, the best candidate inside the historical area ranks:

| Scenario | Best Rank |
|---|---:|
| Balanced | 803 / 939 |
| Demand-Led | 403 / 939 |
| Commercial | 656 / 939 |

The interpretation is therefore not that the 2019 model was wrong.

Instead:

> **The 2019 model successfully identified demand.  
> The 2026 model shows that high demand alone does not necessarily imply high commercial opportunity.**

---

# 11. Final Map

The final interactive map contains:

- 2026 robust candidates
- 2026 opportunity-zone centers
- 2019 59th Street comparison area

Open:

```text
outputs/maps/final_opportunity_map.html
```

The map visually demonstrates how the opportunity geography changes when competition and occupancy cost are considered alongside demand.

---

# 12. Key Methodological Evolution

### 2019

```text
Business Centers
      +
Universities
      ↓
Nearby Venues
      ↓
Turkish Competition
      ↓
Candidate Location
```

### 2026

```text
Food / Social Activity
University Demand
Office Demand
Subway Accessibility
        ↓
Supervised ML
        ↓
Pedestrian Demand
        +
Turkish Competition
        +
Occupancy Cost
        ↓
Sensitivity Analysis
        ↓
Robust Opportunity Zones
```

The most important change is therefore not simply the amount of data.

It is the transition from:

> **Where are people likely to be?**

to:

> **Where is there evidence of demand, acceptable competition, and commercially reasonable occupancy cost?**

---

# 13. Limitations

This is a location-intelligence demonstration, not a restaurant investment recommendation.

Important limitations include:

- Pedestrian observations are geographically sparse.
- DOT pedestrian count locations are not a random sample of New York City.
- Predicted pedestrian demand should be interpreted relatively rather than as an exact foot-traffic forecast.
- OpenStreetMap cuisine tagging is incomplete.
- Storefront rent statistics are tract-level historical indicators rather than current storefront asking rents.
- Restaurant concept, menu, pricing, delivery demand, demographics, tourism, zoning, storefront availability, frontage, visibility, and local street conditions are not modeled.
- A final investment decision would require field validation and current commercial real-estate data.

---

# 14. Technology

The project was developed in Python.

Main technologies include:

- Python 3.12
- pandas
- NumPy
- scikit-learn
- Shapely
- pyshp
- Folium
- OpenStreetMap / Overpass
- NYC Open Data
- NCES IPEDS
- U.S. Census LEHD / LODES
- MTA Open Data

---

# 15. Project Structure

```text
restaurant-location-analysis/
│
├── data/
│   ├── final_opportunity_zones.csv
│   ├── opportunity_zone_candidates.csv
│   └── study_area_candidate_features.csv
│
├── outputs/
│   └── maps/
│       └── final_opportunity_map.html
│
├── src/
│   ├── data collection
│   ├── feature engineering
│   ├── model validation
│   ├── pedestrian demand prediction
│   ├── sensitivity analysis
│   └── opportunity-zone generation
│
├── README.md
└── requirements.txt
```

---

# Conclusion

Seven years later, the business question is still recognizable.

The methodology is not.

The 2019 project used proximity, venue density, and competition to identify a promising restaurant location.

The 2026 version combines open geospatial data, population generators, transportation accessibility, observed pedestrian counts, supervised machine learning, commercial cost signals, and sensitivity analysis.

And perhaps the most useful finding is simple:

> **A place can have extraordinary demand and still not be the strongest commercial opportunity.**