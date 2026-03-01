import streamlit as st
import pandas as pd
import os


@st.cache_data(ttl=60)
def load_jager_cup_data():
    """Load Jager Cup matches data with caching"""
    csv_path = "data/jager_cup_matches.csv"
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except Exception as e:
            return None
    return None


def run_cup_page():
    st.title("Jager Cup 🏆")

    # Try to load data from CSV file
    df = load_jager_cup_data()
    if df is not None:
        display_cup_matches_by_week(df)
    else:
        st.warning("Jager Cup matches will begin in GW34.")


def display_cup_matches_by_week(df):
    if df.empty:
        st.warning("Jager Cup matches will begin in GW34.")
        return

    # Convert DataFrame to match the expected format for display
    matches = []
    for _, row in df.iterrows():
        matches.append({
            "Week": row["event"],
            "Stage": row["stage"],
            "Player 1": row["entry_1_player_name"] if pd.notna(row["entry_1_player_name"]) else "",
            "Team 1": row["entry_1_team_name"],
            "Points 1": row["entry_1_points"],
            "Player 2": row["entry_2_player_name"] if pd.notna(row["entry_2_player_name"]) else "",
            "Team 2": row["entry_2_team_name"],
            "Points 2": row["entry_2_points"],
            "Winner": row["winner"],
            "Is Bye": row["is_bye"],
        })
    
    df_display = pd.DataFrame(matches)
    if df_display.empty:
        st.warning("Jager Cup matches will begin in GW34.")
        return

    # Sort by stage and week
    df_display = df_display.sort_values(["Week"]).reset_index(drop=True)
    # Create a tab for each stage (e.g., "Round of 32", "Quarter Final", etc.)
    stages = df_display["Stage"].unique().tolist()
    tabs = st.tabs(stages)
    for i, stage in enumerate(stages):
        with tabs[i]:
            df_gw = df_display[df_display["Stage"] == stage]
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
                            container_cols = st.columns([1])  # Single column for mobile
                            image = "✅ " if stage != "Final" else "🏆 "
                            st.markdown(
                                f"<div style='margin-bottom: 0.6em; line-height: 2; font-size: 1em; position: relative; top: -10px;'>"
                                f"<span style='position: absolute; left: 0%;'><b>{row['Player 1']}</b></span>"
                                f"<span style='position: absolute; left: 50%;'>{row['Points 1']}</span>"
                                f"<span style='position: absolute; left: 75%;'>{image if row['Points 1'] > row['Points 2'] else ''}</span><br>"
                                f"<span style='position: absolute; left: 0%;'><b>{row['Player 2']}</b></span>"
                                f"<span style='position: absolute; left: 50%;'>{row['Points 2']}</span>"
                                f"<span style='position: absolute; left: 75%;'>{image if row['Points 2'] > row['Points 1'] else ''}</span>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            container_cols = st.columns(
                                [2, 1, 1]
                            )  # Original layout for desktop

                            with container_cols[0]:
                                st.markdown(
                                    f"<div style='margin-bottom: 0.2em; line-height: 2; font-size: 1em;'>"
                                    f"<b>{row['Player 1']}</b><br>"
                                    f"<hr style='margin:2px 0;'>"
                                    f"<b>{row['Player 2']}</b>"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )
                            with container_cols[1]:
                                st.markdown(
                                    f"<div style='margin-bottom: 0.2em; line-height: 2.3; font-size: 1em; text-align: center;'>"
                                    f"{row['Points 1']}<br>"
                                    f"{row['Points 2']}"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )
                            with container_cols[2]:
                                if row["Points 1"] > row["Points 2"]:
                                    winner = row["Player 1"]
                                elif row["Points 2"] > row["Points 1"]:
                                    winner = row["Player 2"]
                                else:
                                    winner = None

                                image = "✅ " if stage != "Final" else "🏆 "
                                st.markdown(
                                    f"<div style='margin-bottom: 0.2em; line-height: 2.3; font-size: 1em; text-align: center;'>"
                                    f"{image if winner == row['Player 1'] else ''}<br>"
                                    f"{image if winner == row['Player 2'] else ''}"
                                    f"</div>",
                                    unsafe_allow_html=True,
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
                                unsafe_allow_html=True,
                            )
