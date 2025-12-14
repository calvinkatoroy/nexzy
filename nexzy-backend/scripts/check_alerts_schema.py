import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Try to get one alert to see schema
try:
    result = supabase.table('alerts').select('*').limit(1).execute()
    if result.data:
        print("✓ Alerts table columns:")
        for col in result.data[0].keys():
            print(f"  - {col}")
    else:
        print("No alerts in table, creating test alert to see schema...")
        # The error message will show us what columns are allowed
except Exception as e:
    print(f"Error: {e}")
