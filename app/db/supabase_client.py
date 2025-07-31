from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)