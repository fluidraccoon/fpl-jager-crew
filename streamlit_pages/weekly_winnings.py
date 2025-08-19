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

    tab1, tab2, tab3 = st.tabs(["📅 Weekly Winner", "🎖️ Total Weekly Prizes", "🌟 Top 5 Finishes"])
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

    with tab3:
        st.subheader(f"🌟 {selected_user}'s Top 5 Finishes")
        
        # Find gameweeks where selected user finished in top 5
        my_top_weeks = []
        
        for event in df_completed["event"].unique():
            event_data = df_completed[df_completed["event"] == event].copy()
            event_data = event_data.sort_values("points", ascending=False)
            
            # Get the 5th highest score to determine cutoff (including ties)
            if len(event_data) >= 5:
                fifth_highest_score = event_data.iloc[4]["points"]
                top_5_data = event_data[event_data["points"] >= fifth_highest_score]
            else:
                # If less than 5 players, take all
                top_5_data = event_data
            
            # Check if selected user is in this top group
            user_in_top = top_5_data[top_5_data["player_name"] == selected_user]
            if not user_in_top.empty:
                # Add rank information
                top_5_data = top_5_data.reset_index(drop=True)
                top_5_data["rank"] = range(1, len(top_5_data) + 1)
                
                # Store this gameweek data
                my_top_weeks.append({
                    "event": event,
                    "my_rank": user_in_top.index[0] + 1,
                    "my_points": user_in_top.iloc[0]["points"],
                    "top_5_data": top_5_data
                })
        
        if my_top_weeks:
            # Sort by gameweek
            my_top_weeks.sort(key=lambda x: x["event"])
            
            top5_count = 0
            for week_data in my_top_weeks:
                top5_count += 1
                event = week_data["event"]
                my_rank = week_data["my_rank"]
                my_points = week_data["my_points"]
                top_5_data = week_data["top_5_data"]
                
                with st.expander(f"📈 Gameweek {event} - Finished #{my_rank} with {my_points} points", expanded=(top5_count==1)):
                    # Highlight function for this specific gameweek
                    def highlight_my_row(row):
                        if row["player_name"] == selected_user:
                            return ["background-color: #cce5ff"] * len(row)  # light blue
                        else:
                            return [""] * len(row)
                    
                    config_columns = {
                        "rank": st.column_config.NumberColumn("#", width=40),
                        "player_name": st.column_config.TextColumn("Manager", width=150),
                        "points": st.column_config.NumberColumn("Points", width=80),
                    }
                    
                    display_data = top_5_data[["rank", "player_name", "points"]]
                    
                    st.dataframe(
                        display_data.style.apply(highlight_my_row, axis=1),
                        hide_index=True,
                        column_config=config_columns,
                        use_container_width=False,
                        height=(len(display_data) + 1) * 35 + 3
                    )
        else:
            st.info(f"No top 5 finishes found for {selected_user} in completed gameweeks.")
