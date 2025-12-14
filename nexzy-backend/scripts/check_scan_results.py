"""
Check recent scan results in database
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("=" * 70)
print("CHECKING RECENT SCAN RESULTS")
print("=" * 70)

# Get recent scans
scans = supabase.table('scans').select('*').order('created_at', desc=True).limit(5).execute()

print(f"\n📊 Recent Scans ({len(scans.data)}):")
for scan in scans.data:
    print(f"\n  Scan ID: {scan['id'][:8]}...")
    print(f"  Status: {scan['status']}")
    print(f"  Results: {scan.get('total_results', 0)}")
    print(f"  Credentials: {scan.get('credentials_found', 0)}")
    print(f"  Created: {scan.get('created_at', 'N/A')}")
    
    # Get results for this scan
    results = supabase.table('scan_results')\
        .select('*')\
        .eq('scan_id', scan['id'])\
        .execute()
    
    print(f"  \n  📄 Results ({len(results.data)}):")
    for result in results.data:
        print(f"    - URL: {result.get('url', 'N/A')[:50]}...")
        print(f"      Has Creds: {result.get('has_credentials', False)}")
        print(f"      Score: {result.get('relevance_score', 0):.2f}")
        print(f"      Target Emails: {len(result.get('target_emails', []))}")

# Check alerts
alerts = supabase.table('alerts').select('*').order('created_at', desc=True).limit(10).execute()
print(f"\n🚨 Recent Alerts ({len(alerts.data)}):")
for alert in alerts.data:
    print(f"  - {alert.get('severity', 'N/A').upper()}: {alert.get('title', 'N/A')[:50]}...")

print("\n" + "=" * 70)
