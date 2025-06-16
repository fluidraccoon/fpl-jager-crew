import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from sidebar import render_sidebar

st.set_page_config(
    page_title="The Jager Crew",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# df_weekly_scores = pd.read_csv("data/weekly_scores.csv")
@st.cache_data
def load_data():
    return pd.read_csv("data/weekly_scores.csv")

df_weekly_scores = load_data()
weekly_prize = 10

selected_user = render_sidebar(df_weekly_scores)

df_weekly_winner = df_weekly_scores[df_weekly_scores["points"] == df_weekly_scores.groupby("event")["points"].transform("max")]
df_weekly_winner = df_weekly_winner.sort_values(by="event")[["event", "player_name", "points"]]
event_counts = df_weekly_winner.groupby("event")["player_name"].transform("count")

# Assign £10 / number of winners for each row
df_weekly_winner['prize'] = 10 / event_counts

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
        use_container_width=False
    )
with tab2:
    df_weekly_prizes = df_weekly_winner.groupby("player_name")["prize"].sum().reset_index()

    # Sort by total winnings in descending order
    df_weekly_prizes = df_weekly_prizes.sort_values(by="prize", ascending=False)
    
    config_columns = {
        "player_name": st.column_config.TextColumn("Manager", width="medium"),
        "prize": st.column_config.NumberColumn("Winnings", format=f"£ %.2f", width="small"),
    }

    st.dataframe(
        df_weekly_prizes.style.apply(highlight_row, axis=1),
        hide_index=True,
        column_config=config_columns,
        use_container_width=False
    )



# df_matchup_schedule = df_matchup_schedule[df_matchup_schedule["league"]==league_selection]\
#     .drop(columns = ["league"]).reset_index(drop=True)
# df_summary_week = pd.read_csv(f"data/df_summary_week_{league_selection}.csv")
# df_summary_season = df_summary_season[df_summary_season["league"]==league_selection]\
#     .drop(columns = ["league"]).reset_index(drop=True)

# max_gameweek = max(df_matchup_schedule["gameweek"])
# # with st.sidebar:
# #     gameweek_start, gameweek_end = st.slider("Select gameweeks", 1, 2, (1, 2))
# gameweek_start = 1
# gameweek_end = 6
# df_matchup_schedule = df_matchup_schedule[
#     (df_matchup_schedule["gameweek"] >= gameweek_start) & (df_matchup_schedule["gameweek"] <= gameweek_end)
# ]

# league_size = df_matchup_schedule[df_matchup_schedule["gameweek"]==1]["gameweek"].count()

# def simulate_table():
#     # Grouping by 'season' and 'Manager' and aggregating
#     table_sim = (df_summary_week.groupby(['season', 'manager','division'], as_index=False)
#                 .agg(wins=('selected_win', 'sum'),
#                     points=('selected_pts', 'sum'),
#                     potential_wins=('selected_pp_win', 'sum'),
#                     potential_points=('selected_pp', 'sum'),
#                     upcoming=('nxt_wk_win', 'sum'))
#                 )

#     # Sorting within each group by 'Points' (descending)
#     table_sim["position"] = table_sim.sort_values(['season', 'division', 'wins', 'points'], ascending=[True, True, False, False])\
#         .groupby(['season', 'division']).cumcount() + 1

#     # Adding 'Playoff' column based on condition (if Position <= 6)
#     if league_selection == "Super Flex Keeper":
#         table_sim_wc = table_sim.copy()
#         table_sim_wc["wins"] = np.where(table_sim_wc["position"] <= 2, 0, table_sim_wc["wins"])
#         table_sim_wc["points"] = np.where(table_sim_wc["position"] <= 2, 0, table_sim_wc["points"])
#         table_sim["overall_position"] = table_sim_wc.sort_values(['season', 'wins', 'points'], ascending=[True, False, False])\
#         .groupby(['season']).cumcount() + 1
#         table_sim['playoff'] = np.where((table_sim['position'] <= 2) | (table_sim["overall_position"] <= 2), 1, 0)
#     else:
#         table_sim['playoff'] = np.where(table_sim['position'] <= (6 if league_size==12 else 4 if league_size==10 else 1), 1, 0)

