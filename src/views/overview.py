"""Overview: KPI row, sentiment split per app, and a grouped comparison of complaint themes."""

import html

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_common import (
    APP_COLORS, APP_ORDER, CHART_CONFIG, COMPLAINT_COLOR, DARK_INK, SENTIMENT_COLORS,
    SENTIMENT_ORDER, TEXT_COLOR, complaint_shares, general_complaint_percent,
    load_reviews, section_header, style_chart,
)

KPI_CARD_HEIGHT = 130  # pixels; a fixed height keeps the four KPI cards the same size


def kpi_card(column, key, label, rows):
    """One KPI card: a small label, then one line per (value, note) pair.

    html.escape turns characters like "&" in "Crashes & slowness" into safe HTML.
    """
    lines = [f"<div class='kpi-label'>{html.escape(label)}</div>"]
    for value, note, value_class in rows:
        row = f"<div class='kpi-row'><span class='{value_class}'>{html.escape(value)}</span>"
        # Some rows have no note; only add the note span when there is one.
        if note:
            row += f"<span class='kpi-note'>{html.escape(note)}</span>"
        lines.append(row + "</div>")
    with column.container(border=True, key=key, height=KPI_CARD_HEIGHT):
        st.html("".join(lines))


reviews = load_reviews()

# ---------------------------------------------------------------------------
# Numbers used by the KPI row and the section findings
# ---------------------------------------------------------------------------
first_date = reviews["date"].min().strftime("%b %-d")
last_date = reviews["date"].max().strftime("%b %-d, %Y")

# Count reviews per (app, sentiment), then divide by each app's total review count.
sentiment = reviews.groupby(["app_name", "sentiment"]).size().reset_index(name="count")
app_totals = reviews["app_name"].value_counts()
sentiment["percent"] = 100 * sentiment["count"] / sentiment["app_name"].map(app_totals)
negative_percent = sentiment[sentiment["sentiment"] == "negative"].set_index("app_name")["percent"]

# One table with both apps' complaint theme shares stacked on top of each other.
shares = pd.concat([complaint_shares(reviews, app_name) for app_name in APP_ORDER])
# complaint_shares() sorts largest first, so the first row per app is its top theme.
top_theme = shares.groupby("app_name")[["theme_label", "percent"]].first()

requests_per_app = reviews[reviews["is_feature_request"]]["app_name"].value_counts()

# ---------------------------------------------------------------------------
# Page title
# ---------------------------------------------------------------------------
st.title("Overview")
st.caption(
    f"{len(reviews):,} Google Play reviews of UKG Pro and Workday ({first_date} – {last_date}), "
    "the 1,000 newest US English reviews per app, classified by Claude."
)

# ---------------------------------------------------------------------------
# Key takeaways (written by hand, not calculated)
# ---------------------------------------------------------------------------
with st.container(border=True, key="card_takeaways"):
    st.subheader("Key takeaways")
    st.markdown(
        """
- Crashes and slowness make up 31% of UKG Pro’s negative reviews, so UKG should prioritize app stability before new features.
- Both apps frustrate users at the front door: login issues are a top-two complaint for each, which makes “stay signed in” or smoother SSO a high-value fix.
- 89% of UKG Pro reviews are negative compared to 46% for Workday, so UKG Pro faces broad dissatisfaction while Workday’s problems are narrower and more concentrated.
"""
    )

# ---------------------------------------------------------------------------
# KPI row: four cards of the same size
# ---------------------------------------------------------------------------
# The "Top complaint" card is a bit wider so each app's line fits without wrapping.
kpi_columns = st.columns([1, 1, 1.4, 1])
kpi_card(
    kpi_columns[0], "card_kpi_reviews", "Reviews analyzed",
    [(f"{len(reviews):,}", f"{app_totals.iloc[0]:,} per app", "kpi-value")],
)
kpi_card(
    kpi_columns[1], "card_kpi_negative", "Negative reviews",
    [(f"{negative_percent[app]:.0f}%", app, "kpi-value") for app in APP_ORDER],
)
kpi_card(
    kpi_columns[2], "card_kpi_complaint", "Top complaint",
    # One line per app, e.g. "UKG Pro: Crashes & slowness, 31%".
    [
        (
            f"{app}: {top_theme.loc[app, 'theme_label']}, {top_theme.loc[app, 'percent']:.0f}%",
            "",
            "kpi-value-text",
        )
        for app in APP_ORDER
    ],
)
kpi_card(
    kpi_columns[3], "card_kpi_requests", "Feature requests",
    [
        (
            f"{requests_per_app.sum():,}",
            " · ".join(f"{requests_per_app[app]} {app}" for app in APP_ORDER),
            "kpi-value",
        )
    ],
)

# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------
# border=True draws a box around everything inside the "with" block. A key starting
# with "card" gives it the card background and padding (see the CSS in dashboard.py).
with st.container(border=True, key="card_sentiment"):
    section_header(
        "Sentiment",
        f"{negative_percent['UKG Pro']:.0f}% of UKG Pro reviews are negative, almost double "
        f"Workday's {negative_percent['Workday']:.0f}%.",
    )

    # 100% stacked horizontal bar: one row per app, segments ordered negative -> positive.
    sentiment_chart = px.bar(
        sentiment,
        x="percent",
        y="app_name",
        color="sentiment",
        orientation="h",
        text="percent",
        category_orders={"sentiment": SENTIMENT_ORDER, "app_name": APP_ORDER},
        color_discrete_map=SENTIMENT_COLORS,
        hover_data={"count": True, "percent": ":.1f", "app_name": False},
        labels={"percent": "Share of app's reviews", "app_name": "", "sentiment": "Sentiment"},
    )
    # Print the % inside each segment, and hide labels on segments too thin to fit them.
    # Dark text on the blue fill; off-white text on the dark neutral gray.
    sentiment_chart.update_traces(
        texttemplate="%{x:.0f}%", textfont_color=DARK_INK, insidetextanchor="middle"
    )
    sentiment_chart.update_traces(selector=dict(name="neutral"), textfont_color=TEXT_COLOR)
    # No label on the negative segment: the KPI row already shows those numbers.
    # (An empty texttemplate counts as "not set" in Plotly; textposition="none" hides the text.)
    sentiment_chart.update_traces(selector=dict(name="negative"), textposition="none")
    style_chart(sentiment_chart, height=170)
    # bargap is the space between bars as a fraction of each slot: higher = thinner bars.
    sentiment_chart.update_layout(
        xaxis_range=[0, 100], bargap=0.45,
        uniformtext_minsize=11, uniformtext_mode="hide",
    )
    st.plotly_chart(sentiment_chart, config=CHART_CONFIG)

# ---------------------------------------------------------------------------
# Top complaints: grouped comparison of both apps
# ---------------------------------------------------------------------------
# Sort themes by combined share so the biggest is at the top; "Other" goes last.
theme_totals = shares[shares["theme"] != "other"].groupby("theme_label")["percent"].sum()
theme_order = theme_totals.sort_values(ascending=False).index.tolist() + ["Other"]

with st.container(border=True, key="card_themes"):
    section_header(
        "Top complaints",
        f"UKG Pro's top complaint is {top_theme.loc['UKG Pro', 'theme_label'].lower()}; "
        f"Workday's is {top_theme.loc['Workday', 'theme_label'].lower()}. "
        "Click a bar to read those reviews.",
    )

    theme_chart = px.bar(
        shares,
        x="percent",
        y="theme_label",
        color="app_name",
        orientation="h",
        barmode="group",
        # Horizontal grouped bars draw the first app at the bottom of each group, so the
        # app order is reversed here (and the legend reversed back) to put UKG Pro on top.
        category_orders={"theme_label": theme_order, "app_name": APP_ORDER[::-1]},
        color_discrete_map=APP_COLORS,
        # custom_data rides along with each bar, so a click tells us which app and themes it was.
        custom_data=["app_name", "includes"],
        hover_data={"count": True, "percent": ":.1f", "includes": True, "theme_label": False},
        labels={
            "percent": "Share of app's negative reviews",
            "theme_label": "",
            "app_name": "App",
            "includes": "Theme",
        },
    )
    # A thin light outline keeps the darker Workday bars visible on the dark card.
    theme_chart.update_traces(marker_line_color=COMPLAINT_COLOR, marker_line_width=1)
    style_chart(theme_chart, height=420)
    # bargap: space between theme groups; bargroupgap: space between the two bars in a group.
    theme_chart.update_layout(legend_traceorder="reversed", bargap=0.35, bargroupgap=0.1)

    # on_select="rerun" makes a click rerun this script and return what was clicked.
    event = st.plotly_chart(
        theme_chart, config=CHART_CONFIG, on_select="rerun", selection_mode="points"
    )

    st.caption(
        f"Not shown: {general_complaint_percent(reviews, 'UKG Pro'):.0f}% of UKG Pro's and "
        f"{general_complaint_percent(reviews, 'Workday'):.0f}% of Workday's negative reviews were "
        "general complaints that didn't name a specific issue. Themes under 1% of an app's "
        "negative reviews are grouped into Other."
    )

# When a bar is clicked, open the Reviews page filtered to that app, its theme(s), and
# negative sentiment. The filters travel in the URL as query parameters.
clicked_points = event.selection.points
if clicked_points:
    # customdata holds the custom_data columns first, then Plotly appends the hover_data
    # columns (like count), so read the first two by position.
    customdata = clicked_points[0]["customdata"]
    app_name = customdata[0]
    includes = customdata[1]
    st.switch_page(
        "views/reviews.py",
        query_params={"app": app_name, "theme": includes.split(", "), "sentiment": "negative"},
    )
