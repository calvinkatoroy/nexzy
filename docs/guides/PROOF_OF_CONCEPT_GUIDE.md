# 🧪 Proof of Concept Testing Guide
# Cara Posting Dummy Data untuk Test Detection System

## ⚠️ PENTING: Data Dummy AI-Generated

**Semua data dibawah adalah FAKE/AI-generated:**
- ✅ Tidak ada NPM/email/nomor telepon asli
- ✅ Aman untuk di-post public
- ✅ Hanya untuk testing detection
- ✅ Format terlihat real tapi data palsu

---

## 📋 Sample Data 1: "Database Leak Simulation"

```
========================================
UI Student Database Export - 2024
========================================
Exported: 2024-11-15 03:42:17 UTC
Total Records: 127
Status: BACKUP_TEST

[Student Records]

NPM: 2106729184
Name: Ahmad Rizki Pratama
Email: ahmad.rizki91@ui.ac.id
Phone: +62 812-3456-7891
Program: Computer Science
Password: Ui2024!Ahmad
API_Token: ui_token_9a8f7e6d5c4b3a2f1e0d9c8b
Address: Jl. Margonda Raya No. 45, Depok, Jawa Barat

NPM: 2106729185
Name: Siti Nurhaliza Putri
Email: siti.nurhaliza@ui.ac.id
Phone: +62 813-9876-5432
Program: Information Systems
Password: SitiUI@2024
API_Token: ui_token_8b7c6d5e4f3a2b1c0d9e8f7a
Address: Jl. Salemba Raya No. 12, Jakarta Pusat

NPM: 2106729186
Name: Budi Santoso Wijaya
Email: budi.santoso@ui.ac.id
Phone: +62 815-2468-1357
Program: Data Science
Password: Budi_Pass123!
API_Token: ui_token_7c6d5e4f3a2b1c0d9e8f7a6b
Address: Jl. Prof. Dr. Satrio No. 88, Jakarta Selatan

NPM: 2106729187
Name: Dewi Lestari Kusuma
Email: dewi.lestari@ui.ac.id
Phone: +62 821-7654-3210
Program: Software Engineering
Password: DewiUI2024$
API_Token: ui_token_6d5e4f3a2b1c0d9e8f7a6b5c
Address: Jl. Thamrin No. 23, Jakarta Pusat

NPM: 2106729188
Name: Eko Prasetyo Nugroho
Email: eko.prasetyo@ui.ac.id
Phone: +62 822-8765-4321
Program: Cybersecurity
Password: Eko@UI_2024
API_Token: ui_token_5e4f3a2b1c0d9e8f7a6b5c4d
Address: Jl. Gatot Subroto No. 67, Jakarta Selatan

[Database Info]
Server: db-student-prod-01.ui.ac.id
Database: student_records_2024
Backup_Date: 2024-11-15
Admin_Email: db.admin@ui.ac.id
Admin_Pass: UIAdmin@Secure2024!

[WARNING]
This is a test backup file.
Do NOT share publicly.
For internal use only.

========================================
```

---

## 📋 Sample Data 2: "API Key Leak Simulation"

```
# UI Academic Portal - Development Config
# Generated: 2024-12-10

DATABASE_URL=postgresql://ui_admin:UIdb_Pass2024@db.ui.ac.id:5432/academic_portal
REDIS_URL=redis://redis.ui.ac.id:6379
SESSION_SECRET=ui_session_9f8e7d6c5b4a3f2e1d0c9b8a

# Student API Keys
STUDENT_API_KEYS=[
  "ui_api_2106729189_f9e8d7c6b5a4f3e2d1c0b9a8",
  "ui_api_2106729190_e8d7c6b5a4f3e2d1c0b9a8f7",
  "ui_api_2106729191_d7c6b5a4f3e2d1c0b9a8f7e6"
]

# Student Emails
REGISTERED_USERS=[
  "farhan.hakim@ui.ac.id",
  "nadia.putri@ui.ac.id",
  "reza.maulana@ui.ac.id"
]

# Admin Credentials
ADMIN_USERNAME=admin_ui
ADMIN_PASSWORD=UIPortal@2024Secure!
ADMIN_EMAIL=admin.portal@ui.ac.id

# JWT Settings
JWT_SECRET=ui_jwt_secret_a9b8c7d6e5f4a3b2c1d0e9f8
JWT_EXPIRY=86400

# Third Party APIs
GOOGLE_API_KEY=AIzaSyC_FAKE_KEY_ui_test_9f8e7d6c5b4a
AWS_ACCESS_KEY=AKIAFAKE_UI_TEST_9F8E7D6C5B4A
AWS_SECRET_KEY=FakeSecretKey_UI_2024_Testing_Only

# Contact
IT_SUPPORT=support@ui.ac.id
PHONE=+62 21-786-7222

========================================
```

---

