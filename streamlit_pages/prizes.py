import streamlit as st
import pandas as pd


def ordinal(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def show_prizes_page():
    """Display the prizes page content side by side"""
    st.title("Prize Fund 💵")
    df = pd.read_csv("prize_fund.csv")
    col1, col2, col3 = st.columns(3)

    # Main League Prizes
    with col1:
        st.markdown("### Main League")
        main_league = df[df["category"] == "standard"]
        main_league_text = "<br>".join(
            [
                f"<b>{ordinal(row['position'])}:</b> £{row['amount']}"
                for _, row in main_league.iterrows()
            ]
        )
        st.markdown(main_league_text, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Head to Head League Prizes
    with col2:
        st.markdown("### Head to Head League")
        h2h_league = df[df["category"] == "h2h"]
        h2h_league_text = "<br>".join(
            [
                f"<b>{ordinal(row['position'])}:</b> £{row['amount']}"
                for _, row in h2h_league.iterrows()
            ]
        )
        st.markdown(h2h_league_text, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Cup League Prizes
    with col1:
        st.markdown("### Jager Cup")
        cup_league = df[df["category"] == "cup"]

        def cup_label(pos):
            if int(pos) == 1:
                return "Winner"
            else:
                return ordinal(pos)

        cup_league_text = "<br>".join(
            [
                f"<b>{cup_label(row['position'])}:</b> £{row['amount']}"
                for _, row in cup_league.iterrows()
            ]
        )
        st.markdown(cup_league_text, unsafe_allow_html=True)
        if st.session_state.get("is_mobile", False):
            st.markdown("<hr>", unsafe_allow_html=True)

    # Weekly League Prizes
    with col2:
        st.markdown("### Weekly Winner")
        weekly_league = df[df["category"] == "weekly"]
        weekly_league_text = "<br>".join(
            [f"£{row['amount']}" for _, row in weekly_league.iterrows()]
        )
        st.markdown(weekly_league_text, unsafe_allow_html=True)
