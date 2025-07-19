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
        'bboost': '🚀 Bench Boost',
        'freehit': '🎯 Free Hit', 
        '3xc': '👑 Triple Captain',
        'wildcard': '🔄 Wildcard',
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
        
        # Add legend for chip emojis
        st.markdown("""
        **Legend:**  
        🚀 Bench Boost | 🎯 Free Hit | 👑 Triple Captain | 🔄 Wildcard
        """)
        st.markdown("---")
        
        # Count chips used by each player - pivot to get chips as columns
        chip_counts = df_chips.groupby(['player_name', 'chip_display']).size().unstack(fill_value=0)
        
        # Create a summary with split chips columns based on gameweek
        chip_summary = chip_counts.reset_index()
        chip_summary = chip_summary.rename(columns={'player_name': 'Manager'})
        
        # Add total points column
        if not df_weekly_scores.empty:
            total_points = df_weekly_scores.groupby('player_name')['total_points'].max().reset_index()
            total_points = total_points.rename(columns={'player_name': 'Manager'})
            chip_summary = chip_summary.merge(total_points, on='Manager', how='left')
            chip_summary['total_points'] = chip_summary['total_points'].fillna(0).astype(int)
        else:
            chip_summary['total_points'] = 0
        
        # Create function to format chips for a specific gameweek range
        def format_chips_for_period(manager, gw_start, gw_end):
            # Filter chips for this manager and gameweek range
            manager_chips = df_chips[
                (df_chips['player_name'] == manager) & 
                (df_chips['event'] >= gw_start) & 
                (df_chips['event'] <= gw_end)
            ]
            
            if manager_chips.empty:
                return ''
            
            # Count chips by type for this period
            chip_counts_period = manager_chips.groupby('chip_display').size()
            chips_used = []
            
            # Define the desired order of chips
            chip_order = [
                ('🚀 Bench Boost', '🚀'),
                ('🎯 Free Hit', '🎯'),
                ('👑 Triple Captain', '👑'),
                ('🔄 Wildcard', '🔄')
            ]
            
            # Process chips in the specified order
            for chip_name, emoji in chip_order:
                if chip_name in chip_counts_period:
                    count = chip_counts_period[chip_name]
                    if count > 0:
                        chips_used.append(emoji * count)
            
            return ' '.join(chips_used) if chips_used else ''
        
        # Create chips columns for each period
        chip_summary['Chips GW 1-19'] = chip_summary['Manager'].apply(
            lambda x: format_chips_for_period(x, 1, 19)
        )
        chip_summary['Chips GW 20-38'] = chip_summary['Manager'].apply(
            lambda x: format_chips_for_period(x, 20, 38)
        )
        
        # Sort by total points (descending) and add rank
        chip_summary = chip_summary.sort_values('total_points', ascending=False)
        chip_summary['Rank'] = range(1, len(chip_summary) + 1)
        
        # Keep only the columns we want to display
        chip_summary = chip_summary[['Rank', 'Manager', 'total_points', 'Chips GW 1-19', 'Chips GW 20-38']]
        
        # Create column configuration
        config_columns = {
            'Rank': st.column_config.NumberColumn("Rank", width=60),
            'Manager': st.column_config.TextColumn("Manager", width=150),
            'total_points': st.column_config.NumberColumn("Total Points", width=100),
            'Chips GW 1-19': st.column_config.TextColumn("GW 1-19", width=120),
            'Chips GW 20-38': st.column_config.TextColumn("GW 20-38", width=120)
        }
        
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
            height=(len(chip_summary) + 1) * 35 + 3,  # Calculate height to show all rows
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