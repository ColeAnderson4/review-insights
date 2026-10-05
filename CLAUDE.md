# CLAUDE.md

## Project
App Review Insights Tool: it scrapes Google Play reviews, classifies them with an LLM, measures accuracy against hand labels, and shows the results in a Streamlit dashboard. Specs are in `docs/`. Read `docs/PRD.md` and `docs/LABELING_GUIDE.md` before writing any code.

## About me
I'm a student building this as a portfolio project, and **I want to learn, not just get working code.** I know Python (Pandas, scikit-learn, statsmodels) and SQL. I'm new to calling LLM APIs, Streamlit, and Claude Code itself.

## How to work with me
- Before writing code, explain your plan in a few sentences and wait for my OK.
- Keep changes small: one file or one function at a time.
- After writing code, explain the key lines and any library I haven't used before.
- When something breaks, explain the cause before you fix it.
- Ask me to write simple pieces myself sometimes, and review my version instead of replacing it.
- I'll need to explain this code in interviews, so avoid clever one-liners.

## Rules
- Python 3.10+. Dependencies go in `requirements.txt`.
- The API key lives in `.env` and is loaded with `python-dotenv`. Never print or commit it.
- Never save reviewer names or profile images.
- `data/raw/` is git-ignored. Cache scraped reviews there so we don't re-scrape.
- LLM outputs must be validated JSON. Retry once on failure and log anything that still fails.
- Theme names must exactly match `docs/LABELING_GUIDE.md`.
- Only change data/labels.csv when I approve it, and log every change in docs/label_corrections.md.
- Suggest a git commit message after each completed user story (e.g., "US-1: scrape reviews to CSV").
