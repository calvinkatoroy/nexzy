"""
Test script to verify scan functionality
Tests the discovery engine directly and database insertion
"""

import sys
import os
from datetime import datetime
import uuid

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.discovery_engine import DiscoveryOrchestrator
from lib.supabase_client import get_supabase

def test_discovery_engine():
    """Test the discovery engine with a sample URL"""
    print("=" * 70)
    print("TESTING DISCOVERY ENGINE")
    print("=" * 70)
    
    orchestrator = DiscoveryOrchestrator()
    
    # Test with a sample Pastebin URL (you should replace with real URL)
    test_urls = [
        "https://pastebin.com/raw/0C3NTXSY",  # Example URL
    ]
    
    print(f"\nTesting with URLs: {test_urls}")
    
    results = orchestrator.run_full_discovery(
        clearnet_urls=test_urls,
        enable_clearnet=True,
        enable_darknet=False,
        crawl_authors=False
    )
    
    print(f"\n✓ Discovery completed!")
    print(f"  Total items found: {results['total_found']}")
    
    if results['discovered_items']:
        print(f"\n  Sample result:")
        item = results['discovered_items'][0]
        print(f"    URL: {item['url']}")
        print(f"    Relevance Score: {item['relevance_score']:.2f}")
        print(f"    Emails found: {len(item['emails'])}")
        print(f"    Target emails: {len(item['target_emails'])}")
        print(f"    Has credentials: {item['has_credentials']}")
    else:
        print("\n  ⚠ No items found (URL might be invalid or low relevance)")
    
    return results

def test_database_insert():
    """Test inserting a scan into the database"""
    print("\n" + "=" * 70)
    print("TESTING DATABASE INSERTION")
    print("=" * 70)
    
    supabase = get_supabase()
    
    # Create test scan record
    scan_id = str(uuid.uuid4())
    test_user_id = "test-user-123"  # You should use a real user ID
    
    print(f"\nCreating test scan: {scan_id[:8]}...")
    
    scan_data = {
        'id': scan_id,
        'user_id': test_user_id,
        'status': 'completed',
        'progress': 1.0,
        'total_results': 5,
        'credentials_found': 2,
        'urls': ['https://pastebin.com/test'],
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
        print(f"✓ Scan inserted successfully!")
        print(f"  Scan ID: {scan_id}")
        
        # Insert a test result
        result_id = str(uuid.uuid4())
        result_data = {
            'id': result_id,
            'scan_id': scan_id,
            'user_id': test_user_id,
            'url': 'https://pastebin.com/test123',
            'source': 'pastebin.com',
            'author': 'test_author',
            'relevance_score': 0.85,
            'emails': ['user@ui.ac.id', 'admin@ui.ac.id'],
            'target_emails': ['user@ui.ac.id', 'admin@ui.ac.id'],
            'has_credentials': True,
            'found_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('scan_results').insert(result_data).execute()
        print(f"✓ Scan result inserted successfully!")
        print(f"  Result ID: {result_id}")
        
        # Query back to verify
        verify = supabase.table('scans').select('*').eq('id', scan_id).execute()
        if verify.data:
            print(f"\n✓ Database verification passed!")
            print(f"  Found scan in database")
        else:
            print(f"\n✗ Database verification failed!")
        
    except Exception as e:
        print(f"✗ Error inserting to database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("\n🔍 NEXZY - Discovery Engine Test Suite")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Discovery Engine
    try:
        results = test_discovery_engine()
    except Exception as e:
        print(f"\n✗ Discovery engine test failed: {e}")
    
    # Test 2: Database Insert
    try:
        success = test_database_insert()
        if success:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED ✓")
            print("=" * 70)
    except Exception as e:
        print(f"\n✗ Database test failed: {e}")
