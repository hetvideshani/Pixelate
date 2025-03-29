import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials! Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
