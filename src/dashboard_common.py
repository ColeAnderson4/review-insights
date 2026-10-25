"""Shared data, colors, and helpers for the dashboard pages.

Every page imports from here, so a color or label only has to change in one place.
"""

import pandas as pd
import streamlit as st

DATA_PATH = "data/dashboard_reviews.csv"
EVAL_HISTORY_PATH = "data/eval_history.csv"

# Display names for the app codes stored in the data, in the order we show them.
APP_NAMES = {"ukg_pro": "UKG Pro", "workday": "Workday"}
APP_ORDER = list(APP_NAMES.values())

# Readable labels for each theme. The data keeps the exact names from
# docs/LABELING_GUIDE.md; the exact name is also shown on hover.
THEME_LABELS = {
    "login_auth": "Login & sign-in",
    "timekeeping": "Timekeeping & punches",
    "pay": "Pay & paystubs",
    "scheduling_pto": "Scheduling & time off",
    "performance": "Crashes & slowness",
    "ui_navigation": "Layout & navigation",
    "notifications": "Notifications",
    "messaging_feed": "Messaging & feed",
    "support": "Support & HR",
    "positive_general": "General praise",
    "negative_general": "General complaint",
    "other": "Other",
}

# Colors for the dark theme. All chart colors were checked for contrast on the card
# color and for colorblind separation (simulated protan/deutan/tritan vision).
TEXT_COLOR = "#f0efec"   # off-white, same as textColor in config.toml
MUTED_TEXT = "#a3a19a"   # labels and notes
DARK_INK = "#1f1f1d"     # text printed on top of light chart fills
CARD_COLOR = "#302f2d"   # bordered "card" containers, slightly lighter than the page

# Sentiment is an ordered scale: muted red, dark gray, soft blue. The neutral gray is
# darker than the other two so the small middle segment stays quiet on a dark page.
SENTIMENT_ORDER = ["negative", "neutral", "positive"]
SENTIMENT_COLORS = {"negative": "#d4706a", "neutral": "#64625d", "positive": "#6f9fd8"}

# Complaint charts use one muted, grayish slate that stands out on a dark page without
# glaring. The grouped chart adds a darker slate for Workday.
COMPLAINT_COLOR = "#9ca1aa"
APP_COLORS = {"UKG Pro": COMPLAINT_COLOR, "Workday": "#5d6b88"}

# Themes below this share of an app's negative reviews are folded into "Other".
MIN_THEME_PERCENT = 1.0

# Shared Plotly settings: Inter font and no toolbar.
CHART_FONT = dict(family="Inter, sans-serif", color=TEXT_COLOR, size=12)
# Transparent chart backgrounds, so charts sit directly on the card color.
TRANSPARENT = "rgba(0, 0, 0, 0)"
CHART_CONFIG = {"displayModeBar": False}


def style_chart(fig, height, legend=True):
    """Apply the shared console-style look to a Plotly chart.

    Every chart calls this, so margins, legend position, and fonts stay consistent.
    Pass legend=False for single-series charts, so no space is left for a legend.
    """
    if legend:
        top_margin = 32
    else:
        top_margin = 8
    fig.update_layout(
        height=height,
        font=CHART_FONT,
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        # Small margins; Plotly still widens the left margin to fit the axis labels.
        # The right margin leaves room for the last tick label (e.g. "100%").
        margin=dict(l=0, r=20, t=top_margin, b=0),
        showlegend=legend,
        # Legend in one row above the chart, lined up with the card's left edge.
        # xref="container" measures x from the whole chart area, not the plot area.
        legend=dict(
            orientation="h", title_text="",
            x=0, xref="container", xanchor="left",
            y=1, yref="container", yanchor="top",
        ),
        xaxis_ticksuffix="%",
        xaxis_title_font_size=12,
    )
    return fig


def section_header(label, finding):
    """A short section label, then the finding as one regular-weight sentence."""
    st.subheader(label)
    st.markdown(finding)


# st.cache_data keeps the loaded DataFrame in memory, so the CSV is read once
# instead of on every rerun (Streamlit reruns the page script on each interaction).
@st.cache_data
def load_reviews():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["app_name"] = df["app"].map(APP_NAMES)
    df["theme_label"] = df["theme"].map(THEME_LABELS)
    # Number of words in each review: split on whitespace, then count the pieces.
    df["word_count"] = df["text"].str.split().str.len()
    return df


def complaint_shares(reviews, app_name):
    """Share of one app's negative reviews in each specific theme, largest first.

    Percentages use the app's total negative reviews as the denominator.
    "General praise" and general complaints are left out, and themes under 1%
    are folded into "Other". The "includes" column lists the exact theme names
    behind each bar, so "Other" can link to every theme it contains.
    """
    app_negative = reviews[(reviews["app_name"] == app_name) & (reviews["sentiment"] == "negative")]
    total_negative = len(app_negative)

    specific = app_negative[~app_negative["theme"].isin(["negative_general", "positive_general"])]
    shares = specific.groupby("theme").size().reset_index(name="count")
    shares["percent"] = 100 * shares["count"] / total_negative

    # Each theme's bar: itself if it's at least 1%, otherwise "other".
    shares["bar"] = shares["theme"].where(shares["percent"] >= MIN_THEME_PERCENT, "other")
    shares = shares.groupby("bar", as_index=False).agg(
        count=("count", "sum"),
        percent=("percent", "sum"),
        includes=("theme", ", ".join),
    )
    shares = shares.rename(columns={"bar": "theme"})
    shares["theme_label"] = shares["theme"].map(THEME_LABELS)
    shares["app_name"] = app_name

    # Sort largest first, but always put "Other" last.
    shares["is_other"] = shares["theme"] == "other"
    return shares.sort_values(["is_other", "percent"], ascending=[True, False])


def general_complaint_percent(reviews, app_name):
    """Share of one app's negative reviews that didn't name a specific issue."""
    app_negative = reviews[(reviews["app_name"] == app_name) & (reviews["sentiment"] == "negative")]
    return 100 * (app_negative["theme"] == "negative_general").mean()


def shared_x_range(reviews):
    """One x-axis range for every complaint chart, so bar lengths compare across apps."""
    largest = max(complaint_shares(reviews, app_name)["percent"].max() for app_name in APP_ORDER)
    return [0, largest * 1.1]