#     # Adding 'Bye' column based on condition (if Position <= 2)
#     if league_selection == "Super Flex Keeper":
#         table_sim['bye'] = np.where(table_sim['position'] == 1, 1, 0)
#     else:
#         table_sim['bye'] = np.where(table_sim['position'] <= 2, 1, 0)

#     # Re-arranging again, sorting by 'Playoff' and 'PPoints' within each 'season'
#     table_sim = table_sim.sort_values(['season', 'playoff', 'potential_points'], ascending=[True, False, False])

#     # Adding 'Draft_Pos' column based on new ranking after re-arranging
#     table_sim['draft_pos'] = table_sim.groupby('season').cumcount() + 1

#     # Removing the groupby index (like ungroup in R)
#     table_sim = table_sim.reset_index(drop=True)

#     return table_sim

# def part1(df_matchup_schedule):
#     st.markdown("## Current Standings")

#     st.markdown(
#         """
#         The hunt for the playoffs as it stands. All-play is the record if all teams were to play each other every week.
#         xWins is the number of wins you would have expected so far based on the all-play record. Accuracy is the number of
#         points compared to the maximum possible points. The playoff{} % is calculated by calculating player scores 
#         since 2016 based on their rank and sampling these to give a score for each simulation. The optimal lineup is 
#         calculated and then an efficiency score is calculated to give the starting lineup score. {} different seasons have
#         been simulated using the wins to date and the remaining fixtures for each team. Strength of roster is taken into account
#         in these calculations.
#         """.format(" and bye" if league_size==12 else "", sims)
#     )

#     df_matchup_schedule["all_play"] = df_matchup_schedule.groupby("gameweek")["points"].rank("max") - 1
    
#     playoff_chances = simulate_table().groupby(["manager"]).agg(
#         playoff=("playoff", "mean"),
#         bye=("bye", "mean")
#     ).reset_index()

#     df_standings = df_matchup_schedule.groupby(["manager"]).agg(
#         wins=("win", "sum"),
#         points=("points", "sum"),
#         pp_points=("pp_points", "sum"),
#         all_play=("all_play", "sum"),
#     ).reset_index()
#     df_standings = df_standings.sort_values(by=["wins", "points"], ascending=False).reset_index(drop=True)
#     df_standings["all_play_display"] = df_standings["all_play"].apply(lambda x: f"{x:.0f}") + "-" + (gameweek_end * (league_size - 1) - df_standings["all_play"]).apply(lambda x: f"{x:.0f}") 
#     df_standings["xwins"] = round(df_standings["all_play"] / (league_size - 1), 1)
#     df_standings["accuracy"] = df_standings["points"] / df_standings["pp_points"] * 100
#     df_standings = df_standings.drop(columns=["pp_points", "all_play"])
#     df_standings = df_standings.merge(playoff_chances, on="manager", how="left")
#     df_standings.index = df_standings.index + 1
    
    

#     def set_background_color(x, league_size):
#         if league_size == 12:
#             color = "#0080ff" if x.name <=2 else "#79c973" if x.name <=6 else "#ff6666"
#         elif league_size == 10:
#             color = "#79c973" if x.name <=4 else "#ff6666"

#         return [f"background-color: {color}" for i in x]
    
#     config_columns = {
#         "manager": st.column_config.TextColumn("Manager", help="Username of team manager"),
#         "wins": st.column_config.NumberColumn("Wins", help="Number of wins so far"),
#         "points": st.column_config.NumberColumn("Points", help="Number of points so far"),
#         "all_play_display": st.column_config.TextColumn("All-Play", help="Wins and losses if you played every team each week"),
#         "xwins": st.column_config.TextColumn("xWins", help="Expected number of wins based on the all-play record"),
#         "accuracy": st.column_config.ProgressColumn("Accuracy", help="Accuracy of team selection compared to maximum points", format="%.1f %%", min_value=0, max_value=100),
#         "playoff": st.column_config.NumberColumn("Playoff %", help="% chance of team making the playoffs"),
#         "bye": st.column_config.NumberColumn("Bye %", help="% chance of team getting a first-round bye"),
#     }
#     if league_size==10:
#         del config_columns["bye"]
#         df_standings = df_standings.drop(columns=["bye"])

