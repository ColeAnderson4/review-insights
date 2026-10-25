"""Score one classification run against the hand labels in data/labels.csv.

Reports theme and sentiment agreement (overall and per app), feature-request
precision/recall/F1, a theme confusion matrix, and every disagreement, then
compares the results to the targets in docs/PRD.md.

Usage (run from the project root):
    python src/evaluate.py --list-runs
    python src/evaluate.py                                    # works when there is only one run
    python src/evaluate.py --model claude-sonnet-5-5 --prompt-version 1a46f99f
    python src/evaluate.py --show-disagreements               # also print every disagreement
    python src/evaluate.py --labels data/raw/labels_2e5be67.csv  # score against another labels file
"""

import argparse
from datetime import datetime
import hashlib
from pathlib import Path

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

from classify import LABELS_PATH, THEMES
from scrape import APPS, RAW_DIR

CLASSIFIED_PATH = RAW_DIR / "classified_labels.csv"

# One row per evaluated run. Numbers only, no review text, so it's safe to commit.
HISTORY_PATH = Path("data/eval_history.csv")

# Model-quality targets from docs/PRD.md section 6.
# (metric key in the results dict, label for the report, target, "min" or "max")
PRD_TARGETS = [
    ("theme_agreement", "Theme agreement", 0.80, "min"),
    ("sentiment_agreement", "Sentiment agreement", 0.85, "min"),
    ("fr_f1", "Feature-request F1", 0.75, "min"),
    ("failure_rate", "Malformed JSON responses", 0.02, "max"),
]

# The LLM columns we score. "app" is left out because labels.csv already has it,
# so the merged table gets one "app" column instead of app_hand and app_llm.
LLM_COLUMNS = ["review_id", "theme", "sentiment", "is_feature_request", "request_summary"]


def to_bool(values, file_name):
    """Turn a column of "TRUE"/"True"/"FALSE"/"False" strings into real booleans.

    labels.csv says TRUE/FALSE (saved by Excel) and the LLM output says
    True/False (written by pandas), so both are upper-cased first.
    Raises ValueError on anything else, e.g. an empty cell or a typo.
    """
    upper = values.str.strip().str.upper()
    converted = upper.map({"TRUE": True, "FALSE": False})

    if converted.isna().any():
        bad = values[converted.isna()].unique()
        raise ValueError(f"is_feature_request in {file_name} has values that aren't true/false: {bad}")

    return converted.astype(bool)


