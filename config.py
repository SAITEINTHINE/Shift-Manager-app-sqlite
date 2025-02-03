from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Fallback value
    DATABASE = os.getenv('DATABASE', 'shift_manager.db')  # SQLite database file
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
