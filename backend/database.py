import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

def get_supabase():
    return supabase

# Tables should be created via Supabase dashboard or SQL editor
# politicians: id (uuid/int), name, party, constituency, state, total_assets, total_liabilities, source_url, myneta_id
# investments: id, politician_id, type, description, amount
