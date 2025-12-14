# 🔧 Quick Fix for Settings & Quick Scan Errors

## Problem
- ❌ Settings page returns 500 error
- ❌ Quick Scan button returns 500 error  
- Error: "Cannot coerce the result to a single JSON object... The result contains 0 rows"

## Root Cause
Database table `user_profiles` is missing required columns:
- `target_domain` (TEXT) - stores target university domain
- `target_keywords` (JSONB) - stores search keywords array
- `organization` (TEXT) - stores organization name
- `updated_at` (TIMESTAMPTZ) - tracks last update

## Solution (5 minutes)

### Step 1: Open Supabase SQL Editor
1. Go to: https://app.supabase.com/project/oyziawmetogvilefpepl/sql/new
2. Log in to your Supabase account

### Step 2: Run Migration SQL
1. Copy ALL contents from `DATABASE_MIGRATION.sql`
2. Paste into SQL Editor
3. Click "Run" button (or press Ctrl+Enter)

### Step 3: Verify Migration
You should see output like:
```
Success. 3 rows affected.  (for ALTER TABLE)
Success. X rows updated.    (for UPDATE existing rows)
Success. 1 rows inserted.   (for INSERT new profile)
```

Final SELECT query should show:
```
id                                   | email                    | target_domain | target_keywords
-------------------------------------|--------------------------|---------------|------------------
[your-user-id]                       | calvinwkatoroy@gmail.com| ui.ac.id      | ["ui.ac.id", "universitas indonesia"]
```

### Step 4: Test Features
1. **Refresh browser** (F5)
2. Go to **Settings page** → Should load without errors
3. Go to **Dashboard** → Click **QUICK SCAN** button → Should start scan
4. Check console logs → Should see 200 responses instead of 500

## Expected Results After Migration

### Settings Page ✅
- Loads without errors
- Shows current domain: `ui.ac.id`
- Shows current keywords: `ui.ac.id`, `universitas indonesia`
- Preset buttons work (UI, ITB, UGM)
- Can add/remove keywords
- Save button updates database

### Quick Scan ✅
- Button starts scan immediately
- Uses your saved settings from Settings page
- Shows scan notification
- No 500 errors

### Multi-University Support ✅
- Switch to ITB preset → Domain becomes `itb.ac.id`
- Switch to UGM preset → Domain becomes `ugm.ac.id`
- Quick Scan uses the selected university's domain
- Each user has independent settings

## Troubleshooting

### If migration fails:
1. Check table exists: `SELECT * FROM user_profiles LIMIT 1;`
2. Check your user ID: `SELECT id, email FROM auth.users;`
3. Manually create profile:
   ```sql
   INSERT INTO user_profiles (id, email, target_domain, target_keywords)
   VALUES (
     '[your-user-id-here]',
     'calvinwkatoroy@gmail.com',
     'ui.ac.id',
     '["ui.ac.id", "universitas indonesia"]'::jsonb
   );
   ```

### If Quick Scan still fails:
1. Check browser console for exact error
2. Verify settings saved: `SELECT * FROM user_profiles WHERE email='calvinwkatoroy@gmail.com';`
3. Check backend logs for detailed error message

## What This Enables

1. **Per-User Configuration**
   - Each user monitors their own university
   - Custom keywords per user
   - Personalized scan targets

2. **Multi-University Support**
   - UI students monitor `ui.ac.id`
   - ITB students monitor `itb.ac.id`
   - UGM students monitor `ugm.ac.id`

3. **One-Click Scanning**
   - Quick Scan button uses saved settings
   - No need to enter domain/keywords every time
   - Faster workflow

## Next Steps After Migration

1. ✅ Test Settings page - load, edit, save
2. ✅ Test Quick Scan - should use your settings
3. ✅ Try different university presets
4. ✅ Add custom keywords relevant to your target
5. ✅ Start monitoring for credential leaks!

---

**Need Help?** Check console logs in browser (F12) and backend terminal for detailed error messages.
