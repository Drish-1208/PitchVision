import os
from fastapi import FastAPI, HTTPException
import psycopg2
from fastapi.middleware.cors import CORSMiddleware  # <-- THIS IS THE MISSING LINE
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="PitchVision Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # React's local ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect to Supabase safely using the pieces from .env
def get_db_connection():
    try:
        return psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/")
def read_root():
    return {"status": "PitchVision API is running 🟢"}

@app.get("/teams")
def get_teams():
    """Fetch all World Cup teams."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT team_id, name FROM teams ORDER BY name;")
    teams = cur.fetchall()
    cur.close()
    conn.close()
    return teams

@app.get("/teams/{team_id}/players")
def get_team_players(team_id: int):
    """Fetch the roster for a specific team."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT player_id, name, jersey_number 
        FROM players 
        WHERE team_id = %s 
        ORDER BY name;
    """, (team_id,))
    players = cur.fetchall()
    cur.close()
    conn.close()
    return players

@app.get("/players/{player_id}/events")
def get_player_events(player_id: int):
    """Fetch all spatial pitch events for a specific player (for heatmaps/pass networks)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, event_type, minute, start_x, start_y, end_x, end_y, expected_goals, is_successful 
        FROM pitch_events 
        WHERE player_id = %s;
    """, (player_id,))
    events = cur.fetchall()
    cur.close()
    conn.close()
    return events