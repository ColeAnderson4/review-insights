"""Build the dataset the Streamlit dashboard reads.

Joins the final LLM classifications to the scraped review text, rating, and date,
and saves the result to data/dashboard_reviews.csv.
"""

import glob

import pandas as pd

FINAL_PROMPT_VERSION = "4af6be35"
EXPECTED_REVIEWS = 2000

# classified_raw.csv holds every prompt version's run; keep only the final one.
classified = pd.read_csv("data/raw/classified_raw.csv")
classified = classified[classified["prompt_version"] == FINAL_PROMPT_VERSION]

# Each review should have been classified exactly once by the final prompt.
assert len(classified) == EXPECTED_REVIEWS, f"Expected {EXPECTED_REVIEWS} rows, got {len(classified)}"
assert classified["review_id"].nunique() == EXPECTED_REVIEWS, "Duplicate review_ids in final run"

scraped_files = glob.glob("data/raw/*_reviews.csv")
scraped = pd.concat([pd.read_csv(path) for path in scraped_files], ignore_index=True)

# "app" is left out because classified already has it (avoids app_x / app_y).
scraped = scraped[["review_id", "text", "rating", "date"]]

# indicator=True adds a "_merge" column, used below to catch unmatched reviews.
dashboard = classified.merge(scraped, on="review_id", how="left", indicator=True)

missing = (dashboard["_merge"] == "left_only").sum()
print(f"Unmatched reviews: {missing}")
if missing > 0:
    raise ValueError(f"{missing} classified reviews have no scraped match")
dashboard = dashboard.drop(columns=["_merge"])

dashboard.to_csv("data/dashboard_reviews.csv", index=False)
print(f"Saved {len(dashboard)} rows to data/dashboard_reviews.csv")
