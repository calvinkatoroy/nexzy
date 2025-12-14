"""
Test credential detection on actual paste content
"""
import re
import requests

def contains_credentials(text: str) -> bool:
    """Check if text contains credentials"""
    patterns = [
        r'\b\w+:\w+@',  # user:pass@
        r'\b\w+:\w{6,}\b',  # user:password (6+ chars)
        r'password\s*[:=]\s*\S+',  # password: xxx or password=xxx
        r'username\s*[:=]\s*\S+.*password\s*[:=]\s*\S+',  # username/password pair
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

# Test with actual paste
paste_url = "https://pastebin.com/KC9Qa3ZU"
raw_url = f"https://pastebin.com/raw/KC9Qa3ZU"

print(f"Fetching: {raw_url}")
response = requests.get(raw_url)

if response.status_code == 200:
    content = response.text
    print(f"\n📄 Content length: {len(content)} chars")
    print(f"\n--- First 500 chars ---")
    print(content[:500])
    print(f"\n--- Last 500 chars ---")
    print(content[-500:])
    
    has_creds = contains_credentials(content)
    print(f"\n🔑 Has credentials: {has_creds}")
    
    # Show what patterns match
    patterns = [
        (r'\b\w+:\w+@', 'user:pass@'),
        (r'\b\w+:\w{6,}\b', 'user:password (6+ chars)'),
        (r'password\s*[:=]\s*\S+', 'password: xxx'),
        (r'username\s*[:=]\s*\S+.*password\s*[:=]\s*\S+', 'username/password pair'),
    ]
    
    print("\n🔍 Pattern matches:")
    for pattern, name in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  ✓ {name}: {len(matches)} matches")
            print(f"    Examples: {matches[:3]}")
        else:
            print(f"  ✗ {name}: 0 matches")
else:
    print(f"❌ Failed to fetch: {response.status_code}")
