# Error Analysis

Review of the disagreements between my hand labels and the LLM in the first evaluation run (US-7).

- **Run:** model `claude-sonnet-5-5`, prompt version `1a46f99f`, 2026-10-04
- **Results:** theme agreement 0.85, sentiment agreement 0.95, feature-request F1 0.80
- **Disagreements:** 19 reviews (15 theme, 5 sentiment, 1 feature request; 2 reviews differ on two fields)

For each disagreement I decided whether the LLM was wrong, my label was wrong, or the rule in `LABELING_GUIDE.md` is unclear.

| Decision | Count | Where it's recorded |
|---|---|---|
| LLM was wrong | 2 | Labels kept; listed in `label_corrections.md` |
| My label was wrong | 10 | Labels corrected; logged in `label_corrections.md` |
| Rule is unclear | 8 | Labels kept; listed below |

The 👌 review counts in two rows (sentiment: my error; theme: unclear rule), so the counts add up to 20.

## Reviews where the rule is unclear

Labels for these reviews were **not** changed in round 1. This section records what the guide left open. The rule decided for each gap is listed in [Decisions](#decisions).

### 1. Slowness while logging in

| review_id | text | my label | LLM label |
|---|---|---|---|
| `6dc9f61b-c70c-42bc-8431-c7bffd95d54c` | "awful, it takes forever to log in and then it takes forever to load anything" | performance | login_auth |

**What's unclear:** `login_auth` covers "signing in", and `performance` covers "slow loading… not covered by another theme". The guide never says whether *slow* sign-in is a login problem or a performance problem. I relabeled "still a bit slow to log." (`e4ef5c9e`) as `login_auth`. If that holds, this review is an even split between slow login and slow loading. The "even split, so choose the one mentioned first" rule would then pick `login_auth`, but the guide doesn't confirm that reading.

### 2. Device compatibility

| review_id | text | my label | LLM label |
|---|---|---|---|
| `b1ee8878-036e-4593-b656-e02d084ba3ca` | "I shouldn't have to change my phone inorder to make this device compatible for my phone. it's a required app for my job. this workday company sucks…" | performance | other |

**What's unclear:** no theme covers installation, device or OS compatibility. `performance` says "bugs not covered by another theme", but it isn't clear whether an unsupported phone counts as a bug. The review also complains about the company ("this workday company sucks"), which could point to `negative_general`.

### 3. Confusion that doesn't name the interface

| review_id | text | my label | LLM label |
|---|---|---|---|
| `497637b3-8006-4959-bfd7-d1c7d15da117` | "confusing on terms" | ui_navigation | other |
| `0dd74fb3-4a0b-436b-9104-3125193e368d` | "Unclear processes" | ui_navigation | other |

**What's unclear:** `ui_navigation` covers "layout, design, finding features, confusing menus". It isn't clear whether confusion about *terminology* or *processes* counts. Those could be the app's wording and flows, or the employer's HR processes. For very short reviews, `ui_navigation` also overlaps with `other` ("isn't understandable").

### 4. "Easy to use" praise, and non-English reviews

| review_id | text | my label | LLM label |
|---|---|---|---|
| `c2a81d78-2c78-4b18-abda-c1f7537fac87` | "mudah digunakan" (Indonesian: "easy to use") | ui_navigation | positive_general |

**What's unclear:**
- **"Easy to use":** it isn't clear whether this is general praise (`positive_general`) or praise of usability. Under the "praise that names a specific feature" rule, usability praise would be `ui_navigation`. My own labels are inconsistent here: the English reviews "easy to use" (`d1c64903`) and "very easy!" (`c3502bcc`) are labeled `positive_general`.
- **Non-English reviews:** the guide doesn't say whether to label them by their meaning or treat them as `other`.

### 5. Praise for the job or employer, not the app

| review_id | text | my label | LLM label |
|---|---|---|---|
| `30c8cdbc-822d-402c-a5f5-faea15b0f07c` | "solid for switching jobs" | positive_general | other |
| `e198e300-cce6-44fb-8644-6661127d9758` | "Thank you so much for giving me this opportunity… I thank you for the free background check as well as the easy experience of changing my profile." | positive_general | other |

**What's unclear:**
- **Job seekers:** Workday is also used for job applications and onboarding, but no theme covers that use, and the guide doesn't say how to label reviews from job seekers.
- **Unlisted features:** `e198e300` names specific features (background check, profile editing). The rule says to file such praise under "that feature's theme", but neither feature has a theme.
- **Consistency:** I relabeled "Great environment, friendly people" (`8ad2cd6e`) as `other` because it praises the workplace. Whatever rule is chosen here should give consistent answers for all three reviews.

### 6. Emoji-only reviews

| review_id | text | my label | LLM label |
|---|---|---|---|
| `484430f0-78d5-4bba-8f78-8d793b56a63e` | "👌" | positive_general | other |

**What's unclear:** the guide's example for `other` is "ok", and 👌 means roughly the same thing. But the emoji also reads as general praise, which would make it `positive_general`. The guide doesn't say how to handle reviews that are only emoji. (Its sentiment was corrected to `positive`; see `label_corrections.md`.)

## Patterns

- Before corrections, `performance` was my label on 8 of the 15 theme disagreements. The LLM never chose `performance` when I hadn't.
- The LLM chose `other` on 7 of the 15 theme disagreements, all for Workday reviews. Several of the unclear cases above (2, 5, 6) involve reviews that don't fit a theme built around employee timekeeping and scheduling.
- All 3 cases where I labeled `negative` and the LLM labeled `positive` were very short praise reviews. All 3 were my labeling errors.

## Decisions

For each gap, I compared two candidate rules and listed every review in all 100 rows whose label would change under each one. The chosen rules are now in `LABELING_GUIDE.md`. The resulting label changes are logged in `label_corrections.md` (round 2).

| # | Gap | Rule chosen | Alternative rejected | Labels changed |
|---|---|---|---|---|
| 1 | Slowness while logging in | Slowness or extra steps while signing in go under `login_auth`, like a crash while clocking in goes under `timekeeping` | Slowness is always `performance` (this would have undone the `e4ef5c9e` correction) | `6dc9f61b` → login_auth |
| 2 | Device compatibility | Install, update and device/OS compatibility problems go under `performance` | Put them under `other` | none (`b1ee8878`, `80c9632e` and `925d41c2` were already `performance`) |
| 3 | Confusion that doesn't name the interface | Confusion about the app's wording, steps or flows goes under `ui_navigation` | Very short, unclear confusion goes under `other` | none (`cc3fb136` "its doing too much" was considered and kept as `negative_general`) |
| 4a | "Easy to use" praise | General ease praise is `positive_general`; only praise naming navigation, layout or design is `ui_navigation` | All ease-of-use praise goes under `ui_navigation` (this would have changed 5 or 6 reviews) | `c2a81d78` → positive_general |
| 4b | Non-English reviews | Label by meaning and record the language in `notes` | Non-English reviews go under `other` | none |
| 5 | Praise for the job or employer | Reviews mainly about the employer, job or coworkers are `other`; app praise for a job-related use stays app praise (`positive_general` if the feature has no theme) | Anything about the job, employer or hiring is `other` | `f3ecf9ac` → other (`d5e8bc72`, French, was considered and kept as `positive_general`) |
| 6 | Emoji-only reviews | Label by meaning: a clearly positive emoji is `positive_general`, and an emoji whose meaning is unclear is `other` | Every emoji-only review is `other` | none (`484430f0` 👌 stays `positive_general`) |

While checking all 100 rows, I also found two labels that broke rules **already** in the guide. I corrected both:
- `eddf84fa` → `login_auth`: its main complaint is that sign-in fails. In round 1, I wrongly recorded it as an LLM error.
- `84234bca` → `timekeeping`: under the clock-in tie-breaker, slowness while clocking in goes under `timekeeping`.

The 2026-10-04 run was originally scored as 0.85 theme agreement. Because the round-1 corrections and these 5 changes were made after seeing that run's labels, US-7 reports every score against both the original labels and the newest labels.
