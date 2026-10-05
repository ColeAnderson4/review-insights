# Labeling Guide

This guide is used for two things: hand-labeling the 100-review test set, and writing the LLM prompt. Both must follow the same rules. Otherwise, the accuracy check compares two different definitions instead of measuring how good the tool is.

## How to label

1. Choose 100 reviews **at random**: 50 per app, each with `df.sample(50, random_state=42)`, then shuffled so the apps are mixed. `src/make_label_sample.py` does this. Do not hand-pick them.
2. Label all 100 **before** you look at the LLM's output, so its answers don't influence yours.
3. Record each label in `labels.csv`, then run `src/check_labels.py` to catch typos and missing values.

## Themes (choose exactly one)

| Theme | Use when the review is mainly about… | Example |
|---|---|---|
| `login_auth` | Signing in, passwords, SSO, being logged out, verification codes | "Logs me out every time I switch apps" |
| `timekeeping` | Clocking in or out, punches, timecards, missed or incorrect punches | "My clock-in didn't save and now I'm marked late" |
| `pay` | Paystubs, direct deposit, taxes, W-2s, pay accuracy | "Can't find my paystub anywhere" |
| `scheduling_pto` | Shifts, schedules, time-off requests, shift swaps | "PTO request button does nothing" |
| `performance` | Crashes, freezing, slow loading, bugs not covered by another theme | "Crashes every time I open it" |
| `ui_navigation` | Layout, design, finding features, confusing menus | "Way too many taps to find anything" |
| `notifications` | Push notifications and alerts (missing, too many, or wrong) | "Never get notified when my schedule changes" |
| `messaging_feed` | Chat, team messages, company feed or posts | "Chat messages never load" |
| `support` | Customer service, help desk, employer or HR admin issues | "Support never responded" |
| `positive_general` | General praise with no specific feature mentioned | "Great app, works fine" |
| `negative_general` | General complaint with no specific feature mentioned | "Terrible app" |
| `other` | Doesn't fit any theme above, or isn't understandable | "ok" |

**Tie-breaker rules**
- When a review covers several topics, choose the theme it complains about **most**. If it's an even split, choose the one mentioned first.
- A crash that happens *while clocking in* goes under `timekeeping`, because the user's goal is the more useful signal for a PM.
- "Can't log in, so I can't see my pay" goes under `login_auth`, because the login is the root cause.
- Praise that names a specific feature goes under that feature's theme with positive sentiment, not under `positive_general`.
- If a vague complaint also names a specific feature (e.g., "terrible app, keeps logging me out"), use that feature's theme, not `negative_general`.
- "I don't get notified about new chat messages" goes under `notifications`, because the alert is what failed, not the chat itself.
- Slowness or extra steps while signing in go under `login_auth`, the same way a crash while clocking in goes under `timekeeping`. Use `performance` for slowness after sign-in.

**Edge cases**
- Install, update, and device or OS compatibility problems (e.g., "Recent update makes the app incompatible with my phone") go under `performance`.
- Confusion about the app's wording, steps, or flows (e.g., "confusing on terms") goes under `ui_navigation`, even if the review doesn't mention menus or layout.
- General ease-of-use praise ("easy to use", "very easy") goes under `positive_general`. Only praise that names navigation, layout, or design ("easy to navigate") goes under `ui_navigation`.
- If a review is mainly about the employer, job, or coworkers rather than the app (e.g., "Great environment, friendly people"), use `other`. If it praises the app for a job-related use, such as applying, onboarding, or switching jobs, treat it as app praise, and use `positive_general` when the feature it names has no theme.
- Label emoji-only reviews by their meaning: a clearly positive emoji such as 👌 or 👍 is `positive_general`, and an emoji whose meaning is unclear is `other`.
- Label non-English reviews by their meaning. In `labels.csv`, record the language in `notes`.

## Sentiment

| Label | Rule |
|---|---|
| `positive` | Mostly satisfied, even if it mentions a minor issue |
| `neutral` | Mixed, factual, or unclear |
| `negative` | Mostly frustrated, or reports a problem |

Use the text, not the star rating. A 4-star review that complains a lot is `negative`. This difference is one of the things the tool should be able to catch.

## Feature request

Mark `true` only when the review asks for something **new** or **changed**, such as "Please add dark mode" or "Wish I could swap shifts in the app." Reporting a bug ("fix the login") is **not** a feature request. For `true` reviews, write a summary of 8 words or fewer in `request_summary`.

The request must be **explicit**. If a review only complains about a gap and you have to infer what they want (e.g., "it doesn't show how much time was used"), mark it `false`, leave `request_summary` empty, and write the implied request in `notes`.

## labels.csv columns

`review_id, app, text, theme, sentiment, is_feature_request, request_summary, notes`

The star rating is left out on purpose, so it can't bias the sentiment label. If needed, join it back from `data/raw/` by `review_id`.

Use `notes` for reviews that were hard to label. They make good examples for the README's limitations section.
