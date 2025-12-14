# IEEE 829 Test Cases - Nexzy OSINT Platform

**Project:** Nexzy - AI-Powered Credential Leak Detection System  
**Version:** 2.0  
**Date:** December 14, 2024  
**Test Plan Reference:** NEXZY-TP-001

---

## Test Case Format

Each test case includes:
- **TC-ID**: Unique identifier
- **Feature**: Feature being tested
- **Priority**: Critical / High / Medium / Low
- **Type**: Functional / Security / Performance / UI
- **Preconditions**: Setup required
- **Test Steps**: Detailed steps
- **Expected Result**: What should happen
- **Actual Result**: (To be filled during execution)
- **Status**: Pass / Fail / Blocked / Not Run

---

## 1. Authentication & Authorization Tests

### TC-001: User Registration
- **Feature**: User Authentication
- **Priority**: Critical
- **Type**: Functional
- **Preconditions**: Fresh browser, Supabase configured
- **Test Steps**:
  1. Navigate to http://localhost/login
  2. Click "Sign Up" or similar
  3. Enter email: test@ui.ac.id
  4. Enter password: Test1234!
  5. Click "Create Account"
- **Expected Result**: User account created, redirected to dashboard
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-002: User Login with Valid Credentials
- **Feature**: User Authentication
- **Priority**: Critical
- **Type**: Functional
- **Preconditions**: User account exists
- **Test Steps**:
  1. Navigate to http://localhost/login
  2. Enter email: test@ui.ac.id
  3. Enter password: Test1234!
  4. Click "Login"
- **Expected Result**: User logged in, redirected to dashboard
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-003: User Login with Invalid Password
- **Feature**: User Authentication
- **Priority**: High
- **Type**: Security
- **Preconditions**: User account exists
- **Test Steps**:
  1. Navigate to http://localhost/login
  2. Enter email: test@ui.ac.id
  3. Enter password: WrongPassword123
  4. Click "Login"
- **Expected Result**: Error message "Invalid login credentials"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-004: Protected Route Access Without Authentication
- **Feature**: Authorization
- **Priority**: Critical
- **Type**: Security
- **Preconditions**: User not logged in
- **Test Steps**:
  1. Clear browser cookies
  2. Navigate to http://localhost/dashboard
- **Expected Result**: Redirected to login page
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-005: User Logout
- **Feature**: User Authentication
- **Priority**: High
- **Type**: Functional
- **Preconditions**: User logged in
- **Test Steps**:
  1. Click profile menu
  2. Click "Logout"
- **Expected Result**: User logged out, redirected to login, session cleared
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 2. Dashboard & Statistics Tests

### TC-010: Dashboard Loads Successfully
- **Feature**: Dashboard
- **Priority**: Critical
- **Type**: Functional
- **Preconditions**: User logged in
- **Test Steps**:
  1. Navigate to /dashboard
  2. Wait for data to load
- **Expected Result**: Dashboard displays with 4 stat cards (Total Alerts, New Alerts, Critical Alerts, Credentials Leaked)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-011: Stats Cards Display Correct Data
- **Feature**: Dashboard Statistics
- **Priority**: High
- **Type**: Functional
- **Preconditions**: Database has alerts
- **Test Steps**:
  1. Check Total Alerts count
  2. Check New Alerts count (status='new')
  3. Check Critical Alerts count (severity='CRITICAL')
  4. Check Credentials Leaked count
- **Expected Result**: All counts match database query results
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-012: Stats Cards Animate on Load
- **Feature**: Dashboard UI
- **Priority**: Low
- **Type**: UI
- **Preconditions**: Dashboard loaded
- **Test Steps**:
  1. Refresh dashboard page
  2. Observe stat card numbers
- **Expected Result**: Numbers animate from 0 to actual value over ~1 second
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-013: Trend Graph Displays Last 30 Days
- **Feature**: Dashboard Trend Graph
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Alerts exist in last 30 days
- **Test Steps**:
  1. Scroll to trend graph section
  2. Check X-axis labels
  3. Check data points
- **Expected Result**: Graph shows last 30 days with correct alert counts per day
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-014: Recent Alerts Table Shows Latest 10
- **Feature**: Dashboard Recent Alerts
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Database has alerts
- **Test Steps**:
  1. Scroll to recent alerts section
  2. Count table rows
  3. Verify alerts are sorted by date (newest first)