#     st.dataframe(
#         df_standings.style\
#             .format("{:.0f}", subset=["wins"])\
#             .format("{:.2f}", subset=["points"])\
#             .format("{:.1f}", subset=["xwins"])\
#             .format("{:.1%}", subset=["accuracy", "playoff", "bye"] if league_size==12 else ["accuracy", "playoff"])\
#             .apply(lambda x: set_background_color(x, league_size), axis=1)\
#             .apply(lambda x: [f"color: white" for i in x], axis=1),
#         column_config=config_columns,
#         height=35*len(df_standings)+38
#     )

#     return df_standings

# def part2(df_standings):
#     df_standings.loc[df_standings.xwins > df_standings.wins , 'angle'] = 'angle-cat-one'
#     df_standings.loc[df_standings.xwins <= df_standings.wins , 'angle'] = 'angle-cat-two'
#     df_standings['manager'] = pd.Categorical(df_standings['manager'], categories=df_standings.sort_values(by=['wins', 'xwins'], ascending=False)['manager'])

#     base = alt.Chart(df_standings).encode(
#         y=alt.Y('manager:N', sort=alt.EncodingSortField(field='wins', op='sum', order='descending'), title=None),
#         color=alt.Color('manager:N', legend=None)
#     )

#     win_circle = base.mark_point(filled=True, size=80, opacity=0.8).encode(
#         x=alt.X('wins:Q', title='Wins', scale=alt.Scale(nice=False),
#                 axis=alt.Axis(tickCount=(df_standings['wins'].max() - df_standings['wins'].min() + 1), tickMinStep=1)),
#         tooltip=alt.value(None)
#     )

#     # Segments between Wins and xWins
#     segments = base.mark_rule(opacity=0.75, strokeWidth=2, strokeCap='round').encode(
#         x='wins:Q',
#         x2='xwins:Q'
#     )

#     xwin_arrow = base.mark_point( 
#         shape='triangle', 
#         size=100, 
#         filled=True, 
#         opacity=0.75
#     ).encode(
#         x='xwins:Q',
#         angle=alt.Angle('angle:N', scale=alt.Scale(domain=['angle-cat-one', 'angle-cat-two'], range=[90, 270])),
#         tooltip=alt.value(None)
#     )

#     chart = (segments + win_circle + xwin_arrow).encode(tooltip=[
#         alt.Tooltip("wins", title="Wins"),
#         alt.Tooltip("xwins", title="xWins"),
#         alt.Tooltip("manager", title="Manager")
#     ]).properties(
#         title={
#             'text': 'Schedule Luck',
#             'subtitle': 'Difference between H2H Wins and xWins based on All-Play. The arrow shows where you deserve to be.'
#         }
#     ).configure_axis(grid=False).configure_title(anchor='start')
    
#     st.markdown(
#         """
#         ## Wins over Expectation
#         Wins over expectation (WOE) looks at the relationship between actual wins and all-play wins.\
#         This shows how lucky or unlucky a team has been with the schedule.
#         """
#     )
    
#     luck_col1, luck_col2, luck_col3 = st.columns([2, 0.3, 0.7])
    
#     with luck_col1:
#         st.altair_chart(chart, use_container_width=True)
        
#     with luck_col3:
#         for i in range(4):
#             st.write("")
#         df_standings["WOE"] = df_standings["wins"] - df_standings["xwins"]
#         max_woe_managers = df_standings[df_standings["WOE"]==df_standings["WOE"].max()]["manager"].tolist()
#         min_woe_managers = df_standings[df_standings["WOE"]==df_standings["WOE"].min()]["manager"].tolist()
#         st.write(
#             """
#             <style>
#             [data-testid="stMetricDelta"] svg {
#                 display: none;
#             }
#             [data-testid="stMetricValue"] {
#                 font-size: 15px;
#             }
#             </style>
#             """,
#             unsafe_allow_html=True,
#         )

#         st.metric('Luckiest Manager(s) 🍀', value=', '.join(max_woe_managers), delta=f"{round(df_standings["WOE"].max(), 1)} more wins than expected", delta_color='normal')
#         st.metric('Unluckiest Manager(s) 🐈‍⬛', value=', '.join(min_woe_managers), delta=f"{-round(df_standings["WOE"].min(), 1)} fewer wins than expected", delta_color='inverse')

# df_standings = part1(df_matchup_schedule)
# part2(df_standings)

# def part3(df_summary_season):
#     st.markdown(
#         """
#         ## Win Projections
#         The following chart shows the distribution of total expected wins over the season. Any wins so far
#         have been included in the calculation, and you would expect the spread to reduce as the season progresses
#         and the win totals become more certain.
#         """
#     )
    
