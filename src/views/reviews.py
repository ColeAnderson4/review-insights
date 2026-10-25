"""Read the reviews: filter by app, theme, sentiment, star rating, and text search."""

import streamlit as st

from dashboard_common import APP_ORDER, SENTIMENT_ORDER, THEME_LABELS, load_reviews

PAGE_SIZE = 20       # reviews shown at first, and added by each "Load more" click
MIN_WORDS = 5        # reviews shorter than this are hidden unless the toggle is on
APP_OPTIONS = ["All apps"] + APP_ORDER

reviews = load_reviews()

# Filters can arrive in the URL, e.g. ?app=Workday&theme=login_auth&sentiment=negative,
# when someone clicks a bar on the Overview. They become the filters' starting values.
url_app = st.query_params.get("app")
url_themes = st.query_params.get_all("theme")
url_sentiments = st.query_params.get_all("sentiment")

if url_app in APP_OPTIONS:
    app_index = APP_OPTIONS.index(url_app)
else:
    app_index = 0
default_themes = [THEME_LABELS[theme] for theme in url_themes if theme in THEME_LABELS]

# Default to negative reviews unless the URL asks for something else.
default_sentiments = [sentiment for sentiment in url_sentiments if sentiment in SENTIMENT_ORDER]
if not default_sentiments:
    default_sentiments = ["negative"]

# ---------------------------------------------------------------------------
# Sidebar filters. An empty multiselect means "no filter".
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    app_choice = st.selectbox("App", APP_OPTIONS, index=app_index)
    theme_choice = st.multiselect(
        "Theme", sorted(THEME_LABELS.values()), default=default_themes, placeholder="All themes"
    )
    sentiment_choice = st.multiselect(
        "Sentiment", SENTIMENT_ORDER, default=default_sentiments, placeholder="All sentiments"
    )
    lowest_rating, highest_rating = st.slider("Star rating", 1, 5, (1, 5))
    search = st.text_input("Search review text")
    show_short = st.toggle(f"Show reviews under {MIN_WORDS} words", value=False)

# ---------------------------------------------------------------------------
# Apply each filter in turn.
# ---------------------------------------------------------------------------
matches = reviews
if app_choice != "All apps":
    matches = matches[matches["app_name"] == app_choice]
if theme_choice:
    matches = matches[matches["theme_label"].isin(theme_choice)]
if sentiment_choice:
    matches = matches[matches["sentiment"].isin(sentiment_choice)]
matches = matches[matches["rating"].between(lowest_rating, highest_rating)]
if search:
    # regex=False treats the search as plain text, so characters like "?" or "(" are safe.
    matches = matches[matches["text"].str.contains(search, case=False, regex=False)]

# Count short reviews before hiding them, so the caption can say how many are hidden.
is_short = matches["word_count"] < MIN_WORDS
short_count = is_short.sum()
if not show_short:
    matches = matches[~is_short]

# Longest first: longer reviews usually explain the problem. Newest breaks ties.
matches = matches.sort_values(["word_count", "date"], ascending=[False, False])

# ---------------------------------------------------------------------------
# "Load more" paging. Reset to the first page whenever a filter changes.
# ---------------------------------------------------------------------------
current_filters = (
    app_choice, tuple(theme_choice), tuple(sentiment_choice),
    lowest_rating, highest_rating, search, show_short,
)
if st.session_state.get("review_filters") != current_filters:
    st.session_state["review_filters"] = current_filters
    st.session_state["reviews_shown"] = PAGE_SIZE


def load_more():
    # A button callback runs before the script reruns, so the new count is used right away.
    st.session_state["reviews_shown"] += PAGE_SIZE


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
st.title("Read the reviews")

if len(matches) == 0:
    st.info("No reviews match these filters.")
else:
    shown = min(len(matches), st.session_state["reviews_shown"])
    st.subheader(f"{len(matches):,} matching reviews")

    caption = f"Showing {shown} of {len(matches):,}, longest first."
    if short_count > 0 and not show_short:
        caption += f" {short_count:,} reviews under {MIN_WORDS} words are hidden."
    st.caption(caption)

    for _, review in matches.head(shown).iterrows():
        # Keys must be unique on the page, hence the review_id.
        with st.container(border=True, key=f"card_review_{review['review_id']}"):
            stars = "★" * review["rating"] + "☆" * (5 - review["rating"])
            # Details line in muted caption text, so the review itself stands out.
            st.caption(
                f"{stars} · {review['date']:%b %-d, %Y} · {review['app_name']} · "
                f"{review['theme_label']} · {review['sentiment']}"
            )
            # st.text, not st.markdown: review text shouldn't be rendered as Markdown.
            st.text(review["text"])

    if shown < len(matches):
        st.button(f"Load {min(PAGE_SIZE, len(matches) - shown)} more", on_click=load_more)
