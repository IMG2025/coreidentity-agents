import time
from supabase import create_client
import os

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Provisionr Agent: Auto-creates tables if they don't exist
def provision_tables():
    print("[Provisionr] Checking and creating required tables if missing...")

    table_definitions = {
        "pulse_logs": """
            create table if not exists pulse_logs (
              id uuid default gen_random_uuid() primary key,
              timestamp text,
              source text,
              message text
            );
        """,
        "deployr_logs": """
            create table if not exists deployr_logs (
              id uuid default gen_random_uuid() primary key,
              timestamp text,
              agent_name text
            );
        """,
        "echo_logs": """
            create table if not exists echo_logs (
              id uuid default gen_random_uuid() primary key,
              timestamp text,
              type text,
              audience text,
              output text
            );
        """,
        "signal_events": """
            create table if not exists signal_events (
              id uuid default gen_random_uuid() primary key,
              timestamp text,
              source text,
              payload text,
              routed_to text,
              result text
            );
        """,
        "edge_logs": """
            create table if not exists edge_logs (
              id uuid default gen_random_uuid() primary key,
              timestamp text,
              agent text,
              action text,
              source text,
              details text
            );
        """
    }

    for name, sql in table_definitions.items():
        try:
            print(f"[Provisionr] Ensuring table exists: {name}")
            supabase.table(name).select("*").limit(1).execute()
        except Exception:
            try:
                print(f"[Provisionr] Creating table: {name}")
                supabase.postgrest.rpc("sql", {"query": sql})
            except Exception as e:
                print(f"[Provisionr] Error creating table {name}: {e}")
