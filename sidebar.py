import streamlit as st

def render_sidebar(df_weekly_scores):
    st.sidebar.title("The Jager Crew ⚽ 2024/25")

    users = sorted(set(df_weekly_scores["player_name"]))

    # Only set a default if the key is missing AND the default is in the list
    if "selected_user" not in st.session_state:
        default_user = "Dan Coulton"
        st.session_state.selected_user = default_user if default_user in users else users[0]

    # Just bind the selectbox — let Streamlit manage it
    st.sidebar.selectbox(
        "Select your name",
        users,
        key="selected_user"
    )

    return st.session_state.selected_user