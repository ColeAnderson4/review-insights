"""Method & validation: how the data was collected and how accurate the classifier is."""

import pandas as pd
import streamlit as st

from dashboard_common import EVAL_HISTORY_PATH, section_header

# Readable names for the versions in eval_history.csv. Only these two label versions
# are shown: they make the 2x2 comparison (each prompt x each set of hand labels).
PROMPT_NAMES = {"1a46f99f": "Original prompt", "4af6be35": "Revised prompt (final)"}
LABEL_NAMES = {"19d83b15": "Original hand labels", "fdc92925": "Corrected hand labels"}

st.title("Method & validation")

with st.container(border=True, key="card_method"):
    st.subheader("Method")
    st.markdown(
        """
- **Data:** the 1,000 newest US English Google Play reviews per app, scraped with
  google-play-scraper. Reviewer names and profile images are not stored.
- **Classification:** Claude Sonnet 5.5 (prompt version `4af6be35`) gave each review one
  theme, a sentiment, and a feature-request flag, returned as validated JSON. Theme
  definitions are in `docs/LABELING_GUIDE.md`.
- **Validation:** 100 randomly sampled reviews (50 per app) were labeled by hand before
  looking at the model's answers, then compared with the model's labels.
"""
    )


# ---------------------------------------------------------------------------
# Accuracy results from data/eval_history.csv
# ---------------------------------------------------------------------------
# Keep version hashes as text (e.g. "12345678" would load as a number).
history = pd.read_csv(
    EVAL_HISTORY_PATH, dtype={"prompt_version": str, "labels_version": str}
)
results = history[history["labels_version"].isin(LABEL_NAMES)].copy()

results["Prompt"] = results["prompt_version"].map(PROMPT_NAMES)
results["Hand labels"] = results["labels_version"].map(LABEL_NAMES)
results["Theme agreement"] = 100 * results["theme_agreement"]
results["Sentiment agreement"] = 100 * results["sentiment_agreement"]
results["Feature-request F1"] = results["fr_f1"]

# Show original labels first, and the original prompt before the revised one.
results["label_order"] = results["labels_version"].map(list(LABEL_NAMES).index)
results["prompt_order"] = results["prompt_version"].map(list(PROMPT_NAMES).index)
results = results.sort_values(["label_order", "prompt_order"])

with st.container(border=True, key="card_accuracy"):
    section_header(
        "Accuracy",
        "Revising the prompt raised theme agreement with hand labels from 85% to 89%.",
    )
    st.dataframe(
        results[["Hand labels", "Prompt", "Theme agreement", "Sentiment agreement", "Feature-request F1"]],
        hide_index=True,
        column_config={
            "Theme agreement": st.column_config.NumberColumn(format="%.0f%%"),
            "Sentiment agreement": st.column_config.NumberColumn(format="%.0f%%"),
            "Feature-request F1": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    st.markdown(
        """
- **Prompt improvement:** against the original hand labels, the revised prompt raised
  theme agreement from 85% to 89%. Sentiment stayed at 95%.
- **Label corrections:** over two review rounds, labels on 15 of the 100 reviews were
  corrected (logged in `docs/label_corrections.md`). Against the corrected labels, the final prompt
  agrees on 99% of themes and 100% of sentiments. The model didn't change between those
  two numbers; only the answer key did.
- **Caveats:** the sample is 100 reviews, so 4 points means 4 reviews. The corrections and
  the clarified labeling rules were made after seeing the model's answers on these same
  reviews, with no separate held-out set. That's why the original-label scores are the
  more cautious estimate.
"""
    )
