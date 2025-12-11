# Auto-Discovery Feature: Search by Keywords

## 🎯 Problem Solved

**Before:** Users had to manually find paste URLs, which was impractical.

**Now:** Users can search by keywords and let Nexzy automatically discover relevant pastes!

## 🚀 How to Use

### Option 1: Auto-Discovery Mode (Recommended)

Search for leaks using keywords - no need to find URLs yourself!

```bash
POST /api/scan
Content-Type: application/json

{
  "keywords": ["ui.ac.id", "universitas indonesia"],
  "auto_discover": true,
  "crawl_authors": true
}
```

**What happens:**
1. System searches paste sites for your keywords
2. Discovers up to 50 relevant pastes automatically
3. Analyzes each paste for credentials/PII
4. Generates alerts for high-risk findings

### Option 2: Manual URL Input (Original Method)

If you already know specific paste URLs:

```bash
POST /api/scan
Content-Type: application/json

{
  "urls": [
    "https://pastebin.com/KC9Qa3ZU",
    "https://paste.ee/p/abc123"
  ],
  "crawl_authors": true
}
```

### Option 3: Hybrid Mode

Combine both methods for comprehensive scanning:

```bash
POST /api/scan
Content-Type: application/json

{
  "urls": ["https://pastebin.com/KC9Qa3ZU"],
  "keywords": ["ui.ac.id"],
  "auto_discover": true,
  "crawl_authors": true
}
```

## 📊 Frontend Integration

### Update the Scan Modal Component

Add keyword input option in your scan creation UI:

```jsx
// src/components/ScanModal.jsx

const [scanMode, setScanMode] = useState('keywords'); // 'keywords' or 'urls'
const [keywords, setKeywords] = useState(['ui.ac.id']);
const [urls, setUrls] = useState([]);

const handleSubmit = async () => {
  const payload = scanMode === 'keywords' 
    ? {
        keywords: keywords,
        auto_discover: true,
        crawl_authors: true
      }
    : {
        urls: urls,
        crawl_authors: true
      };
  
  await api.createScan(payload);
};

return (
  <div>
    <label>Scan Mode:</label>
    <select value={scanMode} onChange={(e) => setScanMode(e.target.value)}>
      <option value="keywords">Search by Keywords (Auto-Discover)</option>
      <option value="urls">Enter Specific URLs</option>
    </select>
    
    {scanMode === 'keywords' ? (
      <div>
        <label>Keywords:</label>
        <input 
          type="text" 
          placeholder="e.g., ui.ac.id, universitas indonesia"
          value={keywords.join(', ')}
          onChange={(e) => setKeywords(e.target.value.split(',').map(s => s.trim()))}
        />
        <p className="text-sm text-gray-400">
          System will automatically search paste sites for these keywords
        </p>
      </div>
    ) : (
      <div>
        <label>Paste URLs:</label>
        <textarea 
          placeholder="https://pastebin.com/..."
          value={urls.join('\n')}
          onChange={(e) => setUrls(e.target.value.split('\n').filter(Boolean))}
        />
      </div>
    )}
  </div>
);
```

## 🔍 How It Works Internally

### Step-by-Step Process:

1. **User submits keywords** (e.g., "ui.ac.id", "universitas indonesia")

2. **System searches Pastebin archive**
   - Fetches recent public pastes
   - Checks each paste for keyword matches
   - Discovers up to 50 relevant URLs

3. **Analysis phase**
   - Scrapes each discovered paste
   - Extracts emails, credentials, PII
   - Calculates relevance score
   - Identifies Indonesian student data (NPM, phone, address)

4. **Optional author crawling**
   - If enabled, finds other pastes by same authors
   - Expands the search radius

5. **AI scoring** (if configured)
   - Sends high-risk findings to AI service
   - Gets vulnerability scores and summaries

6. **Alert generation**
   - Creates alerts for critical findings
   - Severity based on risk level

## ⚙️ Configuration

### Backend Settings

In your `.env` file:

```env
# Discovery settings
MIN_RELEVANCE_SCORE=0.05   # Lower = more sensitive
REQUEST_DELAY=2.0          # Delay between requests (avoid rate limits)
MAX_RETRIES=3              # Retry failed requests
```

