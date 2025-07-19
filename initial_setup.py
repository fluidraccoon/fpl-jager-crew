import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api"
LEAGUE_ID = 16511  # Replace with actual league ID


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

    for entry in league_entries:
        entry_id = entry["entry"]  # FPL team ID
        player_name = entry["player_name"]
        team_name = entry["entry_name"]

        # Get weekly scores data
        weekly_data = get_team_weekly_data(entry_id)

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


# Example usage
try:
    df, df_chips = get_league_data(LEAGUE_ID)
    df["player_name"] = df["player_name"].str.title()
    df.to_csv(f"data/weekly_scores.csv", index=False)

    if not df_chips.empty:
        df_chips["player_name"] = df_chips["player_name"].str.title()
        df_chips.to_csv(f"data/chip_usage.csv", index=False)
        print("Successfully updated weekly_scores.csv and chip_usage.csv")
    else:
        print("Successfully updated weekly_scores.csv (no chip data found)")

except Exception as e:
    print(f"Error occurred: {e}")
    print("Script terminated early due to error")
