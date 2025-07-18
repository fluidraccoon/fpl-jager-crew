import streamlit as st
import pandas as pd


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
                "Winnings", format=f"£ %.2f", width=90
            ),
        }

        st.dataframe(
            df_weekly_prizes.style.apply(highlight_row, axis=1),
            hide_index=True,
            column_config=config_columns,
            use_container_width=False,
        )