- **Expected Result**: Shows 10 most recent alerts, newest first
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 3. Credential Scanning Tests

### TC-020: Create Email Scan
- **Feature**: Credential Scanning
- **Priority**: Critical
- **Type**: Functional
- **Preconditions**: User logged in
- **Test Steps**:
  1. Navigate to /search or click "New Scan"
  2. Select "Email" scan type
  3. Enter: test@ui.ac.id
  4. Click "Start Scan"
- **Expected Result**: Scan created, progress shown, results appear
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-021: Create Domain Scan
- **Feature**: Credential Scanning
- **Priority**: High
- **Type**: Functional
- **Preconditions**: User logged in
- **Test Steps**:
  1. Navigate to /search
  2. Select "Domain" scan type
  3. Enter: ui.ac.id
  4. Click "Start Scan"
- **Expected Result**: Scan searches for *@ui.ac.id pattern
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-022: Scan Validates Email Format
- **Feature**: Input Validation
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: User on scan page
- **Test Steps**:
  1. Enter invalid email: "notanemail"
  2. Click "Start Scan"
- **Expected Result**: Error message "Invalid email format"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-023: Scan Rejects Empty Query
- **Feature**: Input Validation
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: User on scan page
- **Test Steps**:
  1. Leave query field empty
  2. Click "Start Scan"
- **Expected Result**: Error message "Query cannot be empty"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-024: Scan Progress Updates in Real-time
- **Feature**: WebSocket Updates
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Scan started
- **Test Steps**:
  1. Start a scan
  2. Watch progress indicator
- **Expected Result**: Progress updates without page refresh (10%, 50%, 100%)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-025: One-Click Scan from Landing Page
- **Feature**: Quick Scan
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: User on landing page
- **Test Steps**:
  1. Navigate to landing page
  2. Enter email in hero section input
  3. Click "Scan Now"
- **Expected Result**: Redirected to login or scan starts (if logged in)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 4. AI Scoring Tests

### TC-030: High-Risk Content Gets High Score
- **Feature**: RoBERTa AI Scoring
- **Priority**: Critical
- **Type**: Functional
- **Preconditions**: AI service running
- **Test Steps**:
  1. Create scan that finds obvious credential leak
  2. Check vulnerability_score in results
- **Expected Result**: Score > 80 for "password=admin username=root"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-031: Low-Risk Content Gets Low Score
- **Feature**: RoBERTa AI Scoring
- **Priority**: High
- **Type**: Functional
- **Preconditions**: AI service running
- **Test Steps**:
  1. Create scan with benign text
  2. Check vulnerability_score
- **Expected Result**: Score < 30 for "Hello, this is a test message"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-032: Severity Circle Shows Correct Score
- **Feature**: Alert Details UI
- **Priority**: Medium
- **Type**: UI
- **Preconditions**: Alert with score 88.5 exists
- **Test Steps**:
  1. Navigate to alert details
  2. Check severity circle number
- **Expected Result**: Circle displays "88.5/100" with animation
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-033: Mitigation Recommendations Generated
- **Feature**: Gemini AI Mitigation
- **Priority**: High
- **Type**: Functional
- **Preconditions**: Alert exists
- **Test Steps**:
  1. Open alert details
  2. Check mitigation section
- **Expected Result**: Mitigation steps displayed (3-5 actionable items)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-034: AI Service Health Check
- **Feature**: AI Service
- **Priority**: High
- **Type**: Integration
- **Preconditions**: AI service container running
- **Test Steps**:
  1. Navigate to http://localhost:8000/health
  2. Check response
- **Expected Result**: {"status": "healthy", "model": "Harafu/roberta-risk-next"}
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 5. Alert Management Tests

### TC-040: View All Alerts
- **Feature**: Alert List
- **Priority**: High
- **Type**: Functional
- **Preconditions**: User logged in, alerts exist
- **Test Steps**:
  1. Navigate to /alerts
  2. Check alert table
- **Expected Result**: All alerts displayed in table format
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-041: Filter Alerts by Status
- **Feature**: Alert Filtering
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Alerts with different statuses exist
- **Test Steps**:
  1. Go to /alerts
  2. Select "New" filter
  3. Check results