#     step = 20
#     overlap = 0
#     # chart_width = 400
    
#     chart = alt.Chart(df_summary_season, height=step).transform_joinaggregate(
#         mean_of_metric='mean(h2h_wins)', groupby=['manager']
#     ).transform_bin(
#         'binned_wins', 'h2h_wins', bin=alt.Bin(step=1, extent=[0, max_gameweek])
#     ).transform_aggregate(
#         value='count()', groupby=['manager', 'mean_of_metric', 'binned_wins']
#     ).transform_impute(
#         impute='value', groupby=['manager', 'mean_of_metric'], key='binned_wins', value=0
#     ).mark_area(
#         interpolate='monotone',
#         fillOpacity=0.8,
#         stroke='lightgray',
#         strokeWidth=0.5
#     ).encode(
#         alt.X("binned_wins:Q", bin="binned", title="Season Wins"),
#         alt.Y("value:Q", scale=alt.Scale(range=[step, -step * overlap]), axis=None),
#         alt.Fill("mean_of_metric:Q", legend=None, scale=alt.Scale(scheme="redyellowgreen")),
#         tooltip=[alt.Tooltip("mean_of_metric:Q", title="Average Expected Wins")]
#     ).facet(
#         row=alt.Row(
#             'manager:N',
#             title=None,
#             header = alt.Header(labelAngle=0, labelAlign='left'),
#             sort=alt.SortField(field='mean_of_metric', order='descending')
#         )
#     ).properties(
#         title={
#             'text': f'Distribution of Season Win Totals - {sims} Simulated Seasons',
#             'subtitle': f'{league_selection}'
#         },
#         bounds='flush'
#     ).configure_facet(
#         spacing=0
#     ).configure_view(
#         stroke=None
#     )
    
#     chart

# def part4(df_summary_season):
#     st.markdown(
#         """
#         ## Projected Season Rank
#         Using the win totals from the chart above, the following chart shows the likelihood of each team finishing in a given position.
#         """
#     )
#     # Group by season, arrange, and mutate Position
#     df_summary_season['position'] = df_summary_season.groupby('season').apply(
#         lambda x: (x['h2h_wins'] + x['points_for']/10000).rank(method='first', ascending=False)
#     ).reset_index(drop=True)
    
#     df_summary_season['avg_position'] = df_summary_season.groupby('manager')['position'].transform('mean')
#     manager_order = df_summary_season.groupby('manager')['avg_position'].mean().reset_index().sort_values('avg_position')
    
#     # Step 2: Create Altair Chart
#     chart2 = alt.Chart(df_summary_season).mark_bar().encode(
#         x=alt.X('manager:N', axis=None, sort=alt.Sort(manager_order['manager'].tolist())),
#         y=alt.Y('probability:Q', axis=None),
#         color=alt.Color('manager:N', legend=alt.Legend(
#             title="Manager",
#             orient="right"
#         ), sort=manager_order['manager'].tolist(), scale=alt.Scale(scheme='paired')),
#         tooltip=[
#             alt.Tooltip("manager:N", title="Manager"),
#             alt.Tooltip("probability:Q", title="Probability (%)", format=".1f")
#         ]
#     ).transform_aggregate(
#         count='count()',  # Aggregate to count the number of rows
#         groupby=['manager']  # Group by 'category'
#     ).transform_calculate(
#         probability=f'datum.count / {sims} * 100'  # Calculate count()/1000
#     ).properties(
#         width=100,
#         height=60
#     ).facet(
#         facet=alt.Facet('position:Q', title='Position'),
#         columns=4,
#         spacing=10
#     ).configure_axis(
#         labelAngle=0
#     ).configure_view(
#         stroke=None
#     ).properties(
#         title={
#             'text': [f'Final Season Rank - {sims} Simulated Seasons'],
#             'subtitle': [f'{league_selection}'],
#             'anchor': 'start',
#             'fontSize': 16
#         }
#     )
    
#     chart2

# part3(df_summary_season)
# part4(df_summary_season)

# df_summary_week_selector = df_summary_week[['season',"matchup_id","roster_id","opponent_id","team_score","opponent_score",'manager',"week",'division','selected_win','selected_pts']]

