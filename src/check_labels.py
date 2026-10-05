"""Check data/labels.csv against the rules in docs/LABELING_GUIDE.md.

Read-only: this script never changes labels.csv. It prints every problem it
finds, then a summary of the labels.

Usage:
    python src/check_labels.py
"""

import sys
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
LABELS_PATH = Path("data/labels.csv")
APPS = ["ukg_pro", "workday"]
EXPECTED_ROWS = 100
MAX_SUMMARY_WORDS = 8

# Must match the theme table in docs/LABELING_GUIDE.md exactly
THEMES = [
    "login_auth",
    "timekeeping",
    "pay",
    "scheduling_pto",
    "performance",
    "ui_navigation",
    "notifications",
    "support",
    "positive_general",
    "negative_general",
    "other",
]
SENTIMENTS = ["positive", "neutral", "negative"]
FEATURE_REQUEST_VALUES = ["true", "false"]
REQUIRED_COLUMNS = ["theme", "sentiment", "is_feature_request"]


def load_labels():
    """Load labels.csv with every value as a plain string.

    dtype=str stops pandas from converting TRUE/FALSE to booleans, and
    keep_default_na=False keeps empty cells as "" instead of NaN, so
    "is this cell empty?" is a simple comparison.
    """
    return pd.read_csv(LABELS_PATH, dtype=str, keep_default_na=False)


def load_raw_reviews():
    """Load every app's cached reviews into one DataFrame."""
    frames = []
    for app_name in APPS:
        frames.append(pd.read_csv(RAW_DIR / f"{app_name}_reviews.csv", dtype=str))
    return pd.concat(frames)


def find_problems(labels, raw):
    """Return a list of problem messages. An empty list means the labels pass."""
    problems = []

    if len(labels) != EXPECTED_ROWS:
        problems.append(f"Expected {EXPECTED_ROWS} rows, found {len(labels)}")

    duplicate_ids = labels["review_id"][labels["review_id"].duplicated()]
    for review_id in duplicate_ids:
        problems.append(f"Duplicate review_id: {review_id}")

    raw_ids = set(raw["review_id"])

    for i, row in labels.iterrows():
        # i is the DataFrame index; +2 turns it into the spreadsheet row
        # number (1 for the header row, 1 because the index starts at 0)
        where = f"Row {i + 2} ({row['review_id'][:8]})"

        theme = row["theme"].strip()
        sentiment = row["sentiment"].strip().lower()
        is_request = row["is_feature_request"].strip().lower()
        summary = row["request_summary"].strip()

        if row["review_id"] not in raw_ids:
            problems.append(f"{where}: review_id not found in {RAW_DIR}/")

        for column in REQUIRED_COLUMNS:
            if row[column].strip() == "":
                problems.append(f"{where}: {column} is empty")

        # Themes must match exactly, including capitalization
        if theme != "" and row["theme"] not in THEMES:
            problems.append(f"{where}: unknown theme '{row['theme']}'")

        if sentiment != "" and sentiment not in SENTIMENTS:
            problems.append(f"{where}: unknown sentiment '{row['sentiment']}'")

        if is_request != "" and is_request not in FEATURE_REQUEST_VALUES:
            problems.append(f"{where}: is_feature_request must be true/false, got '{row['is_feature_request']}'")

        if is_request == "true" and summary == "":
            problems.append(f"{where}: feature request has no request_summary")

        if is_request == "false" and summary != "":
            problems.append(f"{where}: request_summary filled but is_feature_request is false")

        if len(summary.split()) > MAX_SUMMARY_WORDS:
            problems.append(f"{where}: request_summary is over {MAX_SUMMARY_WORDS} words")

    return problems


def print_summary(labels):
    """Print counts per theme, sentiment, and feature request."""
    sentiment = labels["sentiment"].str.strip().str.lower()
    is_request = labels["is_feature_request"].str.strip().str.lower()

    print("\nTheme counts:")
    # reindex lists every theme from the guide, including ones with 0 labels
    theme_counts = labels["theme"].value_counts().reindex(THEMES, fill_value=0)
    print(theme_counts.sort_values(ascending=False).to_string())

    print("\nSentiment counts:")
    print(sentiment.value_counts().to_string())

    print(f"\nFeature requests: {(is_request == 'true').sum()} of {len(labels)}")

    print("\nSentiment by app:")
    print(pd.crosstab(labels["app"], sentiment).to_string())


def main():
    labels = load_labels()
    raw = load_raw_reviews()

    problems = find_problems(labels, raw)
    if problems:
        print(f"Found {len(problems)} problem(s) in {LABELS_PATH}:")
        for problem in problems:
            print(f"  {problem}")
    else:
        print(f"{LABELS_PATH}: all checks passed.")

    print_summary(labels)

    # A non-zero exit code tells the shell (or a future test) that checks failed
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
