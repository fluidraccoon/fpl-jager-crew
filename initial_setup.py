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


# Function to get weekly history for a given manager/team ID
def get_team_weekly_data(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/history/"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("current", [])  # Weekly data


# Main function to gather all weekly data
def get_league_weekly_data(league_id):
    league_entries = get_league_entries(league_id)
    all_data = []

    for entry in league_entries:
        entry_id = entry["entry"]  # FPL team ID
        player_name = entry["player_name"]
        team_name = entry["entry_name"]
        weekly_data = get_team_weekly_data(entry_id)
        for gw in weekly_data:
            gw["player_name"] = player_name
            gw["team_name"] = team_name
            gw["entry_id"] = entry_id
            all_data.append(gw)

    return pd.DataFrame(all_data)


# Example usage
try:
    df = get_league_weekly_data(LEAGUE_ID)
    df["player_name"] = df["player_name"].str.title()
    df.to_csv(f"data/weekly_scores.csv", index=False)
    print("Successfully updated weekly_scores.csv")
except Exception as e:
    print(f"Error occurred: {e}")
    print("Script terminated early due to error")