# # st.dataframe(df_summary_week_selector)

# df_remaining_matchups = df_summary_week_selector[df_summary_week_selector["week"] > gameweek_end]
# df_remaining_matchups = df_remaining_matchups[["matchup_id","week","manager"]].drop_duplicates()

# df_remaining_matchups['idx'] = df_remaining_matchups.groupby(['matchup_id',"week"]).cumcount()
# df_remaining_matchups_wide = df_remaining_matchups.pivot(index=["matchup_id","week"], columns="idx", values="manager").reset_index()
# df_remaining_matchups_wide["adjusted_winner"] = None

# # Fixture result selector
# st.markdown(
#     """
#     ## Playoff Scenarios
#     Select the outcomes of the remaining games this season to understand how your playoff chances change with
#     the outcomes of each matchup.
#     """
# )

# def clear_all():
#     for i in range(0, len(df_remaining_matchups_wide)):
#         st.session_state[f'radio_{i}'] = None
#     return

# placeholders = {}
# for week in df_remaining_matchups["week"].unique():
#     df_remaining_matchups_wide_week = df_remaining_matchups_wide[df_remaining_matchups_wide["week"] == week]
#     st.markdown("""##### Week {}""".format(week))
#     cols = st.columns(3)

#     week_idx = 0 # index needs to be unique overall but need consecutive for weeks to get in right columns
#     for idx, row in df_remaining_matchups_wide_week.iterrows():
#         with cols[week_idx % 3]:
#             with st.container(height=85):
#                 container_cols = st.columns([3, 1])
#                 with container_cols[0]:
#                     winner = st.radio("Select a Winner", index=None, options=[row[0], row[1]], key=f"radio_{idx}", horizontal=False, label_visibility="collapsed")
#                 with container_cols[1]:
#                     placeholder1 = st.empty()  # Placeholder for the first percentage
#                     placeholder2 = st.empty()  # Placeholder for the second percentage
#                     placeholders[idx] = (placeholder1, placeholder2)
#         df_remaining_matchups_wide.at[idx, 'adjusted_winner'] = winner
        
#         week_idx += 1

# st.button("Clear all", on_click=clear_all)

# df_summary_week_new = df_summary_week.merge(df_remaining_matchups_wide[["matchup_id", "week", "adjusted_winner"]], on=["matchup_id","week"], how="left")
# df_summary_week_new["adjusted_win"] = np.where(
#     df_summary_week_new["adjusted_winner"].isna(), df_summary_week_new["selected_win"], np.where(
#         df_summary_week_new["adjusted_winner"] == df_summary_week_new["manager"], 1, 0
#     )
# )

# def calculate_adjusted_playoff_chance(df):
#     table_sim = (df.groupby(['season', 'manager','division'], as_index=False).agg(
#         wins=('adjusted_win', 'sum'),
#         points=('selected_pts', 'sum')
#     ))

#     # Sorting within each group by 'Points' (descending)
#     table_sim["position"] = table_sim.sort_values(['season', 'division', 'wins', 'points'], ascending=[True, True, False, False])\
#         .groupby(['season', 'division']).cumcount() + 1

#     # Adding 'Playoff' column based on condition (if Position <= 6)
#     if league_selection == "Super Flex Keeper":
#         table_sim_wc = table_sim.copy()
#         table_sim_wc["wins"] = np.where(table_sim_wc["position"] <= 2, 0, table_sim_wc["wins"])
#         table_sim_wc["points"] = np.where(table_sim_wc["position"] <= 2, 0, table_sim_wc["points"])
#         table_sim["overall_position"] = table_sim_wc.sort_values(['season', 'wins', 'points'], ascending=[True, False, False])\
#         .groupby(['season']).cumcount() + 1
#         table_sim['playoff'] = np.where((table_sim['position'] <= 2) | (table_sim["overall_position"] <= 2), 1, 0)
#     else:
#         table_sim['playoff'] = np.where(table_sim['position'] <= (6 if league_size==12 else 4 if league_size==10 else 1), 1, 0)

#     # Adding 'Bye' column based on condition (if Position <= 2)
#     if league_selection == "Super Flex Keeper":
#         table_sim['bye'] = np.where(table_sim['position'] == 1, 1, 0)
#     else:
#         table_sim['bye'] = np.where(table_sim['position'] <= 2, 1, 0)
    
