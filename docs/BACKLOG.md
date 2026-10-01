# Backlog and Sprint Plan

Copy each story onto a card in Trello or Jira. Set up four columns: **Backlog → In Progress → Testing → Done**. Move cards as you work, and take a screenshot of the board at the start and end of each day for the README. Those screenshots are your evidence of Agile work.

**Sprint 1 = Saturday · Sprint 2 = Sunday · Sprint 3 = the following week**

## Sprint 1: Data and classification (Saturday)

| ID | User story | Acceptance criteria | Pts |
|---|---|---|---|
| US-1 | As a PM, I want reviews for a specific app pulled automatically so I don't have to copy them by hand. | Script takes an app ID and saves ≥ 500 reviews to CSV with text, rating, date, and version. No reviewer names are saved. | 2 |
| US-2 | As a PM, I want each review tagged with a theme so I can see what users talk about most. | Every review gets exactly one theme from the taxonomy. Output is valid JSON. | 5 |
| US-3 | As a PM, I want each review's sentiment so I can tell which themes are pain points. | Every review gets positive, neutral, or negative. | 1 |
| US-4 | As a PM, I want feature requests separated from complaints so I can see what users are asking for. | Each review is flagged true or false; requests include a one-line summary. | 2 |
| US-5 | As the builder, I want a hand-labeled test set so I can prove the tool is accurate. | 100 reviews labeled using the labeling guide, saved as `labels.csv`. | 3 |

## Sprint 2: Evaluation and dashboard (Sunday)

| ID | User story | Acceptance criteria | Pts |
|---|---|---|---|
| US-6 | As the builder, I want accuracy measured against my labels so I know whether the tool can be trusted. | Script reports theme and sentiment agreement %, feature-request F1, and a confusion matrix. | 3 |
| US-7 | As the builder, I want to fix the most common errors so the tool meets its targets. | At least one prompt revision is made and re-scored; before and after numbers are recorded. | 3 |
| US-8 | As a PM, I want a dashboard of themes and sentiment so I can understand results in under 2 minutes. | Streamlit app shows a theme bar chart, sentiment split, and 3 example quotes per theme. | 5 |
| US-9 | As a PM, I want a ranked list of feature requests so I can prioritize the roadmap. | Requests are grouped and sorted by how often they appear. | 2 |
| US-10 | As a PM, I want to compare my app with a competitor so I can spot gaps. | Side-by-side theme breakdown for two apps. *(Cut this first if behind.)* | 3 |
| US-11 | As a recruiter, I want a clear README so I can understand the project quickly. | README has the problem, approach, accuracy results, screenshots, and limitations. | 2 |

## Sprint 3: Validation (following week)

| ID | User story | Acceptance criteria | Pts |
|---|---|---|---|
| US-12 | As the builder, I want feedback from real users so I know whether the tool is useful. | 3–5 testers each complete the 2-minute task; their ratings and comments are recorded. | 3 |
| US-13 | As the builder, I want to act on that feedback so v1.1 is better. | Top 2 issues are fixed or logged as future work. | 2 |
| US-14 | As a PM, I want to find themes the taxonomy missed. | Second LLM pass over "Other" reviews suggests new themes. *(Optional.)* | 3 |

## Retro notes (fill in at the end of each sprint)

- **What went well:**
- **What didn't:**
- **What I'd change next sprint:**
- **Points planned vs. completed:**
