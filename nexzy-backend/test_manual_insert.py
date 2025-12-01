"""
Test script to manually create a scan and verify database insertion works
This bypasses frontend and tests backend + database directly
"""
import sys
import os
import asyncio
from datetime import datetime
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.supabase_client import get_supabase

async def test_manual_scan():
    """Manually create a scan in database to test if RLS policies allow it"""
    print("=" * 70)
    print("TESTING MANUAL SCAN CREATION")
    print("=" * 70)
    
    supabase = get_supabase()
    
    # You need a REAL user ID from your auth.users table
    # Get it by logging into frontend and checking your JWT token
    # Or query: SELECT id FROM auth.users WHERE email = 'admin123@nexzy.ai';
    
    print("\n⚠️  IMPORTANT: This test needs a REAL user_id")
    print("   Get your user_id by running this SQL in Supabase:")
    print("   SELECT id FROM auth.users WHERE email = 'admin123@nexzy.ai';")
    
    test_user_id = input("\nPaste your user_id here (or press Enter to skip): ").strip()
    
    if not test_user_id:
        print("\n❌ Skipping test - no user_id provided")
        return
    
    scan_id = str(uuid.uuid4())
    
    print(f"\n📝 Creating test scan: {scan_id[:8]}...")
    
    scan_data = {
        'id': scan_id,
        'user_id': test_user_id,
        'status': 'completed',
        'progress': 1.0,
        'total_results': 3,
        'credentials_found': 1,
        'urls': ['https://pastebin.com/test123'],
        'options': {
            'enable_clearnet': True,
            'enable_darknet': False,
            'crawl_authors': True
        },
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    try:
        result = supabase.table('scans').insert(scan_data).execute()
        
        if result.data:
            print(f"✅ SUCCESS! Scan created in database")
            print(f"   Scan ID: {scan_id}")
            print(f"   Status: {scan_data['status']}")
            print(f"   Credentials Found: {scan_data['credentials_found']}")
            
            # Try to read it back
            verify = supabase.table('scans').select('*').eq('id', scan_id).execute()
            if verify.data:
                print(f"\n✅ VERIFIED! Scan can be read from database")
                print(f"   Data: {verify.data[0]}")
            else:
                print(f"\n⚠️  Warning: Scan created but cannot be read back (RLS issue?)")
                
        else:
            print(f"❌ FAILED! No data returned from insert")
            print(f"   Response: {result}")
            
    except Exception as e:
        print(f"❌ ERROR creating scan: {e}")
        print(f"\n💡 This might be due to:")
        print(f"   1. Invalid user_id (user doesn't exist)")
        print(f"   2. RLS policies blocking the insert")
        print(f"   3. Database permissions issue")

if __name__ == "__main__":
    print("\n🔍 NEXZY - Manual Scan Creation Test\n")
    asyncio.run(test_manual_scan())
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70 + "\n")