#     table_sim_new = table_sim.groupby(["manager"]).agg(
#             playoff=("playoff", "mean"),
#             bye=("bye", "mean")
#         ).reset_index()
    
#     if league_size == 10:
#         table_sim_new.drop("bye", axis=1)
    
#     return table_sim_new


# playoff_chances_fields = ["manager", "playoff", "bye"] if "bye" in df_standings else ["manager", "playoff"]
# adjusted_playoff_chances = calculate_adjusted_playoff_chance(df_summary_week_new).merge(df_standings[playoff_chances_fields], on="manager", how="left", suffixes=("_adjusted", "_original"))
# table_cols = ["manager", "playoff_original", "playoff_adjusted"] + (["bye_original", "bye_adjusted"] if league_size==12 else [])
# adjusted_playoff_chances = adjusted_playoff_chances[table_cols]

# st.markdown("""##### Adjusted Playoff Chances""")
# config_columns = {
#     "manager": st.column_config.TextColumn("Manager", help="Username of team manager"),
#     "playoff_original": st.column_config.NumberColumn("Current Playoff %", help="% chance of team making the playoffs"),
#     "playoff_adjusted": st.column_config.NumberColumn("Adjusted Playoff %", help="% chance of team making the playoffs after adjusting wins above"),
#     "bye_original": st.column_config.NumberColumn("Current Bye %", help="% chance of team getting a bye"),
#     "bye_adjusted": st.column_config.NumberColumn("Adjusted Bye %", help="% chance of team getting a bye after adjusting wins above"),
# }
# if league_size==10:
#     del config_columns["bye_original"]
#     del config_columns["bye_adjusted"]
#     # table_sim_new = table_sim_new.drop(columns=["bye"])
    
# def set_background_color(x, league_size):
#     if league_size == 12:
#         color = "#0080ff" if x.name <=2 else "#79c973" if x.name <=6 else "#ff6666"
#     elif league_size == 10:
#         color = "#79c973" if x.name <=4 else "#ff6666"

#     return [f"background-color: {color}" for i in x]

# def apply_padding(column):
#     # Apply padding-right if the column is in the target list
#     return ['padding-right: 30px;' for i in column]

# columns_to_pad = ["manager"]


# st.dataframe(
#     adjusted_playoff_chances.sort_values(by=["bye_original", "playoff_original"] if league_size==12 else ["playoff_original"], ascending=False).style\
#         # .set_table_styles(
#         #     [{'selector': 'td', 'props': [('padding-left', '20px'), ('padding-right', '20px')]}]
#         # )
#         # .apply(lambda x: set_background_color(x, league_size), axis=1)\
#         # .apply(lambda x: [f"border: 2px solid black" for i in x], axis=1)\
#         .apply(lambda x: [f"padding-left: 20px" for i in x], axis=1)\
#         .format("{:.1%}", subset=["playoff_adjusted", "playoff_original", "bye_original", "bye_adjusted"] if league_size==12 else ["playoff_original", "playoff_adjusted"]),
#         # .apply(lambda x: [f"color: white" for i in x], axis=1),
#     column_config=config_columns,
#     height=35*len(df_standings)+38,
#     hide_index = True
# )

# def calculate_playoff_percentage_change_by_fixture(df, week, winner, loser):
#     df_adjusted = df.copy()
#     df_adjusted.loc[(df['week'] == week) & (df_adjusted['manager'].isin([winner, loser])), 'adjusted_winner'] = winner
#     df_adjusted["adjusted_win"] = np.where(
#         df_adjusted["adjusted_winner"].isna(), df_adjusted["selected_win"], np.where(
#             df_adjusted["adjusted_winner"] == df_adjusted["manager"], 1, 0
#         )
#     )
#     df_summary = calculate_adjusted_playoff_chance(df_adjusted)
    
#     return df_summary

# df_adjusted_summary_week = df_summary_week_new[["season", "division", "manager", "week", "adjusted_winner", "selected_win", "selected_pts"]]

# percentage_changes = {}
# for week in df_remaining_matchups["week"].unique():
#     df_remaining_matchups_wide_week = df_remaining_matchups_wide[df_remaining_matchups_wide["week"] == week]

