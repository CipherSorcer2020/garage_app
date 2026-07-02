import sys
import os
import psycopg2
from dotenv import load_dotenv

# Check if application runs inside PyInstaller compiled environment
if getattr(sys, 'frozen', False):
    # Running as Compiled EXE: look for .env in same directory as the executable
    dotenv_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # Running in Development: look for .env in the project root directory
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

# Load connection settings from the identified .env file
load_dotenv(dotenv_path)

def get_connection():
    """
    Creates and returns a new connection to the PostgreSQL database.
    Reads credentials directly from environment variables.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
