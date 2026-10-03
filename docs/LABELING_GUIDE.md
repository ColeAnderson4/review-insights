# Labeling Guide

This guide is used for two things: hand-labeling the 100-review test set, and writing the LLM prompt. Both must follow the same rules. Otherwise, the accuracy check compares two different definitions instead of measuring how good the tool is.

## How to label

1. Choose 100 reviews **at random**, using `df.sample(100, random_state=42)`. Do not hand-pick them.
2. Label all 100 **before** you look at the LLM's output, so its answers don't influence yours.
3. When a review covers several topics, choose the theme it complains about **most**. If it's an even split, choose the one mentioned first.
4. Record each label in `labels.csv`.

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
| `support` | Customer service, help desk, employer or HR admin issues | "Support never responded" |
| `positive_general` | General praise with no specific feature mentioned | "Great app, works fine" |
| `negative_general` | General complaint with no specific feature mentioned | "Terrible app" |
| `other` | Doesn't fit any theme above, or isn't understandable | "ok" |

**Tie-breaker rules**
- A crash that happens *while clocking in* goes under `timekeeping`, because the user's goal is the more useful signal for a PM.
- "Can't log in, so I can't see my pay" goes under `login_auth`, because the login is the root cause.
- Praise that names a specific feature goes under that feature's theme with positive sentiment, not under `positive_general`.
- If a vague complaint also names a specific feature (e.g., "terrible app, keeps logging me out"), use that feature's theme, not `negative_general`.

## Sentiment

| Label | Rule |
|---|---|
| `positive` | Mostly satisfied, even if it mentions a minor issue |
| `neutral` | Mixed, factual, or unclear |
| `negative` | Mostly frustrated, or reports a problem |

Use the text, not the star rating. A 4-star review that complains a lot is `negative`. This difference is one of the things the tool should be able to catch.

## Feature request

Mark `true` only when the review asks for something **new** or **changed**, such as "Please add dark mode" or "Wish I could swap shifts in the app." Reporting a bug ("fix the login") is **not** a feature request. For `true` reviews, write a summary of 8 words or fewer.

## labels.csv columns

`review_id, text, rating, theme, sentiment, is_feature_request, request_summary, notes`

Use `notes` for reviews that were hard to label. They make good examples for the README's limitations section.
