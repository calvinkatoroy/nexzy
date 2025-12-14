"""
Quick script to check if database schema has credentials_found column
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.supabase_client import get_supabase

def check_schema():
    """Check if credentials_found column exists"""
    print("=" * 70)
    print("CHECKING DATABASE SCHEMA")
    print("=" * 70)
    
    supabase = get_supabase()
    
    try:
        # Try to select the column
        result = supabase.table('scans').select('id, credentials_found').limit(1).execute()
        print("\n✅ SUCCESS: 'credentials_found' column EXISTS in 'scans' table")
        print(f"   Query worked: {result.data}")
        return True
    except Exception as e:
        print("\n❌ ERROR: 'credentials_found' column DOES NOT EXIST")
        print(f"   Error: {e}")
        print("\n📋 YOU NEED TO RUN THIS SQL IN SUPABASE SQL EDITOR:")
        print("-" * 70)
        print("""
ALTER TABLE public.scans 
ADD COLUMN IF NOT EXISTS credentials_found INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_scans_credentials_found 
ON public.scans(credentials_found DESC);
        """)
        print("-" * 70)
        return False

def check_scans():
    """Check existing scans in database"""
    print("\n" + "=" * 70)
    print("CHECKING EXISTING SCANS")
    print("=" * 70)
    
    supabase = get_supabase()
    
    try:
        result = supabase.table('scans').select('*').order('created_at', desc=True).limit(5).execute()
        
        if result.data:
            print(f"\n✅ Found {len(result.data)} recent scans:")
            for scan in result.data:
                print(f"\n   Scan ID: {scan['id'][:8]}...")
                print(f"   Status: {scan['status']}")
                print(f"   Total Results: {scan.get('total_results', 0)}")
                print(f"   Credentials Found: {scan.get('credentials_found', 'N/A')}")
                print(f"   Created: {scan['created_at']}")
        else:
            print("\n⚠️  No scans found in database yet")
            print("   Database is empty - create a scan from frontend to test")
            
    except Exception as e:
        print(f"\n❌ Error checking scans: {e}")

if __name__ == "__main__":
    print("\n🔍 NEXZY - Database Schema Check\n")
    
    schema_ok = check_schema()
    
    if schema_ok:
        check_scans()
    
    print("\n" + "=" * 70)
    print("CHECK COMPLETE")
    print("=" * 70 + "\n")
