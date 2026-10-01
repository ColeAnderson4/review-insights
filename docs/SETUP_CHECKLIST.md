# Pre-Weekend Setup Checklist

Finish this before Saturday morning so the whole weekend goes to building. It should take about 45 minutes.

## Accounts and keys
- [ ] Create an API key at console.anthropic.com or platform.openai.com and add **$5 of credit**.
- [ ] Keep the key in a `.env` file. **Never commit it to GitHub.**
- [ ] Create a free Trello or Jira board and add the stories from `BACKLOG.md`.

## Pick the apps
- [ ] Find **UKG Pro** on the Google Play website. Copy its app ID from the URL (the part after `id=`). Check that it has at least a few hundred reviews.
- [ ] Do the same for one competitor: **ADP Mobile Solutions** or **Workday**.
- [ ] Write both app IDs into the PRD's open questions section.

## Repo
- [ ] Create a GitHub repo, for example `app-review-insights`.
- [ ] Add a `.gitignore` containing at least:
  ```
  .env
  data/raw/
  __pycache__/
  .venv/
  ```
- [ ] Copy the `docs/` folder into the repo.

## Python environment
- [ ] Install Python 3.10 or newer.
- [ ] Create a virtual environment and install the packages:
  ```bash
  python -m venv .venv
  source .venv/bin/activate      # Windows: .venv\Scripts\activate
  pip install -r requirements.txt
  ```
- [ ] Run this quick test. If it prints review text, you're ready:
  ```python
  from google_play_scraper import reviews
  r, _ = reviews("PASTE_APP_ID_HERE", count=5)
  print([x["content"] for x in r])
  ```

## Suggested folder structure
```
app-review-insights/
├── docs/            PRD, backlog, labeling guide
├── data/raw/        scraped CSVs (git-ignored)
├── data/labels.csv  your 100 hand labels
├── src/
│   ├── scrape.py
│   ├── classify.py
│   └── evaluate.py
├── app.py           Streamlit dashboard
├── requirements.txt
└── README.md
```
