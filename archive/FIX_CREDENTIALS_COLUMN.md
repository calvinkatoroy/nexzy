# 🔧 FIX: Missing `credentials_found` Column

## Masalah yang Ditemukan

Backend sedang berjalan dan scan completed, tapi **data tidak tersimpan di database** karena:

1. ❌ Kolom `credentials_found` tidak ada di tabel `scans`
2. ❌ Backend mencoba insert data dengan kolom yang tidak exist
3. ❌ Error: `"Could not find the 'credentials_found' column"`

## Solusi

Jalankan SQL migration untuk menambahkan kolom yang hilang.

### Langkah-langkah:

#### 1. Buka Supabase Dashboard

1. Go to: https://app.supabase.com
2. Select your project: **oyziawmetogvilefpepl**
3. Click **SQL Editor** di sidebar kiri

#### 2. Jalankan Migration SQL

Copy & paste SQL ini ke SQL Editor, lalu klik **Run**:

```sql
-- Add credentials_found column to scans table
ALTER TABLE public.scans 
ADD COLUMN IF NOT EXISTS credentials_found INTEGER NOT NULL DEFAULT 0;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_scans_credentials_found 
ON public.scans(credentials_found DESC);

-- Verify the column was added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'scans' 
AND column_name = 'credentials_found';
```

#### 3. Verify

Kamu harus melihat output seperti ini:

```
column_name         | data_type | column_default
--------------------|-----------|----------------
credentials_found   | integer   | 0
```

## Setelah Migration

### Backend sudah running ✅

Backend sudah otomatis reload dengan perubahan code yang menghitung `credentials_found`:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Test Scan Baru

1. **Login** ke frontend: http://localhost:5173/login
   - Email: `admin123@nexzy.ai`
   - Password: password kamu

2. **Create NEW SCAN**:
   - Click tombol "NEW SCAN" (biru, top-right)
   - Paste URL contoh: `https://pastebin.com/raw/BxqCGVXB`
   - Click "START SCAN"

3. **Watch Real-Time Updates**:
   - Toast notification akan muncul bottom-right
   - Backend akan log progress di terminal
   - WebSocket akan broadcast: `scan_started` → `scan_progress` → `scan_completed`

4. **Check Results**:
   - Navigate ke **Search** page → results table akan populated
   - Navigate ke **Alerts** page → scan akan muncul as alert
   - Check Dashboard → stats akan update dengan real numbers

## Expected Logs

### Backend Terminal:
```
2025-12-01 10:XX:XX - api.main - INFO - Creating scan <uuid> for user <user_id>
2025-12-01 10:XX:XX - api.main - INFO - Scan <uuid> queued successfully
2025-12-01 10:XX:XX - api.main - INFO - Starting scan <uuid> for user <user_id>
2025-12-01 10:XX:XX - scrapers.discovery_engine - INFO - NEXZY DISCOVERY ENGINE - STARTING SCAN
2025-12-01 10:XX:XX - scrapers.discovery_engine - INFO - Analyzing: https://pastebin.com/...
2025-12-01 10:XX:XX - api.main - INFO - Scan <uuid> found 5 results
2025-12-01 10:XX:XX - api.main - INFO - Scan <uuid> found 2 credentials
2025-12-01 10:XX:XX - api.main - INFO - Scan <uuid> completed successfully
```

### Browser Console:
```
✅ WebSocket connected
{type: 'scan_started', scan_id: '...', timestamp: '...'}
{type: 'scan_progress', scan_id: '...', progress: 0.3}
{type: 'scan_progress', scan_id: '...', progress: 0.7}
{type: 'scan_completed', scan_id: '...', total_results: 5, timestamp: '...'}
```

## Troubleshooting

### Jika masih error "column not found":

1. **Restart backend**:
   ```powershell
   # Stop dengan Ctrl+C di terminal backend
   cd C:\Users\calvi\Desktop\Study\nexzy\nexzy-backend
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Hard refresh frontend**: `Ctrl+Shift+R`

3. **Check database** di Supabase:
   ```sql
   SELECT * FROM scans ORDER BY created_at DESC LIMIT 5;
   ```

### Jika URL paste tidak menghasilkan results:

URL paste harus:
- ✅ Valid dan accessible (not 404)
- ✅ Contain text related to `ui.ac.id` (target domain)
- ✅ Contain emails or keywords like "password", "leak", "credentials"

**Test URLs yang bagus**:
- Pastebin dengan email ui.ac.id
- Pastebin dengan kata "database leak"
- Pastebin dengan kata "password dump"

Relevance score calculated: **40% domain + 30% emails + 30% keywords**

Minimum score: **0.3** (30%) untuk masuk ke results

## Status Sekarang

- ✅ Backend running (port 8000)
- ✅ Frontend running (port 5173)
- ✅ Authentication working
- ✅ WebSocket connected
- ✅ Discovery engine implemented
- ⏳ **WAITING**: Migration SQL to be executed
- ⏳ **THEN**: Test creating scan with real URL

## Next Steps

1. **SEKARANG**: Run migration SQL di Supabase SQL Editor
2. **TEST**: Create scan dari frontend
3. **VERIFY**: Check data masuk ke database
4. **CELEBRATE**: System fully functional! 🎉