- **Expected Result**: Only alerts with status='new' shown
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-042: Filter Alerts by Severity
- **Feature**: Alert Filtering
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Alerts with different severities exist
- **Test Steps**:
  1. Go to /alerts
  2. Select "CRITICAL" severity filter
  3. Check results
- **Expected Result**: Only CRITICAL severity alerts shown
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-043: Update Alert Status
- **Feature**: Alert Status Management
- **Priority**: High
- **Type**: Functional
- **Preconditions**: Alert exists with status='new'
- **Test Steps**:
  1. Open alert details
  2. Change status to "investigating"
  3. Save
- **Expected Result**: Status updated in database, UI reflects change
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-044: Add Evidence Notes
- **Feature**: Evidence Management
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Alert details page open
- **Test Steps**:
  1. Scroll to evidence section
  2. Enter note: "Verified with security team"
  3. Click "Save"
- **Expected Result**: Note saved, displayed with timestamp
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-045: View Alert Source Link
- **Feature**: Alert Details
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Alert with source_url exists
- **Test Steps**:
  1. Open alert details
  2. Find source URL link
  3. Click link
- **Expected Result**: Opens source URL in new tab (Pastebin/dark web)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-046: View Content Snippet Preview
- **Feature**: Content Preview
- **Priority**: Low
- **Type**: Functional
- **Preconditions**: Alert with content_snippet exists
- **Test Steps**:
  1. Open alert details
  2. Scroll to content preview section
- **Expected Result**: First 500 characters of paste content shown
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 6. Real-time Notification Tests

### TC-050: WebSocket Connection Established
- **Feature**: WebSocket
- **Priority**: High
- **Type**: Integration
- **Preconditions**: User logged in
- **Test Steps**:
  1. Open browser dev tools
  2. Navigate to dashboard
  3. Check console for WebSocket connection
- **Expected Result**: "✅ WebSocket connected" in console
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-051: Receive Scan Progress Updates
- **Feature**: Real-time Updates
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: WebSocket connected
- **Test Steps**:
  1. Start a new scan
  2. Watch for updates without refreshing
- **Expected Result**: Progress updates appear in real-time
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-052: Receive New Alert Notification
- **Feature**: Real-time Alerts
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: WebSocket connected, scan running
- **Test Steps**:
  1. Start scan
  2. Wait for alert to be created
  3. Check for toast notification
- **Expected Result**: Toast notification appears "New alert created!"
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-053: WebSocket Reconnects After Disconnect
- **Feature**: WebSocket Resilience
- **Priority**: Low
- **Type**: Integration
- **Preconditions**: WebSocket connected
- **Test Steps**:
  1. Stop backend container
  2. Wait 5 seconds
  3. Restart backend container
  4. Check console
- **Expected Result**: WebSocket automatically reconnects
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 7. Dark Web Scanning Tests

### TC-060: Dark Web Scan Started
- **Feature**: Dark Web Scanning
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: User logged in, Tor configured
- **Test Steps**:
  1. Navigate to /search
  2. Check "Include Dark Web" option
  3. Start scan
- **Expected Result**: Scan includes .onion results
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-061: Dark Web Results Displayed
- **Feature**: Dark Web Results
- **Priority**: Medium
- **Type**: Functional
- **Preconditions**: Dark web scan completed
- **Test Steps**:
  1. View scan results
  2. Check source column
- **Expected Result**: Some results show "Dark Web" as source
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 8. Pastebin Search Tests

### TC-070: Pastebin Search via Google CSE
- **Feature**: Pastebin Search
- **Priority**: High
- **Type**: Integration
- **Preconditions**: Google CSE configured
- **Test Steps**:
  1. Start email scan
  2. Check results
- **Expected Result**: Pastebin results included if available
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-071: Pastebin Rate Limiting Handled
- **Feature**: API Rate Limiting
- **Priority**: Low
- **Type**: Integration
- **Preconditions**: Multiple scans running
- **Test Steps**:
  1. Start 10 scans rapidly
  2. Check for rate limit errors
- **Expected Result**: Graceful handling with retry or queue
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 9. Performance Tests

### TC-080: Dashboard Loads Under 2 Seconds
- **Feature**: Performance
- **Priority**: Medium
- **Type**: Performance
- **Preconditions**: Database has <1000 alerts
- **Test Steps**:
  1. Open browser dev tools (Network tab)
  2. Navigate to /dashboard
  3. Measure load time
