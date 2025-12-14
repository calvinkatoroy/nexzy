"""
Insert sample alerts directly into database for POC
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Using service role key for direct inserts
)

# Get user ID (you need to be logged in)
# For POC, using hardcoded user_id (replace with your actual user_id)
user_id = "6829869a-1fcb-49c4-baa3-27a43e8e0ab6"  # Get this from Supabase dashboard or auth

print(f"[INFO] Using user_id: {user_id}")

# Sample data from the pastebin URLs
sample_data = [
    {
        'url': 'https://pastebin.com/KC9Qa3ZU',
        'author': 'juandk',
        'title': 'KMBUI - Data Mahasiswa UI',
        'description': 'Database mahasiswa Universitas Indonesia berisi NPM, nama, email, nomor HP, alamat. Total 30 records dengan 4 target emails (@ui.ac.id)',
        'severity': 'critical',
        'target_emails': 4,
        'total_records': 30
    },
    {
        'url': 'https://pastebin.com/m6FTggSP',
        'author': 'juandk',
        'title': 'KMBUI - Data Mahasiswa UI (Batch 2)',
        'description': 'Database mahasiswa Universitas Indonesia berisi data personal lengkap. Termasuk NPM, kontak pribadi, dan alamat tempat tinggal',
        'severity': 'high',
        'target_emails': 3,
        'total_records': 25
    },
    {
        'url': 'https://pastebin.com/FUq9zxFD',
        'author': 'juandk',
        'title': 'Data Mahasiswa FKM UI',
        'description': 'Data mahasiswa Fakultas Kesehatan Masyarakat UI dengan informasi kontak dan akademik',
        'severity': 'high',
        'target_emails': 2,
        'total_records': 20
    },
    {
        'url': 'https://pastebin.com/14JBWijc',
        'author': 'juandk',
        'title': 'Data Mahasiswa FISIP UI',
        'description': 'Database mahasiswa FISIP UI termasuk data personal dan kontak keluarga',
        'severity': 'medium',
        'target_emails': 1,
        'total_records': 18
    },
    {
        'url': 'https://pastebin.com/caQnCmPB',
        'author': 'juandk',
        'title': 'Data Mahasiswa Teknik UI',
        'description': 'Informasi mahasiswa Fakultas Teknik UI dengan detail kontak dan alamat',
        'severity': 'medium',
        'target_emails': 1,
        'total_records': 22
    }
]

# Create a scan first
scan_data = {
    'id': str(uuid.uuid4()),
    'user_id': user_id,
    'status': 'completed',
    'progress': 1.0,
    'total_results': len(sample_data),
    'credentials_found': len(sample_data),
    'urls': [item['url'] for item in sample_data],
    'options': {
        'crawl_authors': True,
        'enable_clearnet': True,
        'enable_darknet': False
    },
    'created_at': datetime.utcnow().isoformat(),
    'updated_at': datetime.utcnow().isoformat()
}

print(f"\n[CREATING] Inserting scan...")
scan_result = supabase.table('scans').insert(scan_data).execute()
scan_id = scan_result.data[0]['id']
print(f"[OK] Scan created: {scan_id}")

# Insert scan results
print(f"\n[CREATING] Inserting {len(sample_data)} scan results...")
for idx, item in enumerate(sample_data, 1):
    result_data = {
        'id': str(uuid.uuid4()),
        'scan_id': scan_id,
        'user_id': user_id,
        'url': item['url'],
        'source': 'pastebin',
        'author': item['author'],
        'relevance_score': 0.75 if item['severity'] in ['critical', 'high'] else 0.50,
        'emails': [f"student{i}@ui.ac.id" for i in range(item['total_records'])],
        'target_emails': [f"target{i}@ui.ac.id" for i in range(item['target_emails'])],
        'has_credentials': True,
        'found_at': datetime.utcnow().isoformat()
    }
    
    supabase.table('scan_results').insert(result_data).execute()
    print(f"  [{idx}/{len(sample_data)}] Inserted: {item['url']}")

# Insert alerts
print(f"\n[CREATING] Inserting {len(sample_data)} alerts...")
for idx, item in enumerate(sample_data, 1):
    alert_data = {
        'user_id': user_id,
        'title': item['title'],
        'description': item['description'] + f" Source: {item['url']}",
        'severity': item['severity']
        # Let database handle status with default value
    }
    
    supabase.table('alerts').insert(alert_data).execute()
    print(f"  [{idx}/{len(sample_data)}] Alert created: {item['severity'].upper()} - {item['title']}")

print(f"\n{'='*60}")
print(f"[SUCCESS] POC Data Inserted!")
print(f"{'='*60}")
print(f"Scan ID: {scan_id}")
print(f"Total Results: {len(sample_data)}")
print(f"Credentials Found: {len(sample_data)}")
print(f"Alerts Created: {len(sample_data)}")
print(f"\nSeverity Breakdown:")
print(f"  - Critical: {sum(1 for x in sample_data if x['severity'] == 'critical')}")
print(f"  - High: {sum(1 for x in sample_data if x['severity'] == 'high')}")
print(f"  - Medium: {sum(1 for x in sample_data if x['severity'] == 'medium')}")
print(f"  - Low: {sum(1 for x in sample_data if x['severity'] == 'low')}")
print(f"\n{'='*60}")
print(f"Check your dashboard - alerts should now appear!")
print(f"{'='*60}")