#     week_idx = 0 # index needs to be unique overall but need consecutive for weeks to get in right columns
#     for idx, row in df_remaining_matchups_wide_week.iterrows():
#         calculate_playoff_percentage_change_by_fixture(df_adjusted_summary_week, week, row[0], row[1])
        
#         percentage1 = calculate_playoff_percentage_change_by_fixture(df_adjusted_summary_week, week, row[0], row[1])
#         percentage1 = percentage1[percentage1["manager"]==user_selection]["playoff"].iloc[0]
#         percentage2 = calculate_playoff_percentage_change_by_fixture(df_adjusted_summary_week, week, row[1], row[0])
#         percentage2 = percentage2[percentage2["manager"]==user_selection]["playoff"].iloc[0]
        
#         percentage_changes[idx] = (percentage1, percentage2)
        
#         week_idx += 1

#         # percentage = 0.2
#         # current_percentage = adjusted_playoff_chances[adjusted_playoff_chances["manager"]==user_selection]["playoff_adjusted"].iloc[0]
#         # percentage = (percentage1[percentage1["manager"]==user_selection]["playoff"].iloc[0] - current_percentage) * 100
#         # second_percentage = (percentage2[percentage2["manager"]==user_selection]["playoff"].iloc[0] - current_percentage) * 100
        
#         # placeholder1, placeholder2 = placeholders[idx]
        
#         # if percentage < 0:
#         #     arrow = "&#x2193;"  # Down arrow for negative
#         #     color = "red"
#         # elif percentage > 0:
#         #     arrow = "&#x2191;"  # Up arrow for positive
#         #     color = "green"
#         # else:
#         #     arrow = "&#x2192;"
#         #     color = "grey"

#         # # Update the placeholder with percentage and global total wins
#         # placeholder1.markdown(
#         #     f"<div style='text-align: right; color:{color};'>{percentage:.1f}% {arrow}</div>", 
#         #     unsafe_allow_html=True
#         # )
        
#         # if second_percentage < 0:
#         #     second_arrow = "&#x2193;"  # Down arrow for negative
#         #     second_color = "red"
#         # elif second_percentage > 0:
#         #     second_arrow = "&#x2191;"  # Up arrow for positive
#         #     second_color = "green"
#         # else:
#         #     second_arrow = "&#x2192;"
#         #     second_color = "grey"

#         # # Second row: Display the second percentage below the first one
#         # placeholder2.markdown(
#         #     f"<div style='text-align: right; color:{second_color};'>{second_percentage:.1f}% {second_arrow}</div>", 
#         #     unsafe_allow_html=True
#         # )

# # Now, update all the placeholders in one go
# for idx, (percentage1, percentage2) in percentage_changes.items():
#     current_percentage = adjusted_playoff_chances[adjusted_playoff_chances["manager"] == user_selection]["playoff_adjusted"].iloc[0]
    
#     # Calculate the difference from the current playoff chance
#     percentage_change_1 = (percentage1 - current_percentage) * 100
#     percentage_change_2 = (percentage2 - current_percentage) * 100
    
#     # Select arrow and color for percentage 1
#     if percentage_change_1 < 0:
#         arrow1 = "&#x2193;"  # Down arrow for negative
#         color1 = "red"
#     elif percentage_change_1 > 0:
#         arrow1 = "&#x2191;"  # Up arrow for positive
#         color1 = "green"
#     else:
#         arrow1 = "&#x2192;"
#         color1 = "grey"

#     # Select arrow and color for percentage 2
#     if percentage_change_2 < 0:
#         arrow2 = "&#x2193;"  # Down arrow for negative
#         color2 = "red"
#     elif percentage_change_2 > 0:
#         arrow2 = "&#x2191;"  # Up arrow for positive
#         color2 = "green"
#     else:
#         arrow2 = "&#x2192;"
#         color2 = "grey"

#     # Get the placeholders for this matchup
#     placeholder1, placeholder2 = placeholders[idx]

#     # Update the first placeholder with percentage change 1
#     placeholder1.markdown(
#         f"<div style='text-align: right; color:{color1};'>{percentage_change_1:.1f}% {arrow1}</div>", 
#         unsafe_allow_html=True
#     )

#     # Update the second placeholder with percentage change 2
#     placeholder2.markdown(
#         f"<div style='text-align: right; color:{color2};'>{percentage_change_2:.1f}% {arrow2}</div>", 
#         unsafe_allow_html=True
#     )