- **Expected Result**: Page fully loaded < 2000ms
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-081: API Response Time < 500ms
- **Feature**: API Performance
- **Priority**: Medium
- **Type**: Performance
- **Preconditions**: Backend running
- **Test Steps**:
  1. Use Postman or curl
  2. Call GET /api/stats
  3. Measure response time
- **Expected Result**: Response time < 500ms
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-082: Handle 10 Concurrent Users
- **Feature**: Scalability
- **Priority**: Low
- **Type**: Performance
- **Preconditions**: 10 test accounts
- **Test Steps**:
  1. Open 10 browser tabs
  2. Login with different accounts simultaneously
  3. All perform scan
- **Expected Result**: All scans complete without errors
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 10. Security Tests

### TC-090: SQL Injection Prevention
- **Feature**: Security
- **Priority**: Critical
- **Type**: Security
- **Preconditions**: User on scan page
- **Test Steps**:
  1. Enter: `'; DROP TABLE alerts; --` in query
  2. Submit scan
- **Expected Result**: Input sanitized, no database damage
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-091: XSS Prevention
- **Feature**: Security
- **Priority**: Critical
- **Type**: Security
- **Preconditions**: Alert details page
- **Test Steps**:
  1. Add note: `<script>alert('XSS')</script>`
  2. Save and refresh
- **Expected Result**: Script not executed, displayed as text
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-092: RLS Policies Enforced
- **Feature**: Database Security
- **Priority**: Critical
- **Type**: Security
- **Preconditions**: 2 user accounts with different alerts
- **Test Steps**:
  1. Login as user A
  2. Try to access user B's alert via direct URL
- **Expected Result**: Access denied (Supabase RLS blocks)
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-093: JWT Token Expiration
- **Feature**: Session Security
- **Priority**: High
- **Type**: Security
- **Preconditions**: User logged in
- **Test Steps**:
  1. Wait for token expiration (default 1 hour)
  2. Try to access protected page
- **Expected Result**: Redirected to login, token refresh or re-authentication required
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## 11. Docker Deployment Tests

### TC-100: All Containers Start Successfully
- **Feature**: Docker Deployment
- **Priority**: Critical
- **Type**: Integration
- **Preconditions**: Docker compose file ready
- **Test Steps**:
  1. Run: `docker-compose up -d --build`
  2. Check: `docker-compose ps`
- **Expected Result**: All 3 containers (ai-service, backend, frontend) running and healthy
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-101: Container Health Checks Pass
- **Feature**: Docker Health Checks
- **Priority**: High
- **Type**: Integration
- **Preconditions**: Containers running
- **Test Steps**:
  1. Wait 60 seconds after start
  2. Run: `docker-compose ps`
  3. Check health status
- **Expected Result**: All containers show "healthy" status
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-102: Frontend Accessible on Port 80
- **Feature**: Docker Networking
- **Priority**: High
- **Type**: Integration
- **Preconditions**: Docker containers running
- **Test Steps**:
  1. Navigate to http://localhost
- **Expected Result**: Frontend loads correctly
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-103: Backend Accessible on Port 8001
- **Feature**: Docker Networking
- **Priority**: High
- **Type**: Integration
- **Preconditions**: Docker containers running
- **Test Steps**:
  1. Navigate to http://localhost:8001/docs
- **Expected Result**: FastAPI docs page loads
- **Actual Result**: _________
- **Status**: ⏳ Not Run

### TC-104: AI Service Accessible on Port 8000
- **Feature**: Docker Networking
- **Priority**: High
- **Type**: Integration
- **Preconditions**: Docker containers running
- **Test Steps**:
  1. Navigate to http://localhost:8000/health
- **Expected Result**: {"status": "healthy"}
- **Actual Result**: _________
- **Status**: ⏳ Not Run

---

## Test Execution Summary

**Total Test Cases**: 75  
**Executed**: 0  
**Passed**: 0  
**Failed**: 0  
**Blocked**: 0  
**Not Run**: 75

**Pass Rate**: 0%  
**Last Updated**: December 14, 2024

---

## Notes
- Execute automated tests first: `pytest` and `npm run test`
- Manual tests should include screenshots
- Document all bugs in separate defect report
- Update Actual Result and Status during execution
