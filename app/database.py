"""
Supabase Database Connection
"""
from supabase import create_client, Client

# Supabase connection credentials

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase() -> Client:
    """Returns the Supabase client instance"""
    return supabase