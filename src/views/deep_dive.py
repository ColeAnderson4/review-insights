"""App deep dive: one app's complaint themes, sorted by that app's own percentages."""

import plotly.express as px
import streamlit as st

from dashboard_common import (
    APP_ORDER, CHART_CONFIG, COMPLAINT_COLOR, complaint_shares, general_complaint_percent,
    load_reviews, section_header, shared_x_range, style_chart,
)

reviews = load_reviews()

# Widgets created inside "with st.sidebar" appear in the sidebar instead of the page.
with st.sidebar:
    app_name = st.radio("App", APP_ORDER)

shares = complaint_shares(reviews, app_name)
app_negative_count = ((reviews["app_name"] == app_name) & (reviews["sentiment"] == "negative")).sum()
top_theme = shares["theme_label"].iloc[0]
top_percent = shares["percent"].iloc[0]

st.title(f"App deep dive: {app_name}")
st.caption(f"Based on {app_negative_count} negative {app_name} reviews.")

with st.container(border=True, key="card_deep_dive"):
    section_header(
        "Top complaints",
        f"{top_percent:.0f}% of {app_name}'s negative reviews are about {top_theme.lower()}.",
    )

    chart = px.bar(
        shares,
        x="percent",
        y="theme_label",
        orientation="h",
        category_orders={"theme_label": shares["theme_label"].tolist()},
        color_discrete_sequence=[COMPLAINT_COLOR],
        hover_data={"count": True, "percent": ":.1f", "includes": True, "theme_label": False},
        labels={"percent": "Share of app's negative reviews", "theme_label": "", "includes": "Theme"},
    )
    style_chart(chart, height=320, legend=False)
    # The same x-axis range for both apps, so switching apps doesn't rescale the bars.
    # bargap is the space between bars as a fraction of each slot: higher = thinner bars.
    chart.update_layout(xaxis_range=shared_x_range(reviews), bargap=0.45)
    st.plotly_chart(chart, config=CHART_CONFIG)

    st.caption(
        f"Not shown: {general_complaint_percent(reviews, app_name):.0f}% were general complaints "
        "that didn't name a specific issue. Themes under 1% are grouped into Other."
    )
