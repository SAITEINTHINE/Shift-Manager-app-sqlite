import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE)
cursor = conn.cursor()

# Create Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

# Create Shifts Table (Updated with Fixed Column Order)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        break_start_time TEXT DEFAULT NULL,
        break_end_time TEXT DEFAULT NULL,
        break_time INTEGER DEFAULT 0,  
        total_hours REAL NOT NULL,
        hourly_wage_day REAL NOT NULL,
        hourly_wage_night REAL NOT NULL,
        total_pay REAL NOT NULL,
        shift_type TEXT NOT NULL CHECK(shift_type IN ('day', 'night', 'mixed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
""")

conn.commit()
conn.close()
print("Database initialized successfully.")