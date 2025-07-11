import streamlit as st
import pandas as pd
import requests

def run_cup_page():
    st.title("Jager Cup 🏆")
    
    url = "https://fantasy.premierleague.com/api/leagues-h2h-matches/league/2636085/?page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        display_cup_matches_by_week(data)
    else:
        st.error(f"Failed to fetch data from FPL API. Status code: {response.status_code}")

def display_cup_matches_by_week(data):
    # Parse the results into a DataFrame
    matches = []
    for match in data["results"]:
        matches.append({
            "Week": match["event"],
            "Stage": match["knockout_name"],
            "Player 1": match["entry_1_player_name"].title() if match["entry_1_player_name"] else "",
            "Team 1": match["entry_1_name"],
            "Points 1": match["entry_1_points"],
            "Player 2": match["entry_2_player_name"].title() if match["entry_2_player_name"] else "",
            "Team 2": match["entry_2_name"],
            "Points 2": match["entry_2_points"],
            "Winner": match["winner"],
            "Is Bye": match["is_bye"]
        })
    df = pd.DataFrame(matches)
    if df.empty:
        st.warning("Jager Cup matches will begin in GW34.")
        return
    
    # Sort by stage and week
    df = df.sort_values(["Week"]).reset_index(drop=True)
    # Create a tab for each stage (e.g., "Round of 32", "Quarter Final", etc.)
    stages = df["Stage"].unique().tolist()
    tabs = st.tabs(stages)
    for i, stage in enumerate(stages):
        with tabs[i]:
            df_gw = df[df["Stage"] == stage]
            # Separate byes from regular matches
            df_matches = df_gw[~df_gw["Is Bye"]]
            df_byes = df_gw[df_gw["Is Bye"]]

            cols = st.columns(3)
            week_idx = 0
            # Detect mobile state
            is_mobile = st.session_state.get("is_mobile", False)

            # Adjust layout based on mobile state
            for idx, row in df_matches.iterrows():
                with cols[week_idx % 2]:
                    with st.container(height=100):
                        if is_mobile:
                            container_cols = st.columns([2, 1, 1, 2])
                            for col in container_cols:
                                col.markdown("<style>div[data-testid='column'] { max-width: 100px; }</style>", unsafe_allow_html=True)
                        else:
                            container_cols = st.columns([2, 1, 1])  # Original layout for desktop

                        with container_cols[0]:
                            st.markdown(
                                f"<div style='margin-bottom: 0.2em; line-height: 2; font-size: 1em;'>"
                                f"<b>{row['Player 1']}</b><br>"
                                f"<hr style='margin:2px 0;'>"
                                f"<b>{row['Player 2']}</b>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        with container_cols[1]:
                            st.markdown(
                                f"<div style='margin-bottom: 0.2em; line-height: 2.3; font-size: 1em; text-align: center;'>"
                                f"{row['Points 1']}<br>"
                                f"{row['Points 2']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        with container_cols[2]:
                            if row['Points 1'] > row['Points 2']:
                                winner = row['Player 1']
                            elif row['Points 2'] > row['Points 1']:
                                winner = row['Player 2']
                            else:
                                winner = None

                            image = "✅ " if stage != "Final" else "🏆 " 
                            st.markdown(
                                f"<div style='margin-bottom: 0.2em; line-height: 2.3; font-size: 1em; text-align: center;'>"
                                f"{image if winner == row['Player 1'] else ''}<br>"
                                f"{image if winner == row['Player 2'] else ''}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                week_idx += 1

            # Display byes at the bottom, split into two columns inside column 3
            if not df_byes.empty:
                with cols[2]:
                    st.subheader("Byes")
                    bye_managers = df_byes.sort_values("Player 1")["Player 1"].tolist()
                    half = (len(bye_managers) + 1) // 2
                    bye_cols = st.columns(2)
                    for i, manager in enumerate(bye_managers):
                        with bye_cols[0 if i < half else 1]:
                            st.markdown(
                                f"<div style='margin-bottom: 0.5em; font-size: 1em;'>"
                                f"<b>{manager}</b>"
                                f"</div>",
                                unsafe_allow_html=True
                            )