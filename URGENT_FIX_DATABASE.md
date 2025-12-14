# 🚨 CRITICAL: Run Database Migration First!

## The Error You're Seeing:
```
column alerts.vulnerability_score does not exist
```

This means the database doesn't have the new columns yet.

## Fix in 3 Steps:

### 1. Open Supabase Dashboard
Go to: https://app.supabase.com

### 2. Run the Migration SQL
- Click on your Nexzy project
- Go to **SQL Editor** (left sidebar)
- Click **New Query**
- Copy ALL contents from: `nexzy-backend/COMPREHENSIVE_UPGRADES.sql`
- Paste into SQL Editor
- Click **Run** (or press Ctrl+Enter)

### 3. Verify Migration Succeeded
Run this check query:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'alerts' 
AND column_name IN ('vulnerability_score', 'ai_signals', 'ai_confidence', 'ai_mitigation');
```

Should return 4 rows:
- vulnerability_score | double precision
- ai_signals | ARRAY
- ai_confidence | double precision  
- ai_mitigation | text

---

## After Migration:
1. Refresh your frontend (Ctrl+Shift+R)
2. All errors should disappear
3. Dashboard should load with real stats

---

## If Migration Fails:

Check if alerts table exists:
```sql
SELECT * FROM alerts LIMIT 1;
```

If table doesn't exist, run the full schema first:
```sql
-- Copy from nexzy-backend/supabase_schema.sql
```

Then run COMPREHENSIVE_UPGRADES.sql