## 📋 Sample Data 3: "Credential List Simulation"

```
UI Student Portal - Active Accounts 2024

LOGIN CREDENTIALS:

1. NPM: 2106729192
   Email: agus.wijaya@ui.ac.id
   Password: Agus2024_UI!
   Phone: +62 856-1234-5678

2. NPM: 2106729193
   Email: rina.sari@ui.ac.id
   Password: RinaSari@UI24
   Phone: +62 857-8765-4321

3. NPM: 2106729194
   Email: doni.prasetya@ui.ac.id
   Password: Doni_UIPass123
   Phone: +62 858-2468-1357

4. NPM: 2106729195
   Email: maya.lestari@ui.ac.id
   Password: Maya@UI2024!
   Phone: +62 859-7531-2468

5. NPM: 2106729196
   Email: andi.firmansyah@ui.ac.id
   Password: AndiUI_2024$
   Phone: +62 851-9876-5432

========================================
INTERNAL USE ONLY
DO NOT DISTRIBUTE
========================================
```

---

## 🌐 Cara 1: Post ke Pastebin (Clearnet)

### Step-by-Step:

1. **Buka Pastebin:**
   - Go to: https://pastebin.com

2. **Paste Data:**
   - Copy salah satu sample data diatas
   - Paste di text area
   - Judul: Contoh: "UI Database Backup Test 2024"

3. **Settings:**
   - **Paste Exposure:** Pilih **"Unlisted"** (RECOMMENDED!)
     - ✅ **Unlisted** = Hanya bisa diakses via link langsung (TERBAIK untuk testing)
     - Public = Muncul di recent pastes tapi cepat hilang (scroll dalam 5-10 menit)
     - Private = Butuh login (skip)
   
   - **Paste Expiration:** Pilih "1 Week" atau "1 Month"
   
   - **Syntax Highlighting:** Pilih "None" atau "Text"