### API Request Limits

- **Keywords:** Max 5 per request
- **URLs:** Max 20 per request (manual mode)
- **Auto-discovery:** Finds up to 50 pastes per scan
- **Rate limit:** 5 scans per minute per user

## 🛡️ Security Features

All built-in protections still apply:

- ✅ Keyword validation (min 3 chars, max 100 chars)
- ✅ Domain allowlist (only trusted paste sites)
- ✅ SSRF protection
- ✅ Rate limiting
- ✅ User authentication required

## 📝 Example Workflows

### Scenario 1: University IT Security Team

**Goal:** Monitor for any leaked UI credentials

```bash
curl -X POST http://localhost:8001/api/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["ui.ac.id", "@ui.ac.id", "universitas indonesia"],
    "auto_discover": true,
    "crawl_authors": true
  }'
```

### Scenario 2: Incident Response

**Goal:** Investigate a specific leak you heard about

```bash
curl -X POST http://localhost:8001/api/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://pastebin.com/KC9Qa3ZU"],
    "keywords": ["ui.ac.id"],
    "auto_discover": true,
    "crawl_authors": true
  }'
```

This hybrid approach:
1. Analyzes the specific paste you found
2. Searches for related pastes with the keyword
3. Crawls the author's other pastes
4. Gives you comprehensive coverage

### Scenario 3: Daily Monitoring

**Goal:** Regular automated scans

Set up a cron job or scheduled task:

```python
import requests
import schedule

def daily_scan():
    requests.post(
        "http://localhost:8001/api/scan",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "keywords": ["ui.ac.id"],
            "auto_discover": True,
            "crawl_authors": True
        }
    )

# Run every day at 2 AM
schedule.every().day.at("02:00").do(daily_scan)
```

## ⚠️ Limitations & Notes

### Current Limitations:

1. **Pastebin Search**
   - Relies on archive page (not API search)
   - Only finds recent public pastes
   - Private/unlisted pastes won't be discovered

2. **Other Paste Sites**
   - Most don't have public search APIs
   - Currently only Pastebin auto-discovery works
   - Future: Add Google/Bing search integration

3. **Rate Limits**
   - Pastebin may block aggressive scraping
   - Built-in delays to avoid detection
   - Consider proxies for large-scale monitoring

### Best Practices:

- ✅ Use specific keywords (better results than generic terms)
- ✅ Combine common variations ("ui.ac.id" + "universitas indonesia")
- ✅ Run scans during off-peak hours
- ✅ Enable author crawling for better coverage
- ✅ Review false positives and adjust MIN_RELEVANCE_SCORE

## 🔮 Future Enhancements

Planned improvements:

- [ ] Google/Bing search integration for paste sites
- [ ] Paste.ee, PrivateBin auto-discovery
- [ ] Dark web paste site monitoring
- [ ] GitHub gist/code search
- [ ] Telegram/Discord channel monitoring
- [ ] Historical data search (archive.org)
- [ ] Machine learning for better keyword expansion

## 🐛 Troubleshooting

### "No URLs found" error

**Problem:** Auto-discovery didn't find any pastes

**Solutions:**
- Try broader keywords
- Check if paste sites are accessible
- Verify REQUEST_DELAY isn't too high
- Look for recent manual pastes first

### Rate limiting issues

**Problem:** Getting blocked by paste sites

**Solutions:**
- Increase REQUEST_DELAY in config
- Use VPN or proxy
- Reduce scan frequency
- Contact paste site for API access

### Low relevance results

**Problem:** Too many false positives

**Solutions:**
- Increase MIN_RELEVANCE_SCORE
- Use more specific keywords
- Combine multiple keywords
- Review and report false positives

## 📚 Related Documentation

- [Backend API Documentation](../nexzy-backend/README.md)
- [Discovery Engine Code](../nexzy-backend/scrapers/discovery_engine.py)
- [Configuration Guide](../nexzy-backend/config.py)
- [Security Improvements](../IMPROVEMENTS_SUMMARY.md)

---

**This feature makes Nexzy truly autonomous - no more manual paste hunting! 🎯**
