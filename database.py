import sqlite3
import time
from datetime import datetime

DB_NAME = "sentinel_sessions.db"

def init_db():
  """This will create the sessions table if not exist."""
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT,
      start_time TEXT,
      end_time TEXT,
      duration_seconds INTEGER,
      focus_score INTEGER,
      phone_seconds INTEGER,
      absent_seconds INTEGER,
      social_seconds INTEGER
    )
  ''')
  conn.commit()
  conn.close()

def save_session(start_time_obj, duration_seconds, focus_score, phone_seconds, absent_seconds, social_seconds):
  """This will save a completed work session to the database."""
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  end_time_obj = datetime.now()    # This captures the exact time when the user click save_session button.
  c.execute('''
    INSERT INTO sessions
    (date, start_time, end_time, duration_seconds, focus_score, phone_seconds, absent_seconds, social_seconds)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  ''', (
    start_time_obj.strftime("%Y-%m-%d"),    # The start YYYY-MM-DD captured when user click the session start
    start_time_obj.strftime("%H:%M:%S"),    # The start time captured when user click the session start
    end_time_obj.strftime("%H:%M:%S"),      # The time format when the user clicks save_session button as I mentioned above
    duration_seconds,
    focus_score,
    phone_seconds,
    absent_seconds,
    social_seconds
  ))
  conn.commit()
  conn.close()

def get_all_sessions():
  """Retrieve all past sessions for the dashboard history chart."""
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("SELECT date, focus_score, duration_seconds, phone_seconds, absent_seconds, social_seconds FROM sessions ORDER BY id DESC LIMIT 20")
  rows = c.fetchall()
  conn.close()
  return rows
