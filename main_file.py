import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
import threading
from streamlit_javascript import st_javascript
from streamlit_pages.prizes import show_prizes_page
from streamlit_pages.jager_cup import run_cup_page


def keep_alive():
    """Background thread to keep the app active"""
    while True:
        time.sleep(300)


def load_weekly_scores():
    @st.cache_data
    def load_data():
        return pd.read_csv("data/weekly_scores.csv")

    return load_data()


def initialize_session_state():
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = "Dan Coulton"

    if "keep_alive_started" not in st.session_state:
        st.session_state.keep_alive_started = True
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()


def render_sidebar(df_weekly_scores):
    """Render sidebar with persistent dropdown"""
    st.sidebar.title("The Jager Crew ⚽ 2024/25")
    user_options = sorted(set(df_weekly_scores["player_name"]))
    selected_user = st.sidebar.selectbox(
        label="Select your name",
        options=user_options,
        key="selected_user",
    )

    st.sidebar.markdown("---")

    return selected_user


def show_weekly_winner_page(df_weekly_scores, selected_user):
    """Display the weekly winner page content"""
    st.title("Weekly Winner")

    df_weekly_winner = df_weekly_scores[
        df_weekly_scores["points"]
        == df_weekly_scores.groupby("event")["points"].transform("max")
    ]
    df_weekly_winner = df_weekly_winner.sort_values(by="event")[
        ["event", "player_name", "points"]
    ]
    event_counts = df_weekly_winner.groupby("event")["player_name"].transform("count")

    # Assign £10 / number of winners for each row
    df_weekly_winner["prize"] = 10 / event_counts

    # Styling function
    def highlight_row(row):
        if row["player_name"] == selected_user:
            return ["background-color: #cce5ff"] * len(row)  # light blue
        else:
            return [""] * len(row)

    tab1, tab2 = st.tabs(["📅 Weekly Winner", "🎖️ Total Weekly Prizes"])
    with tab1:
        config_columns = {
            "event": st.column_config.NumberColumn("Gameweek"),
            "player_name": st.column_config.TextColumn("Manager"),
            "points": st.column_config.NumberColumn("Points"),
            "prize": st.column_config.NumberColumn("Winnings", format=f"£ %.2f"),
        }

        st.dataframe(
            df_weekly_winner.style.apply(highlight_row, axis=1),
            hide_index=True,
            column_config=config_columns,
            use_container_width=False,
        )
    with tab2:
        df_weekly_prizes = (
            df_weekly_winner.groupby("player_name")["prize"].sum().reset_index()
        )

        # Sort by total winnings in descending order
        df_weekly_prizes = df_weekly_prizes.sort_values(by="prize", ascending=False)

        config_columns = {
            "player_name": st.column_config.TextColumn("Manager", width="medium"),
            "prize": st.column_config.NumberColumn(
                "Winnings", format=f"£ %.2f", width="small"
            ),
        }

        st.dataframe(
            df_weekly_prizes.style.apply(highlight_row, axis=1),
            hide_index=True,
            column_config=config_columns,
            use_container_width=False,
        )


def main():
    st.set_page_config(
        page_title="The Jager Crew",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    width = st_javascript("window.innerWidth")
    if width is not None:
        st.session_state["is_mobile"] = width < 700

    df_weekly_scores = load_weekly_scores()

    initialize_session_state()
    selected_user = render_sidebar(df_weekly_scores)

    pages = [
        st.Page(show_prizes_page, title="Prize Fund", icon="🏅"),
        st.Page(
            lambda: show_weekly_winner_page(df_weekly_scores, selected_user),
            title="Weekly Winner",
            icon="🏆",
        ),
        st.Page(run_cup_page, title="Jager Cup (from GW34)", icon="⚽"),
    ]

    pg = st.navigation(pages)

    pg.run()


if __name__ == "__main__":
    main()
