"""Entry point for the multi-page dashboard.

Run from the project root with:  streamlit run src/dashboard.py
(The theme and font come from .streamlit/config.toml.)

This file sets up the header, shared styles, pages, and footer.
Each page's code is in src/views/.
"""

from pathlib import Path

import streamlit as st

from dashboard_common import CARD_COLOR, MUTED_TEXT

LOGO_PATH = Path(__file__).parent / "assets" / "logo.svg"
GITHUB_URL = "https://github.com/ColeAnderson4"
LINKEDIN_URL = "https://www.linkedin.com/in/coleanderson-"

# Must be the first st. call. An int initial_sidebar_state sets the sidebar width in pixels.
st.set_page_config(page_title="App Review Insights", layout="wide", initial_sidebar_state=240)

st.logo(str(LOGO_PATH), size="large")

# Shared CSS. The theme has no settings for these, so they're styled here:
# - Cards: Streamlit gives a container with key="card_..." the class "st-key-card_...";
#   the selector matches any class containing "st-key-card". Same padding on every card.
# - KPI text: classes used by the KPI cards on the Overview (built with st.html).
# - Top padding: Streamlit's default leaves a large gap under the header bar.
st.html(
    f"""
<style>
[class*='st-key-card'] {{ background-color: {CARD_COLOR}; padding: 20px 24px; }}
[data-testid='stMainBlockContainer'] {{ padding-top: 4.5rem; }}
.kpi-label {{ color: {MUTED_TEXT}; font-size: 0.8rem; margin-bottom: 6px; }}
.kpi-row {{ display: flex; align-items: baseline; gap: 8px; line-height: 1.5; white-space: nowrap; }}
.kpi-value {{ font-size: 1.5rem; font-weight: 600; }}
.kpi-value-text {{ font-size: 0.95rem; font-weight: 600; }}
.kpi-note {{ color: {MUTED_TEXT}; font-size: 0.8rem; }}
</style>
"""
)

# Paths are relative to this file.
pages = [
    st.Page("views/overview.py", title="Overview", default=True),
    st.Page("views/deep_dive.py", title="App deep dive", url_path="deep-dive"),
    st.Page("views/reviews.py", title="Read the reviews", url_path="reviews"),
    st.Page("views/feature_requests.py", title="Feature requests", url_path="feature-requests"),
    st.Page("views/method.py", title="Method & validation", url_path="method"),
]

# Top nav bar, so the sidebar only appears on pages that use it (the filters).
current_page = st.navigation(pages, position="top")
current_page.run()

# Footer on every page: it's in the entry script, after the page's own content.
st.space("large")
st.divider()
st.caption(f"Built by Cole Anderson · [GitHub]({GITHUB_URL}) · [LinkedIn]({LINKEDIN_URL})")
