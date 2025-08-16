import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api"
LEAGUE_ID = 43344  # Replace with actual league ID
JAGER_CUP_LEAGUE_ID = 2636085  # Jager Cup H2H league ID


# Function to get current gameweek information
def get_current_gameweek_info():
    """Get current gameweek information from FPL API."""
    url = f"{BASE_URL}/bootstrap-static/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch gameweek info. Status code: {response.status_code}")
        return None
    
    data = response.json()
    events = data.get("events", [])
    
    # Find current and finished gameweeks
    current_event = None
    finished_events = []
    
    for event in events:
        if event["is_current"]:
            current_event = event["id"]
        if event["finished"]:
            finished_events.append(event["id"])
    
    return {
        "current_event": current_event,
        "finished_events": finished_events,
        "all_events": events
    }


# Function to get list of managers in the league
def get_league_entries(league_id):
    entries = []
    page = 1
    while True:
        url = f"{BASE_URL}/leagues-classic/{league_id}/standings/?page_new_entries=1&page_standings={page}"
        r = requests.get(url)
        data = r.json()
        standings = data["standings"]["results"]
        if not standings:
            break
        entries.extend(standings)
        page += 1
    return entries


# Function to get chip usage for a manager across all gameweeks
def get_manager_chips(entry_id):
    chips_used = []
    # Try to get picks for each gameweek (1-38)
    for gw in range(1, 39):
        url = f"{BASE_URL}/entry/{entry_id}/event/{gw}/picks/"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if data.get("active_chip"):
                chips_used.append({"event": gw, "chip": data["active_chip"]})
        else:
            # If we get an error, the gameweek might not be available yet
            break
    return chips_used


# Function to get weekly history for a given manager/team ID
def get_team_weekly_data(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/history/"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("current", [])  # Weekly data


# Main function to gather all weekly data
def get_league_data(league_id):
    league_entries = get_league_entries(league_id)
    all_data = []
    chip_data = []

    # Debug: Print the first entry to see available fields
    if league_entries:
        print("Available fields in league entry:", list(league_entries[0].keys()))

    for entry in league_entries:
        entry_id = entry["entry"]  # FPL team ID
        # Handle potential missing player_name field
        player_name = entry.get("player_name", "Unknown Player")
        team_name = entry.get("entry_name", "Unknown Team")

        # Get weekly scores data
        weekly_data = get_team_weekly_data(entry_id)
        
        if weekly_data:
            for gw in weekly_data:
                gw["player_name"] = player_name
                gw["team_name"] = team_name
                gw["entry_id"] = entry_id
                all_data.append(gw)

        # Get chip usage data separately
        chips_used = get_manager_chips(entry_id)
        for chip_info in chips_used:
            chip_data.append(
                {
                    "entry_id": entry_id,
                    "player_name": player_name,
                    "team_name": team_name,
                    "event": chip_info["event"],
                    "chip": chip_info["chip"],
                }
            )

    return pd.DataFrame(all_data), pd.DataFrame(chip_data)


# Function to get Jager Cup H2H matches data
def get_jager_cup_data(league_id):
    """Fetch Jager Cup H2H matches data from FPL API."""
    url = f"{BASE_URL}/leagues-h2h-matches/league/{league_id}/?page=1"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Jager Cup league {league_id} not found or H2H matches haven't started yet.")
        return pd.DataFrame()
    elif response.status_code != 200:
        print(f"Failed to fetch Jager Cup data. Status code: {response.status_code}")
        return pd.DataFrame()
    
    data = response.json()
    
    # Check if there are any results
    if not data.get("results"):
        print("No Jager Cup matches found yet.")
        return pd.DataFrame()
    
    matches = []
    
    for match in data["results"]:
        matches.append({
            "event": match["event"],
            "stage": match["knockout_name"],
            "entry_1_id": match["entry_1_entry"],
            "entry_1_player_name": match["entry_1_player_name"],
            "entry_1_team_name": match["entry_1_name"],
            "entry_1_points": match["entry_1_points"],
            "entry_2_id": match["entry_2_entry"],
            "entry_2_player_name": match["entry_2_player_name"],
            "entry_2_team_name": match["entry_2_name"],
            "entry_2_points": match["entry_2_points"],
            "winner": match["winner"],
            "is_bye": match["is_bye"]
        })
    
    df = pd.DataFrame(matches)
    if not df.empty:
        # Title case player names for consistency
        df["entry_1_player_name"] = df["entry_1_player_name"].str.title()
        df["entry_2_player_name"] = df["entry_2_player_name"].str.title()
    
    return df


# Example usage
try:
    # Get current gameweek information
    gw_info = get_current_gameweek_info()
    if gw_info:
        # Save gameweek info to a JSON-like CSV for easy reading in Streamlit
        gw_df = pd.DataFrame([{
            "current_event": gw_info["current_event"],
            "finished_events": ",".join(map(str, gw_info["finished_events"])) if gw_info["finished_events"] else ""
        }])
        gw_df.to_csv("data/gameweek_info.csv", index=False)
        print(f"Current gameweek: {gw_info['current_event']}, Finished gameweeks: {len(gw_info['finished_events'])}")

    # Get league weekly scores and chip data
    df, df_chips = get_league_data(LEAGUE_ID)
    
    # Check if DataFrame is not empty and has the expected column
    if not df.empty and "player_name" in df.columns:
        df["player_name"] = df["player_name"].str.title()
    
    df.to_csv(f"data/weekly_scores.csv", index=False)

    if not df_chips.empty:
        if "player_name" in df_chips.columns:
            df_chips["player_name"] = df_chips["player_name"].str.title()
        df_chips.to_csv(f"data/chip_usage.csv", index=False)
        print("Successfully updated weekly_scores.csv and chip_usage.csv")
    else:
        print("Successfully updated weekly_scores.csv (no chip data found)")

    # Get Jager Cup data
    df_jager_cup = get_jager_cup_data(JAGER_CUP_LEAGUE_ID)
    if not df_jager_cup.empty:
        df_jager_cup.to_csv("data/jager_cup_matches.csv", index=False)
        print("Successfully updated jager_cup_matches.csv")
    else:
        print("No Jager Cup data found or failed to fetch")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
    print("Script terminated early due to error")
