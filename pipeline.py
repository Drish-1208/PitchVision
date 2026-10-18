import os
import pandas as pd
from statsbombpy import sb
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Load the hidden variables from .env
load_dotenv()

# 2. Fetch the variables safely
password = os.getenv("DB_PASSWORD")
user = os.getenv("DB_USER")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")

# 3. Construct the URL dynamically
DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(DB_URL)

print("Fetching World Cup matches...")
# ... the rest of your script
matches_df = sb.matches(competition_id=43, season_id=106)

# 1. Extract and Load Teams
home_teams = matches_df[['home_team_id', 'home_team']].rename(columns={'home_team_id': 'team_id', 'home_team': 'name'})
away_teams = matches_df[['away_team_id', 'away_team']].rename(columns={'away_team_id': 'team_id', 'away_team': 'name'})
teams_df = pd.concat([home_teams, away_teams]).drop_duplicates(subset=['team_id'])

print("Loading Teams...")
teams_df.to_sql('teams', engine, if_exists='append', index=False)

# 2. Extract and Load Matches
clean_matches = pd.DataFrame({
    'match_id': matches_df['match_id'],
    'home_team_id': matches_df['home_team_id'],
    'away_team_id': matches_df['away_team_id'],
    'match_date': pd.to_datetime(matches_df['match_date']),
    'home_score': matches_df['home_score'],
    'away_score': matches_df['away_score']
})

print("Loading Matches...")
clean_matches.to_sql('matches', engine, if_exists='append', index=False)

# 3. Process Lineups (Players) and Events
all_events = []
unique_players = {}

print("Fetching Lineups and Pitch Events...")

for match_id in clean_matches['match_id'].head(3):
    
    # --- NEW: GET PLAYERS FOR THIS MATCH ---
    lineups = sb.lineups(match_id=match_id)
    for team_name, lineup_df in lineups.items():
        team_id = teams_df[teams_df['name'] == team_name]['team_id'].values[0]
        
        for _, player_row in lineup_df.iterrows():
            pid = player_row['player_id']
            if pid not in unique_players:
                unique_players[pid] = {
                    'player_id': pid,
                    'team_id': team_id,
                    'name': player_row['player_name'],
                    'position': None, # Skipping position for now to keep it simple
                    'jersey_number': player_row['jersey_number']
                }

    # --- GET EVENTS FOR THIS MATCH ---
    events_df = sb.events(match_id=match_id)
    pitch_actions = events_df.dropna(subset=['location'])
    
    for _, row in pitch_actions.iterrows():
        event_type = row['type']
        location = row['location']
        
        end_x, end_y = None, None
        end_location = row.get('pass_end_location')
        if isinstance(end_location, list) and len(end_location) >= 2:
            end_x, end_y = end_location[0], end_location[1]
            
        xg = row.get('shot_statsbomb_xg', None)
        
        pid = row.get('player_id')
        player_id = int(pid) if pd.notna(pid) else None
        
        all_events.append({
            'event_id': row['id'],
            'match_id': match_id,
            'player_id': player_id,
            'event_type': event_type,
            'minute': row['minute'],
            'start_x': location[0],
            'start_y': location[1],
            'end_x': end_x,
            'end_y': end_y,
            'expected_goals': xg,
            'is_successful': row.get('pass_outcome') is None if event_type == 'Pass' else None
        })

# --- LOAD PLAYERS FIRST ---
print("Loading Players...")
players_df = pd.DataFrame(list(unique_players.values()))
players_df.to_sql('players', engine, if_exists='append', index=False)

# --- THEN LOAD EVENTS ---
print("Loading Pitch Events...")
events_to_db = pd.DataFrame(all_events)
events_to_db.to_sql('pitch_events', engine, if_exists='append', index=False)

print("Pipeline Complete! Check Supabase.")