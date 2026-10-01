from google_play_scraper import reviews, Sort

APPS = {
    "UKG Pro": "com.ukg.oneapp",
    "Workday": "com.workday.workdroidapp",
}

for name, app_id in APPS.items():
    results, _ = reviews(app_id, lang="en", country="us", sort=Sort.NEWEST, count=5)
    print(f"\n=== {name}: {len(results)} reviews ===")
    for r in results:
        print(f"{r['score']}★  {r['content'][:100]}")