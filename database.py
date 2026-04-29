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

def save_session(duration_seconds, focus_score, phone_seconds, absent_seconds, social_seconds):
  """This will save a completed work session to the database."""
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute('''
    INSERT INTO sessions
    (date, start_time, end_time, duration_seconds, focus_score, phone_seconds, absent_seconds, social_seconds)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  ''', (
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%H:%M:%S"),
    datetime.now().strftime("%H:%M:%S"),
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
