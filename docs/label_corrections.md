# Label Corrections

Changes made to `data/labels.csv` after reviewing the disagreements from the first LLM evaluation run (US-7).

- **Date:** 2026-10-04
- **Run reviewed:** model `claude-sonnet-5-5`, prompt version `1a46f99f` (theme agreement 0.85, sentiment agreement 0.95)
- **Original labels:** commit `2e5be67` ("US-5: hand-label 100-review test set"). Retrieve them with `git show 2e5be67:data/labels.csv`.

## Why this matters for the accuracy numbers

`LABELING_GUIDE.md` requires labeling before seeing the LLM's output. These corrections break that rule on purpose, so they need to be reported honestly:

- Only the 19 reviews where the LLM **disagreed** with me were re-checked. If the LLM and I made the same mistake on a review, it was never reviewed, so it stays wrong in both.
- Correcting only disagreements can only raise agreement. Part of any improvement against the corrected labels comes from the relabeling, not from the prompt.
- For that reason, US-7 reports before/after numbers against **both** the original labels (`2e5be67`) and the corrected labels.

Decisions on the 19 reviews that disagreed:

- **LLM wrong (2):** labels kept; listed at the bottom.
- **My label wrong (10):** corrected below.
- **Rule unclear (8):** labels kept; see `error_analysis.md`.

These add to 20 because the 👌 review counts twice: its sentiment was my error, and its theme is an unclear-rule case.

## Changes

Each reason cites the rule in `LABELING_GUIDE.md` that the corrected label follows.

| review_id | field | old value | new value | reason |
|---|---|---|---|---|
| `e4ef5c9e-eb65-42d3-977e-4eb0b3878687` | theme | performance | login_auth | "still a bit slow to log." The slowness is about signing in, which `login_auth` covers. `performance` is only for problems "not covered by another theme". |
| `9bf7da53-b21c-475a-9ae1-e1aca7f75c27` | theme | performance | ui_navigation | Tie-breaker: choose the theme it complains about most. "Convoluted, not intuitive at all" (design) outweighs one word, "Slow". My original note already said "UI is confusing". |
| `b2a81c68-195f-468c-85dc-788a8ffc7daf` | theme | performance | ui_navigation | Tie-breaker: choose the theme it complains about most. "Unorganized", "too complicated", "simple, neat and clean to use and navigate" and "complete redesign" are all about layout and design; "slow" is mentioned once. |
| `b2a81c68-195f-468c-85dc-788a8ffc7daf` | is_feature_request | FALSE | TRUE | Feature request rule: `true` when the review asks for something changed. "NEEDS a complete redesign" asks for it explicitly, consistent with the other reviews I marked `TRUE`. |
| `b2a81c68-195f-468c-85dc-788a8ffc7daf` | request_summary | *(empty)* | Complete app redesign that is simpler and cleaner | Required for `true` reviews; 8 words, within the limit. |
| `3511c3e4-6eac-48df-8a21-6dbde1b97b70` | theme | performance | pay | Tie-breaker: choose the theme it complains about most. The paystub download failure gets two sentences ("unable to download paystubs…", "the file always corrupts"); slowness and layout get a few words each. `pay` covers paystubs. |
| `8ad2cd6e-cac7-425f-b143-6ba762bbed9e` | theme | positive_general | other | "Great environment, friendly people" praises the workplace, not the app. `positive_general` is general praise of the app, so this "doesn't fit any theme above" and is `other`. |
| `484430f0-78d5-4bba-8f78-8d793b56a63e` | sentiment | negative | positive | Sentiment rule: `positive` is "mostly satisfied". 👌 is an approval gesture. *(Its theme is kept as an unclear-rule case; see `error_analysis.md`.)* |
| `d1c64903-aa70-4c00-87b8-2e44b3e2785d` | sentiment | negative | positive | "easy to use" is satisfied: `positive`. |
| `c3502bcc-fbc4-4d6a-a6ee-164f8dc20505` | sentiment | negative | positive | "very easy!" is satisfied: `positive`. |
| `92eb1e74-bf2a-45dd-88ce-1b42ce1d9308` | sentiment | neutral | negative | Sentiment rule: `negative` is "mostly frustrated, or reports a problem". Timesheets taking minutes to load is a reported problem; "works fine sometimes" doesn't balance it out. |
| `536cffb7-62de-4709-9426-f030f842aef7` | sentiment | negative | neutral | Sentiment rule: `neutral` is "mixed, factual, or unclear". "im terminated" is a fact about the reviewer and says nothing about the app. |

## Disagreements where the LLM was wrong (labels kept)

| review_id | text (shortened) | my label (kept) | LLM label |
|---|---|---|---|
| `eddf84fa-0624-4e2d-909d-aabde02cfec8` | "will not allow me to login and when it does i can't see my schedule…" | performance | login_auth |
| `9920ba7d-d8d5-45eb-8ef6-a22a23ab2f13` | "everything takes longer than it should to load… the layout is atrocious…" | performance | ui_navigation |
