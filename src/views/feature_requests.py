"""Feature requests: the most common request themes per app, with examples."""

import streamlit as st

from dashboard_common import APP_ORDER, load_reviews, section_header

reviews = load_reviews()

# Every request summary is worded differently, so requests are grouped by theme.
requests = reviews[reviews["is_feature_request"]].sort_values("date", ascending=False)
app_totals = reviews["app_name"].value_counts()

# The most common request theme per app, for the title.
top_request = {}
for app_name in APP_ORDER:
    top_request[app_name] = requests[requests["app_name"] == app_name]["theme_label"].mode()[0]

if top_request["UKG Pro"] == top_request["Workday"]:
    request_finding = f"{top_request['UKG Pro']} is the top feature-request theme for both apps."
else:
    request_finding = (
        f"UKG Pro users most often request changes to {top_request['UKG Pro'].lower()}; "
        f"Workday users to {top_request['Workday'].lower()}."
    )

st.title("Feature requests")
st.caption(
    "Reviews the classifier marked as asking for something new or changed, grouped by "
    "theme. Examples are the newest requests in each theme."
)

with st.container(border=True, key="card_requests"):
    section_header("Requests by theme", request_finding)

    request_columns = st.columns(len(APP_ORDER))
    for column, app_name in zip(request_columns, APP_ORDER):
        app_requests = requests[requests["app_name"] == app_name]

        # head(3) keeps the 3 newest summaries, since the data is sorted newest first.
        request_table = app_requests.groupby("theme_label").agg(
            requests=("review_id", "size"),
            examples=("request_summary", lambda summaries: "; ".join(summaries.head(3))),
        )
        request_table = request_table.sort_values("requests", ascending=False).reset_index()

        column.markdown(f"**{app_name}**: {len(app_requests)} of {app_totals[app_name]:,} reviews")
        column.dataframe(
            request_table,
            hide_index=True,
            column_config={
                "theme_label": "Theme",
                "requests": "Requests",
                "examples": st.column_config.TextColumn("Example requests", width="large"),
            },
        )
