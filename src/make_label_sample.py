"""Build a blank labeling sheet of 100 random reviews (50 per app).

The output, data/labels.csv, is where hand labels go. The script refuses to
overwrite it so a re-run can never wipe out labeling work.

Usage:
    python src/make_label_sample.py
"""

import sys
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
LABELS_PATH = Path("data/labels.csv")
APPS = ["ukg_pro", "workday"]
REVIEWS_PER_APP = 50
RANDOM_STATE = 42

# rating is left out on purpose: sentiment should be labeled from the text,
# not the stars. It can be joined back from data/raw/ by review_id later.
KEEP_COLUMNS = ["review_id", "app", "text"]
LABEL_COLUMNS = ["theme", "sentiment", "is_feature_request", "request_summary", "notes"]


def sample_app(app_name):
    """Load one app's cached reviews and return a random sample of REVIEWS_PER_APP rows."""
    path = RAW_DIR / f"{app_name}_reviews.csv"
    df = pd.read_csv(path)
    return df.sample(n=REVIEWS_PER_APP, random_state=RANDOM_STATE)


def main():
    # --- Safety check ---
    # If LABELS_PATH already exists, print a message saying so and stop the
    # script without writing anything. Hint: Path.exists() and sys.exit().
    if LABELS_PATH.exists():
        print(f"{LABELS_PATH} already exists. Refusing to overwrite your hand labels. Delete or rename it first if you really want a new sample.")
        sys.exit(1)
    # 1. Sample each app separately so we get exactly 50 of each
    samples = []
    for app_name in APPS:
        samples.append(sample_app(app_name))

    # 2. Stack the samples, then shuffle so the apps are mixed together.
    #    frac=1 means "sample 100% of the rows", which just reorders them.
    df = pd.concat(samples)
    df = df.sample(frac=1, random_state=RANDOM_STATE)
    df = df.reset_index(drop=True)

    # 3. Keep only the columns needed for labeling and add empty label columns
    df = df[KEEP_COLUMNS]
    for column in LABEL_COLUMNS:
        df[column] = ""

    # 4. Save and summarize
    df.to_csv(LABELS_PATH, index=False)
    counts = df["app"].value_counts()
    print(f"Wrote {len(df)} rows to {LABELS_PATH}:")
    for app_name in APPS:
        print(f"  {app_name}: {counts[app_name]}")


if __name__ == "__main__":
    main()
