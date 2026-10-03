"""Scrape the newest Google Play reviews for each app and cache them as CSVs.

Usage:
    python src/scrape.py                 # scrape every app in APPS (skips cached ones)
    python src/scrape.py --app workday   # scrape one app
    python src/scrape.py --force         # re-scrape even if the CSV already exists
"""

import argparse
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

# Short name (used in filenames and the "app" column) -> Google Play package ID
APPS = {
    "ukg_pro": "com.ukg.oneapp",
    "workday": "com.workday.workdroidapp",
}

RAW_DIR = Path("data/raw")
TARGET_REVIEWS = 1000
BATCH_SIZE = 100
SECONDS_BETWEEN_REQUESTS = 1


def fetch_reviews(app_id, target=TARGET_REVIEWS):
    """Fetch up to `target` of the newest English reviews for one app.

    Google Play returns reviews in pages, so we keep asking for the next page
    using the continuation token until we have enough or run out.
    Returns a list of raw review dicts exactly as google-play-scraper gives them.
    """
    all_reviews = []
    token = None

    while len(all_reviews) < target:
        batch, token = reviews(
            app_id,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=BATCH_SIZE,
            continuation_token=token,
        )

        if len(batch) == 0:
            print("  No more reviews available.")
            break

        all_reviews.extend(batch)
        print(f"  Fetched {len(all_reviews)} reviews so far...")

        if token is None:
            break

        time.sleep(SECONDS_BETWEEN_REQUESTS)

    # The last batch can push us past the target, so trim the extras
    return all_reviews[:target]


def clean_reviews(raw, app_name):
    """Turn raw review dicts into a DataFrame with only the columns we keep.

    Input:
        raw: list of dicts from fetch_reviews(). Each dict has keys like
             "reviewId", "userName", "userImage", "content", "score",
             "thumbsUpCount", "at", "appVersion", and a few others.
        app_name: short name from APPS, e.g. "ukg_pro".

    Output:
        A pandas DataFrame with exactly these columns, in this order:
            review_id    <- reviewId
            app          <- app_name (the same value on every row)
            text         <- content
            rating       <- score
            thumbs_up    <- thumbsUpCount
            date         <- at
            app_version  <- appVersion (can be None; that's fine)

    Rules:
        - Build the rows from a whitelist of the keys above. Never copy
          userName, userImage, or any other key.
        - Drop duplicate review_id rows.
    """
    if not raw:
        raise ValueError(f"No reviews to clean for {app_name}. Check the app ID or try again later.")
    df = pd.DataFrame(raw)
    
    #1 Keep only the whitelisted keys
    keep = ["reviewId", "content", "score", "thumbsUpCount", "at", "appVersion"]
    
    #2 Rename to our column names
    df = df[keep]
    df = df.rename(columns={
        "reviewId": "review_id",
        "content": "text",
        "score": "rating",
        "thumbsUpCount": "thumbs_up",
        "at": "date",
        "appVersion": "app_version",
    })
    # 3. Add the app column
    df["app"] = app_name

    # 4. Remove duplicate reviews
    df = df.drop_duplicates(subset=["review_id"])

    # 5. Put columns in the order the docstring requires
    df = df[["review_id", "app", "text", "rating", "thumbs_up", "date", "app_version"]]

    return df


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Play reviews.")
    parser.add_argument(
        "--app",
        choices=list(APPS.keys()),
        help="Scrape only this app (default: all apps).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-scrape even if a cached CSV already exists.",
    )
    args = parser.parse_args()

    if args.app:
        app_names = [args.app]
    else:
        app_names = list(APPS.keys())

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for app_name in app_names:
        out_path = RAW_DIR / f"{app_name}_reviews.csv"

        if out_path.exists() and not args.force:
            print(f"{app_name}: cached at {out_path}, skipping (use --force to re-scrape).")
            continue

        print(f"{app_name}: scraping {APPS[app_name]}...")
        raw = fetch_reviews(APPS[app_name])
        df = clean_reviews(raw, app_name)
        df.to_csv(out_path, index=False)
        print(f"{app_name}: saved {len(df)} reviews to {out_path}")


if __name__ == "__main__":
    main()
