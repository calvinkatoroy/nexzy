"""
Test PII Detection for Indonesian Student Data
"""

import re

def test_contains_credentials(text: str) -> bool:
    """Test the enhanced credential detection"""
    
    # Traditional credential patterns
    credential_patterns = [
        r'\b\w+:\w+@',  # user:pass@
        r'\b\w+:\w{6,}\b',  # user:password (6+ chars)
        r'password\s*[:=]\s*\S+',  # password: xxx or password=xxx
        r'username\s*[:=]\s*\S+.*password\s*[:=]\s*\S+',  # username/password pair
    ]
    
    # PII (Personal Identifiable Information) patterns - Indonesian context
    pii_patterns = [
        r'npm\s*[:=]\s*\d{10}',  # NPM: 2006596371
        r'no\.?\s*hp\s*(pribadi|orang\s*tua)?\s*[:=]\s*[\d\s\+\-\(\)]{8,}',  # Phone: 87781835703
        r'nik\s*[:=]\s*\d{16}',  # NIK (Indonesian ID)
        r'alamat\s*(rumah|kost|lengkap)?\s*[:=]',  # Address patterns
        r'tempat\s*lahir\s*[:=]',  # Birth place
        r'tanggal\s*lahir\s*[:=]',  # Birth date
        r'nama\s*(lengkap|panggilan)\s*[:=]',  # Full name patterns
        r'program\s*studi\s*[:=]',  # Study program
        r'jalur\s*masuk\s*[:=]',  # University entry method
        r'fakultas\s*[:=]',  # Faculty
    ]
    
    # Database leak indicators
    leak_indicators = [
        r'database\s+(dump|leak|breach)',
        r'leaked\s+(credentials|data|database)',
        r'(dump|leaked)\s+\d+\s+(users|accounts|emails)',
    ]
    
    text_lower = text.lower()
    
    # Check for traditional credentials
    for pattern in credential_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print(f"✅ MATCH: Traditional credential pattern: {pattern}")
            return True
    
    # Check for PII patterns (Indonesian student data leaks)
    for pattern in pii_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"✅ MATCH: PII pattern: {pattern}")
            print(f"   Found: {match.group()}")
            return True
    
    # Check for database leak indicators
    for pattern in leak_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            print(f"✅ MATCH: Leak indicator: {pattern}")
            return True
    
    # Check if contains multiple personal data fields (heuristic)
    pii_keywords = ['nama', 'npm', 'email', 'alamat', 'no. hp', 'hp pribadi', 
                    'tanggal lahir', 'tempat lahir', 'fakultas', 'jurusan']
    keyword_count = sum(1 for keyword in pii_keywords if keyword in text_lower)
    
    if keyword_count >= 3:
        print(f"✅ MATCH: Multiple PII fields detected ({keyword_count} fields)")
        matching_keywords = [kw for kw in pii_keywords if kw in text_lower]
        print(f"   Keywords found: {matching_keywords}")
        return True
    
    print(f"❌ NO MATCH - Only {keyword_count} PII keywords found")
    return False


# Test with sample data
sample_data = """
Nama Lengkap: Adrian Larry Ananda Sudarthio
Nama Panggilan: Larry
Jenis Kelamin: Laki-Laki
Tempat Lahir: Depok
Tanggal Lahir: 20 Oktober 2001
Asal SMA: Sekolah Global Mandiri Cibubur
NPM: 2006596371
Fakultas: Fasilkom
Jurusan: Ilmu Komputer
Program Studi: Reguler
Jalur Masuk: SIMAK
Asal Daerah: Depok, Jawa Barat
Alamat Rumah: Bumi Ampel Raya Blok A No.17
Alamat Kost: -
No. HP Pribadi: 87781835703
No. HP Orang Tua: 87778488578
Email: larry.sudarthio@gmail.com
ID Line: larrypult
"""

print("=" * 70)
print("TESTING PII DETECTION")
print("=" * 70)
print("\nSample data:")
print(sample_data[:200] + "...")
print("\n" + "=" * 70)
print("DETECTION RESULTS:")
print("=" * 70 + "\n")

result = test_contains_credentials(sample_data)

print("\n" + "=" * 70)
print(f"FINAL RESULT: {'✅ CREDENTIALS DETECTED' if result else '❌ NO CREDENTIALS'}")
print("=" * 70)
