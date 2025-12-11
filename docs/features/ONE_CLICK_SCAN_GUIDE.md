# One-Click Scan & Multi-University Support

## 🎯 New Features

### 1️⃣ **One-Click "Scan Now" Button**
No more typing URLs or keywords! Just click and go.

### 2️⃣ **Configurable Target University**
Monitor any university, not just Universitas Indonesia!

---

## 🚀 How It Works

### User Flow

```
1. User signs up/logs in
2. Go to Settings → Configure target university (e.g., "itb.ac.id", "ugm.ac.id")
3. Click "Scan Now" button on dashboard
4. System automatically searches for leaks
5. Get alerts when credentials found
```

---

## 📡 API Endpoints

### GET `/api/settings`
Get user's monitoring configuration

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "target_domain": "ui.ac.id",
  "target_keywords": ["ui.ac.id", "universitas indonesia"],
  "organization": "Universitas Indonesia IT Security"
}
```

### PUT `/api/settings`
Update monitoring configuration

**Request Body:**
```json
{
  "target_domain": "itb.ac.id",
  "target_keywords": ["itb.ac.id", "institut teknologi bandung", "ITB"],
  "organization": "ITB Security Team"
}
```

**Response:**
```json
{
  "success": true,
  "data": { /* updated profile */ }
}
```

### POST `/api/scan/quick`
One-click scan using saved settings

**No body required!** Just call it.

**Response:**
```json
{
  "scan_id": "abc-123",
  "status": "queued",
  "message": "Quick scan started! Monitoring itb.ac.id for leaks...",
  "created_at": "2025-12-11T..."
}
```

---

## 🎨 Frontend Implementation

### Settings Page

```jsx
// src/pages/Settings.jsx
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await api.updateSettings({
        target_domain: settings.target_domain,
        target_keywords: settings.target_keywords,
        organization: settings.organization
      });
      alert('Settings saved!');
    } catch (error) {
      alert('Failed to save settings');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Monitoring Settings</h1>
      
      <form onSubmit={handleSave} className="space-y-6">
        {/* Target Domain */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Target Domain
          </label>
          <input
            type="text"
            value={settings.target_domain}
            onChange={(e) => setSettings({...settings, target_domain: e.target.value})}
            placeholder="e.g., ui.ac.id, itb.ac.id"
            className="w-full px-4 py-2 border rounded-lg"
          />
          <p className="text-sm text-gray-500 mt-1">
            The domain you want to monitor for leaked credentials
          </p>
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Search Keywords
          </label>
          <input
            type="text"
            value={settings.target_keywords?.join(', ')}
            onChange={(e) => setSettings({
              ...settings, 
              target_keywords: e.target.value.split(',').map(k => k.trim())
            })}
            placeholder="e.g., ui.ac.id, universitas indonesia"
            className="w-full px-4 py-2 border rounded-lg"
          />
          <p className="text-sm text-gray-500 mt-1">
            Comma-separated keywords for auto-discovery (max 10)
          </p>
        </div>

        {/* Organization */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Organization (Optional)
          </label>
          <input
            type="text"
            value={settings.organization || ''}
            onChange={(e) => setSettings({...settings, organization: e.target.value})}
            placeholder="e.g., IT Security Team"
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-red text-white py-3 rounded-lg font-semibold hover:bg-red/90 transition"
        >
          Save Settings
        </button>
      </form>
    </div>
  );
}
```

### Dashboard with "Scan Now" Button

```jsx
// src/pages/Dashboard.jsx
import { useState } from 'react';
import { api } from '../lib/api';

export default function Dashboard() {
  const [scanning, setScanning] = useState(false);

  const handleQuickScan = async () => {
    setScanning(true);
    try {
      const response = await api.quickScan();
      alert(`Scan started! ${response.message}`);
      // Optionally navigate to scan details
      // navigate(`/scans/${response.scan_id}`);
    } catch (error) {
      alert('Failed to start scan: ' + error.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        
        {/* ONE-CLICK SCAN BUTTON */}
        <button
          onClick={handleQuickScan}
          disabled={scanning}
          className="bg-red text-white px-8 py-3 rounded-lg font-semibold 
                     hover:bg-red/90 transition disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center gap-2"
        >
          {scanning ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Scanning...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Scan Now
            </>
          )}
        </button>
      </div>

      {/* Rest of dashboard content */}
      <DashboardStats />
      <RecentAlerts />
    </div>
  );
}
```

### API Client Updates

```javascript
// src/lib/api.js

export const api = {
  // ... existing methods ...

  /**
   * Get user settings
   */
  async getSettings() {
    return fetchAPI('/api/settings');
  },

  /**
   * Update user settings
   */
  async updateSettings(data) {
    return fetchAPI('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Quick scan with saved settings
   */
  async quickScan() {
    return fetchAPI('/api/scan/quick', {
      method: 'POST',
    });
  },
};
```

---

## 🏫 Supported Universities

Users can monitor **any university** by configuring their domain:

### Indonesian Universities
- **Universitas Indonesia**: `ui.ac.id`
- **ITB**: `itb.ac.id`
- **UGM**: `ugm.ac.id`
- **ITS**: `its.ac.id`
- **Unpad**: `unpad.ac.id`
- **Undip**: `undip.ac.id`
- **Unair**: `unair.ac.id`
- **Binus**: `binus.ac.id`

### International Universities
- **MIT**: `mit.edu`
- **Stanford**: `stanford.edu`
- **Harvard**: `harvard.edu`
- Any `.edu`, `.ac.id`, `.ac.uk` domain

---

## 💡 Example Configurations

### For ITB Security Team

```json
{
  "target_domain": "itb.ac.id",
  "target_keywords": [
    "itb.ac.id",
    "@itb.ac.id",
    "institut teknologi bandung",
    "ITB",
    "bandung institute"
  ],
  "organization": "ITB IT Security"
}
```

### For UGM

```json
{
  "target_domain": "ugm.ac.id",
  "target_keywords": [
    "ugm.ac.id",
    "@ugm.ac.id",
    "universitas gadjah mada",
    "UGM",
    "gadjah mada"
  ],
  "organization": "UGM Cyber Security"
}
```

### For Stanford

```json
{
  "target_domain": "stanford.edu",
  "target_keywords": [
    "stanford.edu",
    "@stanford.edu",
    "stanford university",
    "stanford"
  ],
  "organization": "Stanford InfoSec"
}
```

---

## 🎯 User Experience

### Before (Old Way)
```
1. User needs to find paste URLs manually
2. Copy URLs
3. Paste into scan form
4. Submit
5. Wait for results
```
**Problems:** Time-consuming, requires technical knowledge, incomplete coverage

### After (New Way)
```
1. User clicks "Scan Now" button
2. Done! ✅
```
**Benefits:** 
- ✅ Instant scanning
- ✅ No manual search required
- ✅ Comprehensive auto-discovery
- ✅ Works for any university
- ✅ One-time configuration

---

## 📊 Database Schema Update

Add to your Supabase database:

```sql
-- Add columns to user_profiles table
ALTER TABLE public.user_profiles 
ADD COLUMN IF NOT EXISTS target_domain TEXT NOT NULL DEFAULT 'ui.ac.id',
ADD COLUMN IF NOT EXISTS target_keywords JSONB DEFAULT '["ui.ac.id", "universitas indonesia"]'::jsonb;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_target_domain 
ON public.user_profiles(target_domain);
```

**Run this in Supabase SQL Editor!**

---

## 🔐 Security Features

All security protections apply:

- ✅ Rate limiting (5 quick scans/minute)
- ✅ Authentication required
- ✅ Domain validation
- ✅ Keyword validation (max 10)
- ✅ User-specific settings (RLS)

---

## 🚀 Deployment Steps

1. **Update database schema**
   ```sql
   -- Run the SQL above in Supabase
   ```

2. **Deploy backend changes**
   ```bash
   cd nexzy-backend
   pip install -r requirements.txt  # No new deps needed
   uvicorn api.main:app --reload
   ```

3. **Update frontend**
   ```bash
   cd nexzy-frontend
   # Add Settings page and update Dashboard
   npm run dev
   ```

4. **Test the flow**
   - Login → Settings → Configure domain → Dashboard → Click "Scan Now"

---

## 🎨 UI Recommendations

### Dashboard Button Design

**Primary Action (Hero Button)**
```jsx
<button className="
  bg-gradient-to-r from-red to-orange 
  text-white text-lg font-bold
  px-12 py-4 rounded-xl
  shadow-lg hover:shadow-xl
  transform hover:scale-105
  transition-all duration-200
  flex items-center gap-3
">
  <SearchIcon size={24} />
  Scan for Leaks Now
</button>
```

### Settings Page

- Clean, organized form
- Helpful tooltips/descriptions
- Real-time validation
- Save confirmation feedback
- Example values visible

---

## 📝 Example Workflows

### Workflow 1: First-Time User

```
1. Sign up for Nexzy
2. Navigate to Settings
3. Enter: target_domain = "itb.ac.id"
4. Enter keywords: "itb.ac.id, institut teknologi bandung"
5. Save
6. Go to Dashboard
7. Click "Scan Now"
8. System automatically:
   - Searches paste sites for ITB leaks
   - Analyzes discovered pastes
   - Generates alerts for credentials
9. User reviews alerts
```

### Workflow 2: Daily Monitoring

```
1. User logs in
2. Clicks "Scan Now" (one click!)
3. Gets notification when scan completes
4. Reviews any new alerts
```

### Workflow 3: Multi-University

```
IT Security Consultant managing multiple universities:

Account 1 → UI monitoring (ui.ac.id)
Account 2 → ITB monitoring (itb.ac.id)
Account 3 → UGM monitoring (ugm.ac.id)

Each account: Just click "Scan Now" daily
```

---

## ✅ Benefits Summary

| Feature | Before | After |
|---------|--------|-------|
| **Setup Time** | Find URLs manually | One-time config |
| **Scan Time** | Type URLs each time | One click |
| **Coverage** | Limited to known pastes | Auto-discovers new leaks |
| **Universities** | Hardcoded UI only | Any university |
| **User Effort** | High (manual search) | Low (automated) |
| **Scalability** | Single institution | Multi-tenant ready |

---

## 🔮 Future Enhancements

- [ ] Multi-domain monitoring (one user, multiple universities)
- [ ] Scheduled automatic scans (daily/weekly)
- [ ] Email notifications when leaks found
- [ ] Mobile app with push notifications
- [ ] Team accounts (multiple users, one organization)
- [ ] Advanced keyword templates by university type
- [ ] Integration with university SIEM systems

---

## 📚 Related Documentation

- [Database Schema](../nexzy-backend/SCHEMA.md)
- [API Documentation](../nexzy-backend/README.md)
- [Auto-Discovery Guide](./AUTO_DISCOVERY_GUIDE.md)
- [Security Improvements](./IMPROVEMENTS_SUMMARY.md)

---

**Now Nexzy is truly user-friendly! One click to protect your university! 🎓🔒**
