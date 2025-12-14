"""
Direct database insert test - bypass all backend logic
Tests if we can insert directly to Supabase
"""
import os
from supabase import create_client
from datetime import datetime
import uuid

# Load from .env
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Service role bypasses RLS

print("=" * 70)
print("DIRECT DATABASE INSERT TEST")
print("=" * 70)

print(f"\n🔗 Supabase URL: {SUPABASE_URL}")
print(f"🔑 Using SERVICE ROLE KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'NOT FOUND'}...")

if not SUPABASE_KEY:
    print("\n⚠️  WARNING: SUPABASE_SERVICE_ROLE_KEY not found in .env")
    print("   Using SUPABASE_KEY instead (might be blocked by RLS)")
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get your user ID
print("\n📋 Step 1: Getting your user ID...")
print("   Run this SQL in Supabase SQL Editor:")
print("   SELECT id, email FROM auth.users;")
user_id = input("\n   Paste your user_id here: ").strip()

if not user_id:
    print("❌ No user_id provided. Exiting.")
    exit(1)

# Create test scan
scan_id = str(uuid.uuid4())
print(f"\n📝 Step 2: Creating test scan {scan_id[:8]}...")

scan_data = {
    'id': scan_id,
    'user_id': user_id,
    'status': 'completed',
    'progress': 1.0,
    'total_results': 2,
    'credentials_found': 1,
    'urls': ['https://pastebin.com/test_direct'],
    'options': {'enable_clearnet': True},
    'created_at': datetime.utcnow().isoformat(),
    'updated_at': datetime.utcnow().isoformat()
}

try:
    result = supabase.table('scans').insert(scan_data).execute()
    print(f"✅ Scan inserted! ID: {scan_id}")
    print(f"   Data: {result.data}")
except Exception as e:
    print(f"❌ Failed to insert scan: {e}")
    print(f"\n💡 If error mentions RLS or permission:")
    print(f"   1. Check SUPABASE_SERVICE_ROLE_KEY in .env")
    print(f"   2. Or disable RLS: ALTER TABLE scans DISABLE ROW LEVEL SECURITY;")
    exit(1)

# Create test result
result_id = str(uuid.uuid4())
print(f"\n📝 Step 3: Creating test result {result_id[:8]}...")

result_data = {
    'id': result_id,
    'scan_id': scan_id,
    'user_id': user_id,
    'url': 'https://pastebin.com/example123',
    'source': 'pastebin.com',
    'author': 'test_user',
    'relevance_score': 0.85,
    'emails': ['admin@ui.ac.id', 'user@ui.ac.id'],
    'target_emails': ['admin@ui.ac.id'],
    'has_credentials': True,
    'found_at': datetime.utcnow().isoformat()
}

try:
    result = supabase.table('scan_results').insert(result_data).execute()
    print(f"✅ Result inserted! ID: {result_id}")
    print(f"   Data: {result.data}")
except Exception as e:
    print(f"❌ Failed to insert result: {e}")
    exit(1)

# Verify
print(f"\n✅ Step 4: Verifying data...")
try:
    verify_scan = supabase.table('scans').select('*').eq('id', scan_id).execute()
    verify_result = supabase.table('scan_results').select('*').eq('id', result_id).execute()
    
    if verify_scan.data and verify_result.data:
        print(f"✅ SUCCESS! Data is in database!")
        print(f"\n   Scan: {verify_scan.data[0]['id'][:8]}... - {verify_scan.data[0]['status']}")
        print(f"   Result: {verify_result.data[0]['id'][:8]}... - Score: {verify_result.data[0]['relevance_score']}")
        print(f"\n🎉 Database is working! Check Supabase dashboard.")
    else:
        print(f"⚠️  Data inserted but cannot read back (RLS policy issue?)")
except Exception as e:
    print(f"❌ Verification failed: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE - Now check your Supabase dashboard!")
print("=" * 70)
