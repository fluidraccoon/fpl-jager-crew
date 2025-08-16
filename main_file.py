import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
import threading
from streamlit_javascript import st_javascript
from streamlit_pages.prizes import show_prizes_page
from streamlit_pages.jager_cup import run_cup_page
from streamlit_pages.weekly_winnings import show_weekly_winner_page
from streamlit_pages.chip_usage import show_chip_usage_page


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
        st.Page(show_prizes_page, title="Prize Fund", icon="💵"),
        st.Page(
            lambda: show_weekly_winner_page(df_weekly_scores, selected_user),
            title="Weekly Winner",
            icon="📅",
            url_path="/weekly-winner",
        ),
        st.Page(
            lambda: show_chip_usage_page(selected_user),
            title="Chip Usage",
            icon="🍟",
            url_path="/chip-usage",
        ),
        st.Page(run_cup_page, title="Jager Cup (from GW34)", icon="🏆"),
    ]

    pg = st.navigation(pages, position="top")

    pg.run()


if __name__ == "__main__":
    main()
