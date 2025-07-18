import streamlit as st
import pandas as pd


def load_chip_usage():
    """Load chip usage data with caching"""
    @st.cache_data
    def load_data():
        try:
            return pd.read_csv("data/chip_usage.csv")
        except FileNotFoundError:
            st.error("Chip usage data not found. Please run initial_setup.py first.")
            return pd.DataFrame()
    
    return load_data()


def load_weekly_scores():
    """Load weekly scores data with caching"""
    @st.cache_data
    def load_data():
        try:
            return pd.read_csv("data/weekly_scores.csv")
        except FileNotFoundError:
            st.error("Weekly scores data not found. Please run initial_setup.py first.")
            return pd.DataFrame()
    
    return load_data()


def show_chip_usage_page(selected_user):
    """Display the chip usage page content"""
    st.title("Chip Usage Analysis")
    
    df_chips = load_chip_usage()
    df_weekly_scores = load_weekly_scores()
    
    if df_chips.empty:
        st.warning("No chip usage data available.")
        return
    
    # Create chip display mapping
    chip_mapping = {
        'wildcard': '🃏 Wildcard',
        'freehit': '🎯 Free Hit', 
        'bboost': '🚀 Bench Boost',
        '3xc': '3️⃣ Triple Captain',
    }
    
    # Map chip names for display
    df_chips['chip_display'] = df_chips['chip'].map(chip_mapping)
    df_chips['chip_display'] = df_chips['chip_display'].fillna(df_chips['chip'])
    
    # Filter out "manager" chip as it's not a real FPL chip
    df_chips = df_chips[df_chips['chip'] != 'manager']
    
    # Styling function
    def highlight_row(row):
        if row["player_name"] == selected_user:
            return ["background-color: #cce5ff"] * len(row)  # light blue
        else:
            return [""] * len(row)
    
    tab1, tab2 = st.tabs(["🎯 Chip Summary", "📈 Chip Timeline"])
    
    with tab1:
        st.subheader("Chip Usage Summary by Manager")
        
        # Count chips used by each player - pivot to get chips as columns
        chip_summary = df_chips.groupby(['player_name', 'chip_display']).size().unstack(fill_value=0)
        
        # Add total chips column for sorting only
        chip_cols = list(chip_summary.columns)
        chip_summary['Total Chips'] = chip_summary[chip_cols].sum(axis=1)
        
        # Reset index to make manager names a regular column with proper header
        chip_summary = chip_summary.reset_index()
        chip_summary = chip_summary.rename(columns={'player_name': 'Manager'})
        
        # Add total points column
        if not df_weekly_scores.empty:
            total_points = df_weekly_scores.groupby('player_name')['total_points'].max().reset_index()
            total_points = total_points.rename(columns={'player_name': 'Manager'})
            chip_summary = chip_summary.merge(total_points, on='Manager', how='left')
            chip_summary['total_points'] = chip_summary['total_points'].fillna(0).astype(int)
        else:
            chip_summary['total_points'] = 0
        
        # Sort by total points (descending) and add rank
        chip_summary = chip_summary.sort_values('total_points', ascending=False)
        chip_summary['Rank'] = range(1, len(chip_summary) + 1)
        
        # Drop the temporary Total Chips column
        chip_summary = chip_summary.drop('Total Chips', axis=1)
        
        # Reorder columns to put Rank first, then Manager, then Total Points
        chip_cols = [col for col in chip_summary.columns if col not in ['Rank', 'Manager', 'total_points']]
        chip_summary = chip_summary[['Rank', 'Manager', 'total_points'] + chip_cols]
        
        # Convert numbers to green tick emojis (exclude Rank, Manager and total_points columns)
        for col in chip_summary.columns:
            if col not in ['Rank', 'Manager', 'total_points']:
                def format_ticks(x):
                    if x == 0:
                        return ''
                    else:
                        return '✅' * x
                
                chip_summary[col] = chip_summary[col].apply(format_ticks)
        
        # Create column configuration
        config_columns = {
            'Rank': st.column_config.NumberColumn("Rank", width=60),
            'Manager': st.column_config.TextColumn("Manager", width=150),
            'total_points': st.column_config.NumberColumn("Total Points", width=100)
        }
        for col in chip_summary.columns:
            if col not in ['Rank', 'Manager', 'total_points']:
                config_columns[col] = st.column_config.TextColumn(col, width=120)
        
        # Create styling function for summary
        def highlight_summary_row(row):
            if row["Manager"] == selected_user:
                return ["background-color: #cce5ff"] * len(row)  # light blue
            else:
                return [""] * len(row)
        
        st.dataframe(
            chip_summary.style.apply(highlight_summary_row, axis=1),
            hide_index=True,
            column_config=config_columns,
            use_container_width=False,
        )
    
    with tab2:
        st.subheader("Chip Usage Timeline")
        
        # Create a timeline chart
        if not df_chips.empty:
            # Count chips used per gameweek
            timeline_data = df_chips.groupby(['event', 'chip_display']).size().reset_index(name='count')
            
            # Create a chart showing chip usage over time
            import altair as alt
            
            chart = alt.Chart(timeline_data).mark_bar().encode(
                x=alt.X('event:O', title='Gameweek'),
                y=alt.Y('count:Q', title='Number of Chips Used'),
                color=alt.Color('chip_display:N', title='Chip Type'),
                tooltip=[
                    alt.Tooltip('event:O', title='Gameweek'),
                    alt.Tooltip('chip_display:N', title='Chip'),
                    alt.Tooltip('count:Q', title='Count')
                ]
            ).properties(
                width=600,
                height=400,
                title='Chip Usage by Gameweek'
            )
            
            st.altair_chart(chart, use_container_width=True)