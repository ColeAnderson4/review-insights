# PRD: App Review Insights Tool

**Author:** Cole Anderson · **Status:** Draft v1 · **Last updated:** Oct 2026

## 1. Problem

Product managers at HR-software companies get thousands of app-store reviews, but reading them by hand is slow and inconsistent. As a result, they make prioritization decisions based on a handful of reviews they remember instead of on the full picture.

**Target user:** A product manager responsible for a mobile workforce app (e.g., UKG Pro).

**User need:** "Tell me what users are most frustrated about, how widespread it is, and what they're asking for, without making me read 2,000 reviews."

## 2. Goals and non-goals

**Goals (v1)**
- Turn a set of public Google Play reviews into ranked themes with sentiment and example quotes.
- Separate feature requests from complaints, then rank the requests.
- Compare two apps side by side (UKG Pro vs. a competitor).
- Prove the output is accurate by checking it against a hand-labeled test set.

**Non-goals (v1)**
- Apple App Store reviews (scraping is unreliable)
- Live or scheduled data refreshes
- Responding to reviews, or any automated action
- User accounts, logins, or hosting at scale

## 3. Hypothesis

Login and authentication problems are among the top 3 negative themes in UKG Pro reviews. This would independently validate my earlier UKG clock-in UX case study.

## 4. How it works

1. **Collect:** Pull the most recent ~1,000 reviews for an app using `google-play-scraper`, keeping review text, star rating, date, and app version.
2. **Classify:** Send reviews in batches to an LLM. For each review it returns JSON with:
   - `theme` (one value from the fixed taxonomy in the labeling guide)
   - `sentiment` (positive / neutral / negative)
   - `is_feature_request` (true / false)
   - `request_summary` (short summary, only if it is a feature request)
3. **Discover:** Run a second pass over reviews tagged "Other" to suggest new themes the taxonomy missed.
4. **Aggregate:** Count reviews by theme and sentiment, and rank feature requests by how often they come up.
5. **Display:** Show everything in a Streamlit dashboard with charts, filters, and real example quotes for each theme.

## 5. Features

| Priority | Feature |
|---|---|
| P0 | Scrape reviews for a given app ID |
| P0 | LLM classification into theme, sentiment, and feature request, returned as structured JSON |
| P0 | Accuracy evaluation against 100 hand-labeled reviews |
| P0 | Dashboard: theme breakdown, sentiment by theme, example quotes |
| P1 | Ranked feature-request list |
| P1 | Two-app competitor comparison |
| P2 | Emerging-theme discovery from "Other" |
| P2 | Theme trends over time / by app version |

## 6. Success metrics

**Model quality** (measured against my 100 hand-labeled reviews)

| Metric | Target |
|---|---|
| Theme agreement | ≥ 80% |
| Sentiment agreement | ≥ 85% |
| Feature-request detection (F1) | ≥ 0.75 |
| Malformed JSON responses | < 2% |

**Product value** (measured with 3–5 testers)
- Each tester can name the top problem and the top feature request within 2 minutes of opening the dashboard.
- Testers rate usefulness ≥ 4 out of 5.

## 7. Responsible AI and data considerations

- **Grounding:** Every theme must link to real review quotes so users can verify the tool's claims.
- **Privacy:** Reviewer names and profile images are dropped at collection. Only review text, rating, date, and version are stored. The raw scraped data is not committed to the public GitHub repo.
- **Known limitations:** The documentation will state that reviews over-represent angry users, that sarcasm hurts sentiment accuracy, and that results describe reviewers rather than all users.
- **Human in the loop:** The tool supports PM judgment; it does not make the prioritization decision.

## 8. Tech stack

Python · `google-play-scraper` · Anthropic or OpenAI API · Pandas · Streamlit · scikit-learn (evaluation metrics)

## 9. Risks

| Risk | Mitigation |
|---|---|
| Scraper breaks or gets rate-limited | Cache reviews to a local CSV after the first pull |
| LLM returns malformed JSON | Validate every response; retry once; log failures |
| Themes too vague to act on | Use a fixed taxonomy for v1 instead of free-form themes |
| API cost | Small batches; ~1,000 reviews should cost under $5 |
| Running out of weekend time | Cut P1 and P2 features first; never cut the evaluation |

## 10. Open questions

- Is UKG Pro the best primary app, or does it have too few recent reviews? (Check the review count before starting.)
- Which competitor should it be compared against: ADP Mobile or Workday?
