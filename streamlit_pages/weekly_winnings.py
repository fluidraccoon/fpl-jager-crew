import streamlit as st
import pandas as pd
import os


def get_finished_gameweeks():
    """Get list of finished gameweeks from the gameweek info CSV."""
    try:
        if os.path.exists("data/gameweek_info.csv"):
            gw_info = pd.read_csv("data/gameweek_info.csv")
            if not gw_info.empty and "finished_events" in gw_info.columns:
                finished_str = gw_info["finished_events"].iloc[0]
                # Convert to string to handle numpy types and NaN values
                finished_str = str(finished_str) if pd.notna(finished_str) else ""
                if finished_str.strip() and finished_str.strip() != "nan":
                    return [int(x) for x in finished_str.split(",")]
                else:
                    # Empty string means no finished gameweeks yet - this is valid
                    return []
        # If file doesn't exist, return None to indicate we couldn't determine status
        return None
    except Exception as e:
        st.warning(f"Could not load gameweek info: {e}")
        return None


def show_weekly_winner_page(df_weekly_scores, selected_user):
    """Display the weekly winner page content"""
    st.title("Weekly Winner")

    # Get list of finished gameweeks
    finished_gameweeks = get_finished_gameweeks()
    
    # Handle different cases
    if finished_gameweeks is None:
        # Could not determine gameweek status
        st.warning("Could not determine which gameweeks are finished. Showing all data.")
        df_completed = df_weekly_scores
    elif len(finished_gameweeks) == 0:
        # No gameweeks are finished yet
        st.info("No completed gameweeks yet. Weekly winners will appear once gameweeks are finished.")
        return
    else:
        # Some gameweeks are finished
        if len(finished_gameweeks) == 1:
            st.info(f"Showing winners for completed gameweek: {finished_gameweeks[0]}")
        else:
            st.info(f"Showing winners for completed gameweeks: 1-{max(finished_gameweeks)}")
        df_completed = df_weekly_scores[df_weekly_scores["event"].isin(finished_gameweeks)]
        if df_completed.empty:
            st.info("No data available for completed gameweeks.")
            return

    df_weekly_winner = df_completed[
        df_completed["points"]
        == df_completed.groupby("event")["points"].transform("max")
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
            "player_name": st.column_config.TextColumn("Manager", width=150),
            "prize": st.column_config.NumberColumn(
                "Winnings", format=f"£ %.2f", width=80
            ),
        }

        st.dataframe(
            df_weekly_prizes.style.apply(highlight_row, axis=1),
            hide_index=True,
            column_config=config_columns,
            use_container_width=False,
        )