def labels_version(path):
    """Return the first 8 hex characters of the file's SHA-256, used to tell label versions apart.

    Any edit to the file, even re-saving it in Excel, gives a new version.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:8]


def load_data(model, prompt_version, labels_path):
    """Join the hand labels to one run's LLM labels by review_id.

    Input:
        model, prompt_version: which run to score (see list_runs()).
        labels_path: the hand-labels CSV to score against (usually LABELS_PATH).

    Returns (merged, n_missing):
        merged:    one row per review that both files have. Columns: review_id,
                   app, text, notes, and each label twice with a suffix, e.g.
                   theme_hand and theme_llm.
        n_missing: hand-labeled reviews with no row in this run. classify.py
                   only writes rows that passed validation, so these are the
                   reviews that failed (used for the malformed-JSON target).
    """
    # dtype=str for the same reason as load_done_ids in classify.py: a version
    # like "12345678" would otherwise load as a number and never match.
    labels = pd.read_csv(labels_path, dtype=str)
    classified = pd.read_csv(CLASSIFIED_PATH, dtype=str)

    run = classified[(classified["model"] == model) & (classified["prompt_version"] == prompt_version)]
    if run.empty:
        raise ValueError(f"No rows for model {model!r}, prompt version {prompt_version!r} in {CLASSIFIED_PATH}")

    # classify.py skips reviews already done for a run, so a repeat here means something went wrong
    if run["review_id"].duplicated().any():
        raise ValueError(f"Some review_ids appear more than once in this run of {CLASSIFIED_PATH}")

    # Inner join: reviews missing from the run are counted in n_missing instead.
    merged = labels.merge(
        run[LLM_COLUMNS],
        on="review_id",
        how="inner",
        suffixes=("_hand", "_llm"),
    )
    n_missing = len(labels) - len(merged)

    merged["is_feature_request_hand"] = to_bool(merged["is_feature_request_hand"], labels_path)
    merged["is_feature_request_llm"] = to_bool(merged["is_feature_request_llm"], CLASSIFIED_PATH)

    # Empty cells load as NaN. Blank strings print and compare more simply.
    for column in ["notes", "request_summary_hand", "request_summary_llm"]:
        merged[column] = merged[column].fillna("")

    return merged, n_missing


def agreement(merged, column):
    """Return the share of rows (0.0 to 1.0) where the hand label equals the LLM label.

    column: "theme" or "sentiment". Compares merged[column + "_hand"] to merged[column + "_llm"].
    """
    hand = merged[column + "_hand"]
    llm = merged[column + "_llm"]
    return (hand == llm).mean()


def majority_baseline(merged, column):
    """Return (label, share): the most common hand label and the agreement you'd get
    by always guessing it.

    This is the score of a "model" that ignores the review text, so a real model
    is only useful to the extent that it beats this number.
    """
    shares = merged[column + "_hand"].value_counts(normalize=True)
    return shares.index[0], shares.iloc[0]


def feature_request_scores(merged):
    """Return precision, recall, F1 and the TP/FP/FN counts for is_feature_request.

    The hand label is the truth (y_true) and the LLM label is the prediction (y_pred).
    """
    y_true = merged["is_feature_request_hand"]
    y_pred = merged["is_feature_request_llm"]

    # zero_division=0: if the LLM flags nothing, precision is 0/0. Report 0 instead of a warning.
    scores = {
        "fr_precision": precision_score(y_true, y_pred, zero_division=0),
        "fr_recall": recall_score(y_true, y_pred, zero_division=0),
        "fr_f1": f1_score(y_true, y_pred, zero_division=0),
        "fr_tp": int((y_true & y_pred).sum()),    # both say request
        "fr_fp": int((~y_true & y_pred).sum()),   # LLM says request, I don't
        "fr_fn": int((y_true & ~y_pred).sum()),   # I say request, LLM doesn't
    }
    return scores


def theme_confusion_matrix(merged):
    """Return a THEMES x THEMES table of counts: rows = hand theme, columns = LLM theme.

    The diagonal is agreement. Off-diagonal cells show which themes get mixed up.
    """
    matrix = pd.crosstab(merged["theme_hand"], merged["theme_llm"])

    # Add unused themes as zeros, in guide order, so every run's matrix has the same shape.
    matrix = matrix.reindex(index=THEMES, columns=THEMES, fill_value=0)
    matrix.index.name = "hand \\ llm"
    matrix.columns.name = None
    return matrix


def find_disagreements(merged):
    """Return the rows where theme, sentiment, or feature request differ.

    Adds a differs_on column, e.g. "theme, sentiment", so you can filter in a spreadsheet.
    """
    differs_on = []
    for _, row in merged.iterrows():
        fields = []
        for field in ["theme", "sentiment", "is_feature_request"]:
            if row[field + "_hand"] != row[field + "_llm"]:
                fields.append(field)
        differs_on.append(", ".join(fields))

    result = merged.copy()
    result["differs_on"] = differs_on
    result = result[result["differs_on"] != ""]

    columns = [
        "review_id", "app", "differs_on", "text",
        "theme_hand", "theme_llm",
        "sentiment_hand", "sentiment_llm",
        "is_feature_request_hand", "is_feature_request_llm",
        "request_summary_hand", "request_summary_llm",
        "notes",
    ]
    return result[columns]


def evaluate_run(merged, n_missing):
    """Compute every metric for one run and return them in one flat dict."""
    results = {
        "n_scored": len(merged),
        "n_missing": n_missing,
        # Reviews with no row in the run failed validation in classify.py
        "failure_rate": n_missing / (len(merged) + n_missing),
        "theme_agreement": agreement(merged, "theme"),
        "sentiment_agreement": agreement(merged, "sentiment"),
    }

    for app_name in APPS:
        app_rows = merged[merged["app"] == app_name]
        results[f"theme_agreement_{app_name}"] = agreement(app_rows, "theme")
        results[f"sentiment_agreement_{app_name}"] = agreement(app_rows, "sentiment")

    for column in ["theme", "sentiment"]:
        label, share = majority_baseline(merged, column)
        results[f"{column}_baseline_label"] = label
        results[f"{column}_baseline"] = share

    results.update(feature_request_scores(merged))
    return results


def pct(value):
    """Format a 0-1 share as a percentage, or "n/a" for NaN (a slice with no rows)."""
    if pd.isna(value):
        return "n/a"
    return f"{value:.0%}"


def print_summary(results):
    """Print agreement, per-app agreement, baselines, and feature-request scores."""
    print(f"\nScored {results['n_scored']} reviews ({results['n_missing']} missing from this run)")

    print("\nAgreement with hand labels")
    print(f"  {'':12}{'overall':>9}", end="")
    for app_name in APPS:
        print(f"{app_name:>10}", end="")
    print("   baseline (always guess the most common label)")

    for column in ["theme", "sentiment"]:
        print(f"  {column:12}{pct(results[column + '_agreement']):>9}", end="")
        for app_name in APPS:
            print(f"{pct(results[f'{column}_agreement_{app_name}']):>10}", end="")
        print(f"   {pct(results[column + '_baseline'])} ({results[column + '_baseline_label']})")

    print("\nFeature requests (hand label = truth)")
    print(f"  precision {results['fr_precision']:.2f}   recall {results['fr_recall']:.2f}   "
          f"F1 {results['fr_f1']:.2f}")
    print(f"  TP {results['fr_tp']}   FP {results['fr_fp']}   FN {results['fr_fn']}   "
          f"(hand-labeled requests: {results['fr_tp'] + results['fr_fn']})")
    print("  baseline (always guess false): F1 0.00")


def print_targets(results):
    """Print each PRD target with the actual value and PASS or MISS."""
    print("\nPRD targets")
    print(f"  {'Metric':26}{'Target':>10}{'Actual':>10}   Result")

    for key, label, target, direction in PRD_TARGETS:
        actual = results[key]

        if key == "fr_f1":
            target_text = f">= {target:.2f}"
            actual_text = f"{actual:.2f}"
        elif direction == "min":
            target_text = f">= {target:.0%}"
            actual_text = pct(actual)
        else:
            target_text = f"< {target:.0%}"
            actual_text = f"{actual:.1%}"

        if direction == "min":
            passed = actual >= target
        else:
            passed = actual < target

        if passed:
            result_text = "PASS"
        else:
            result_text = "MISS"

        print(f"  {label:26}{target_text:>10}{actual_text:>10}   {result_text}")


def save_history(results, model, prompt_version, labels_ver):
    """Write this run's numbers to HISTORY_PATH, replacing any earlier row for the
    same run scored against the same labels.

    Re-scoring the same run against the same labels gives the same numbers, so
    keeping one row per (model, prompt_version, labels_version) stops the
    before/after table filling with duplicates. Scoring against a different
    labels file (e.g. the original vs. corrected labels) adds a separate row.
    """
    row = {
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "prompt_version": prompt_version,
        "labels_version": labels_ver,
    }
    row.update(results)
    new_row = pd.DataFrame([row])

    if HISTORY_PATH.exists():
        # Read versions as text: a hash like "12345678" would otherwise load as a number
        history = pd.read_csv(HISTORY_PATH, dtype={"prompt_version": str, "labels_version": str})
        same_run = (
            (history["model"] == model)
            & (history["prompt_version"] == prompt_version)
            & (history["labels_version"] == labels_ver)
        )
        history = pd.concat([history[~same_run], new_row], ignore_index=True)
    else:
        history = new_row

    history.to_csv(HISTORY_PATH, index=False)


def list_runs():
    """Return a DataFrame of the runs in CLASSIFIED_PATH: model, prompt_version, rows."""
    classified = pd.read_csv(CLASSIFIED_PATH, dtype=str)
    runs = classified.groupby(["model", "prompt_version"]).size().reset_index(name="rows")
    return runs


def choose_run(model, prompt_version):
    """Return the (model, prompt_version) to score.

    If both are given, use them. If neither is given and the file has exactly
    one run, use that one. Otherwise stop and list the runs, rather than guess.
    """
    if model is not None and prompt_version is not None:
        return model, prompt_version

    runs = list_runs()
    if model is None and prompt_version is None and len(runs) == 1:
        return runs["model"].iloc[0], runs["prompt_version"].iloc[0]

    raise SystemExit(
        "Pick a run with --model and --prompt-version. Runs in "
        f"{CLASSIFIED_PATH}:\n{runs.to_string(index=False)}"
    )


def main():
    parser = argparse.ArgumentParser(description="Score a classification run against the hand labels.")
    parser.add_argument("--model", help="Model name of the run to score, e.g. claude-sonnet-5-5.")
    parser.add_argument("--prompt-version", help="Prompt version of the run to score, e.g. 1a46f99f.")
    parser.add_argument("--list-runs", action="store_true", help="List the runs available to score, then stop.")
    parser.add_argument(
        "--show-disagreements",
        action="store_true",
        help="Also print every disagreement (they are always saved to CSV).",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=LABELS_PATH,
        help=f"Hand-labels CSV to score against (default: {LABELS_PATH}).",
    )
    args = parser.parse_args()

    if args.list_runs:
        print(list_runs().to_string(index=False))
        return

    model, prompt_version = choose_run(args.model, args.prompt_version)
    labels_ver = labels_version(args.labels)
    print(f"Evaluating model {model}, prompt version {prompt_version}")
    print(f"Against labels {args.labels} (labels version {labels_ver})")

    merged, n_missing = load_data(model, prompt_version, args.labels)
    results = evaluate_run(merged, n_missing)

    print_summary(results)
    print_targets(results)

    # Wide enough that the 12 x 12 matrix prints on one block instead of wrapping
    pd.set_option("display.width", 250)
    print("\nTheme confusion matrix (rows = hand label, columns = LLM label)")
    print(theme_confusion_matrix(merged).to_string())

    disagreements = find_disagreements(merged)
    disagreements_path = RAW_DIR / f"disagreements_{model}_{prompt_version}_{labels_ver}.csv"
    disagreements.to_csv(disagreements_path, index=False)
    print(f"\n{len(disagreements)} disagreements saved to {disagreements_path}")

    if args.show_disagreements:
        for _, row in disagreements.iterrows():
            print(f"\n[{row['app']}] differs on: {row['differs_on']}")
            print(f"  {row['text']}")
            print(f"  theme      hand {row['theme_hand']:18} llm {row['theme_llm']}")
            print(f"  sentiment  hand {row['sentiment_hand']:18} llm {row['sentiment_llm']}")
            print(f"  request    hand {str(row['is_feature_request_hand']):18} "
                  f"llm {row['is_feature_request_llm']}")
            if row["notes"]:
                print(f"  notes: {row['notes']}")

    save_history(results, model, prompt_version, labels_ver)
    print(f"Summary row saved to {HISTORY_PATH}")


if __name__ == "__main__":
    main()