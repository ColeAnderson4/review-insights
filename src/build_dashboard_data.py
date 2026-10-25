"""Build the dataset the Streamlit dashboard reads.

Joins the final LLM classifications to the scraped review text, rating, and date,
and saves the result to data/dashboard_reviews.csv.
"""

import glob

import pandas as pd

FINAL_PROMPT_VERSION = "4af6be35"
EXPECTED_REVIEWS = 2000

# 1. Load the classifications and keep only the final prompt's run.
classified = pd.read_csv("data/raw/classified_raw.csv")
classified = classified[classified["prompt_version"] == FINAL_PROMPT_VERSION]

# Each review should have been classified exactly once by the final prompt.
assert len(classified) == EXPECTED_REVIEWS, f"Expected {EXPECTED_REVIEWS} rows, got {len(classified)}"
assert classified["review_id"].nunique() == EXPECTED_REVIEWS, "Duplicate review_ids in final run"

# 2. Load the scraped reviews (one file per app) and stack them into one table.
scraped_files = glob.glob("data/raw/*_reviews.csv")
scraped = pd.concat([pd.read_csv(path) for path in scraped_files], ignore_index=True)

# Keep only what the dashboard needs. "app" is left out because the classified
# data already has it; keeping both would give us app_x and app_y after the join.
scraped = scraped[["review_id", "text", "rating", "date"]]

# 3. Left join: keep every classified review and attach its scraped details.
# indicator=True adds a "_merge" column saying whether each row found a match.
dashboard = classified.merge(scraped, on="review_id", how="left", indicator=True)

# 4. Check for classified reviews with no scraped match, then drop "_merge".
missing = (dashboard["_merge"] == "left_only").sum()
print(f"Unmatched reviews: {missing}")
if missing > 0:
    raise ValueError(f"{missing} classified reviews have no scraped match")
dashboard = dashboard.drop(columns=["_merge"])

# 5. Save the result for the dashboard.
dashboard.to_csv("data/dashboard_reviews.csv", index=False)
print(f"Saved {len(dashboard)} rows to data/dashboard_reviews.csv")