4. **Create Paste:**
   - Click "Create New Paste"
   - **COPY URL** yang dihasilkan (e.g., https://pastebin.com/aBcD1234)
   - **SAVE URL** ini untuk testing!

5. **Test Detection (Method A - Direct URL):**
   - Buka Nexzy dashboard
   - Click "NEW SCAN"
   - **ADD DIRECT URLs**: Paste your 3 pastebin URLs
   - Keywords: `ui.ac.id` (optional)
   - Start scan
   - Nexzy akan scan URL yang kamu kasih langsung!

6. **Test Detection (Method B - Auto Discovery):**
   - Click "NEW SCAN"
   - **JANGAN isi URLs** (leave empty)
   - Keywords: `ui.ac.id`
   - Enable: Auto Discover, Author Crawling
   - Start scan
   - Nexzy akan search recent pastes (hanya jika paste masih di recent feed)

---

## 🕸️ Cara 2: Post ke Darkweb Paste Site (Recommended)

### Option A: Stronghold Paste (via Clearnet Mirror)

1. **Buka Stronghold:**
   - URL: https://strongerw2ise74v3duebgsvug4mehyhlpa7f6kfwnas7zofs3kov7yd.onion.ly
   - (Ini clearnet mirror dari .onion site)

2. **Create Paste:**
   - Paste salah satu sample data
   - Title: "Database Export 2024"
   - No login required

3. **Settings:**
   - Expiration: 1 week
   - Public/Unlisted (jika ada pilihan)

4. **Submit:**
   - Click submit/post
   - Copy URL hasil

5. **Test:**
   - Scan dengan keywords: `ui.ac.id`
   - Enable darkweb search
   - Paste akan terdeteksi di darkweb results!

---

### Option B: DarkPaste (via Clearnet Mirror)

1. **Buka DarkPaste:**
   - URL: https://paste2vljbekqqa3k555ihc2c4k62kzqjfbgvqk6zkupcdnlqsx4biqd.onion.pet

2. **Create Paste:**
   - Same steps as above
   - Copy URL

---

### Option C: Ghostbin / Alternative

1. **Ghostbin:**
   - URL: https://ghostbin.com
   - Anonymous paste site
   - No registration needed
   
2. **Post Data:**
   - Paste content
   - Set expiration
   - Create paste

---

## 🧪 Testing Workflow

### Full Test Scenario:

1. **Preparation:**
   - Have all 3 services running:
     - Backend (port 8000)
     - Frontend (port 5174)
     - AI Service (port 8001) with Gemini API key

2. **Post Test Data:**
   - Post Sample Data 1 ke Pastebin (unlisted)
   - Post Sample Data 2 ke Stronghold Paste
   - Post Sample Data 3 ke DarkPaste or Ghostbin

3. **Run Scan (Method: Direct URLs):**
   ```
   URLs: 
   - https://pastebin.com/xxxxx (your paste 1)
   - https://pastebin.com/yyyyy (your paste 2)
   - https://pastebin.com/zzzzz (your paste 3)
   
   Keywords: ui.ac.id (optional)
   ✅ Enable Author Crawling (optional)
   ✅ Enable Darkweb Search (optional)
   ```
   
   **OR Method: Auto Discovery (jika paste masih recent):**
   ```
   URLs: (leave empty)
   Keywords: ui.ac.id, 2106729
   ✅ Auto Discover
   ✅ Enable Author Crawling
   ✅ Enable Darkweb Search
   ```

4. **Expected Results:**
   - 🔍 Scanner finds all 3 pastes
   - 📧 Detects fake emails (ahmad.rizki91@ui.ac.id, etc.)
   - 🔑 Detects fake passwords and API keys
   - 📱 Detects fake phone numbers
   - 🎯 Creates HIGH/CRITICAL alerts
   - 🤖 AI analyzes and gives vulnerability score
   - 🛡️ AI generates mitigation recommendations

5. **Check Alert Details:**
   - Open alert in dashboard
   - Verify AI Summary present
   - Verify Risk Assessment
   - **Verify Mitigation Recommendations section** (green box)
   - Check detected signals: passwords, emails, pii, etc.

---

## 📊 Expected Detection Output

### What Nexzy Should Detect:

**From Sample Data 1:**
- ✅ 5 NPM numbers (2106729184-2106729188)
- ✅ 5 @ui.ac.id emails
- ✅ 5 passwords (plaintext)
- ✅ 5 API tokens
- ✅ 5 phone numbers
- ✅ 5 addresses
- ✅ Database credentials
- ✅ Admin credentials

**Severity:** CRITICAL (85-95 score)

**AI Mitigation Should Include:**
```
IMMEDIATE (0-24h):
• Force password reset for all 5 accounts
• Revoke all API tokens immediately
• Disable admin account access
• Contact paste site for removal
• Alert affected students

SHORT-TERM (1-7 days):
• Audit database access logs
• Implement password hashing
• Enable 2FA
• Review security configs

LONG-TERM:
• Automated leak monitoring
• Security training
• Database encryption
• Incident procedures

NOTIFY:
• IT Security Team
• Data Protection Officer
• Students (after mitigation)
• University leadership
```

---

## 🎯 Proof Points

### What This Proves:

1. ✅ **Clearnet Detection:**
   - Finds unlisted pastes on pastebin.com
   - Not limited to public/recent pastes

2. ✅ **Darkweb Detection:**
   - Finds pastes on .onion sites via mirrors
   - Searches multiple darkweb sources

3. ✅ **PII Detection:**
   - Indonesian student IDs (NPM)
   - Email addresses
   - Phone numbers
   - Residential addresses

4. ✅ **Credential Detection:**
   - Passwords (plaintext)
   - API keys/tokens
   - Database credentials
   - Admin accounts

5. ✅ **AI Analysis:**
   - Vulnerability scoring (0-100)
   - Risk assessment
   - Signal detection
   - **Mitigation recommendations**

6. ✅ **Real-time Alerts:**
   - WebSocket notifications
   - Severity classification
   - Detailed evidence
   - Actionable recommendations

---

## 🔒 Safety Notes

**Remember:**
- ✅ All data is FAKE/AI-generated
- ✅ No real student data used
- ✅ Safe to post publicly
- ✅ For testing purposes only
- ✅ Can delete pastes after testing

**Cleanup After Testing:**
- Delete pastes from pastebin/paste sites
- Or let them expire (1 week/1 month)
- Archive test results in Nexzy

---

## 📸 Screenshot Checklist

**For Proof of Concept, capture:**

1. ✅ Paste site showing posted content
2. ✅ Nexzy scan in progress (WebSocket updates)
3. ✅ Scan results showing found pastes
4. ✅ Alert created (HIGH/CRITICAL severity)
5. ✅ Alert details showing:
   - AI vulnerability score
   - AI summary
   - Risk assessment
   - Detected signals
   - **Mitigation recommendations** (green box)
6. ✅ Credential table showing detected data
7. ✅ Source URL linking back to paste

---

## 🚀 Quick Commands

**Start all services:**

```powershell
# Terminal 1 - AI Service
cd "c:\Users\calvi\Documents\My Projects\nexzy\ai-service"
.\start.ps1

# Terminal 2 - Backend
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-backend"
.\start.ps1

# Terminal 3 - Frontend
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-frontend"
npm run dev
```

**Then:**
1. Post dummy data to paste sites
2. Open http://localhost:5174
3. Run scan with keywords
4. Watch magic happen! ✨

---

**Goal:** Demonstrate Nexzy dapat mendeteksi credential leaks di public & darkweb pastes, menganalisis dengan AI, dan memberikan mitigation recommendations yang actionable.

**Result:** Proof of concept bahwa sistem bekerja end-to-end! 🎉
