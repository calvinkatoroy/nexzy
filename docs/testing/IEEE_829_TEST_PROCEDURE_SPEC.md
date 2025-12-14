# IEEE 829 Test Procedure Specification - Nexzy OSINT Platform

**Project:** Nexzy - AI-Powered Credential Leak Detection System  
**Version:** 2.0  
**Date:** December 14, 2024  
**Test Plan Reference:** NEXZY-TP-001  
**Test Design Reference:** NEXZY-TDS-001  
**Document Status:** Complete

---

## 1. Test Procedure Specification Identifier
**NEXZY-TPS-001**

---

## 2. Purpose
This document provides detailed procedures for executing all test cases defined in the Test Case Specification. It ensures consistent, repeatable test execution across different environments and testers.

---

## 3. Test Environment Setup

### 3.1 Prerequisites
- Windows 10/11 with PowerShell 5.1+
- Docker Desktop 24.0+
- Node.js 18.0+
- Python 3.11+
- Git for version control
- Chrome/Firefox browser

### 3.2 Environment Preparation
```powershell
# Clone repository
git clone https://github.com/your-repo/nexzy.git
cd nexzy

# Start all services
.\start-all.ps1

# Wait for services to be ready (check logs)
# Frontend: http://localhost
# Backend: http://localhost:8001
# AI Service: http://localhost:8000
```

### 3.3 Test Data Setup
```powershell
# Backend test data
cd nexzy-backend
.\venv\Scripts\python insert_sample_alerts.py

# Frontend test accounts
# Use test@ui.ac.id / Test1234! for testing
```

---

## 4. Automated Test Execution

### 4.1 Backend Tests (pytest)
```powershell
# From project root
.\run-tests.ps1

# Or manually:
cd nexzy-backend
.\venv\Scripts\pytest tests/ -v --tb=short --html=report.html
```

**Expected Output:**
```
======================== test session starts ========================
collected 27 items
...
================= 24 passed, 3 skipped in 6.82s =================
```

### 4.2 Frontend Tests (Vitest)
```powershell
# From project root
.\run-tests.ps1

# Or manually:
cd nexzy-frontend
npm test
```

**Expected Output:**
```
✓ src/test/components/StatsCard.test.jsx (4 tests)
✓ src/test/components/Navigation.test.jsx (3 tests)
Test Files  2 passed (2)
Tests  7 passed (7)
```

---

## 5. Manual Test Execution Procedures

### 5.1 General Test Execution Guidelines

#### 5.1.1 Test Case Execution Steps
1. **Review Preconditions**: Ensure all prerequisites are met
2. **Prepare Test Data**: Set up required data state
3. **Execute Steps**: Follow numbered steps exactly
4. **Observe Results**: Record actual vs expected behavior
5. **Document Findings**: Note any deviations or issues
6. **Clean Up**: Reset environment for next test

#### 5.1.2 Result Recording
- **Pass**: Expected result matches actual result
- **Fail**: Expected result does not match actual result
- **Blocked**: Unable to execute due to external factors
- **Not Run**: Test not executed (time constraints, etc.)

#### 5.1.3 Evidence Collection
- Screenshots for UI tests
- API response logs
- Error messages
- Performance metrics
- Browser console logs

### 5.2 Authentication Test Procedures

#### Procedure AUTH-001: User Registration
**Test Cases:** TC-001 through TC-005

**Setup:**
1. Open fresh browser instance
2. Navigate to http://localhost/login
3. Ensure no user session exists

**Execution Steps:**
1. Click "Sign Up" or registration link
2. Enter test email: test@ui.ac.id
3. Enter password: Test1234!
4. Confirm password: Test1234!
5. Click "Create Account" button
6. Wait for email verification (if required)
7. Check dashboard access

**Verification:**
- Account creation success message
- Automatic login or verification prompt
- Dashboard access granted
- Database user record created

#### Procedure AUTH-002: User Login
**Test Cases:** TC-006 through TC-010

**Setup:**
1. Ensure test user exists (run AUTH-001 first)
2. Open fresh browser instance
3. Clear browser cache/cookies

**Execution Steps:**
1. Navigate to http://localhost/login
2. Enter email: test@ui.ac.id
3. Enter password: Test1234!
4. Click "Sign In" button
5. Wait for redirect to dashboard

**Verification:**
- Successful login message
- JWT token in localStorage
- Dashboard page loads
- User menu shows correct email

### 5.3 Dashboard Test Procedures

#### Procedure DASH-001: Statistics Display
**Test Cases:** TC-011 through TC-015

**Setup:**
1. Login as test user
2. Navigate to dashboard
3. Ensure sample data exists

**Execution Steps:**
1. Observe statistics cards loading
2. Wait for animation completion (2 seconds)
3. Verify numerical values display
4. Check trend indicators
5. Test responsive layout

**Verification:**
- All stats cards render correctly
- Values animate from 0 to target
- Trend arrows display correctly
- Mobile layout works

### 5.4 Scanning Test Procedures

#### Procedure SCAN-001: Credential Search
**Test Cases:** TC-016 through TC-021

**Setup:**
1. Login as test user
2. Navigate to search page
3. Ensure backend services running

**Execution Steps:**
1. Enter search query: test@ui.ac.id
2. Click "Scan" button
3. Wait for results (may take 10-30 seconds)
4. Review result list
5. Test pagination if >10 results

**Verification:**
- Search completes without errors
- Results display in table format
- AI scores show (0-100)
- Risk levels indicated
- Export functionality works

### 5.5 AI Scoring Test Procedures

#### Procedure AI-001: Vulnerability Assessment
**Test Cases:** TC-022 through TC-026

**Setup:**
1. Execute SCAN-001 to generate results
2. Ensure AI service is running

**Execution Steps:**
1. Review scan results with AI scores
2. Click on high-risk result
3. Verify score calculation (0-100)
4. Check mitigation recommendations
5. Test score filtering

**Verification:**
- Scores calculated correctly
- Risk levels: Low (0-30), Medium (31-70), High (71-100)
- Mitigation text generated
- Filtering works by risk level

### 5.6 Alert Management Procedures

#### Procedure ALERT-001: Alert CRUD Operations
**Test Cases:** TC-027 through TC-033

**Setup:**
1. Login as test user
2. Navigate to alerts page
3. Ensure sample alerts exist

**Execution Steps:**
1. View existing alerts list
2. Click "Create Alert" button
3. Fill alert form with test data
4. Save new alert
5. Edit existing alert
6. Update status and evidence
7. Delete test alert

**Verification:**
- Alert creation successful
- Edit form pre-populates data
- Status updates save correctly
- Evidence notes persist
- Deletion removes record

### 5.7 Real-time Feature Procedures

#### Procedure RT-001: WebSocket Notifications
**Test Cases:** TC-034 through TC-037

**Setup:**
1. Login as test user
2. Open browser developer tools
3. Navigate to dashboard

**Execution Steps:**
1. Monitor Network tab for WebSocket connection
2. Trigger scan operation in another tab
3. Observe real-time updates
4. Check notification display
5. Test connection recovery

**Verification:**
- WebSocket connects successfully
- Real-time updates appear
- Notifications show in UI
- Connection handles disconnections

### 5.8 Security Test Procedures

#### Procedure SEC-001: Input Validation
**Test Cases:** TC-038 through TC-041

**Setup:**
1. Login as test user
2. Prepare malicious input strings

**Execution Steps:**
1. Attempt SQL injection in search field
2. Try XSS in alert notes
3. Test large input payloads
4. Check rate limiting with rapid requests

**Verification:**
- Malicious input rejected
- Error messages appropriate
- No data leakage
- Rate limiting enforced

### 5.9 Performance Test Procedures

#### Procedure PERF-001: Load Testing
**Test Cases:** TC-042 through TC-044

**Setup:**
1. Ensure clean database state
2. Prepare load testing tools

**Execution Steps:**
1. Execute 100 concurrent scan requests
2. Monitor response times
3. Check memory usage
4. Verify error rate <5%

**Verification:**
- Response time <2 seconds average
- No memory leaks
- Error rate within limits
- System remains stable

### 5.10 Docker Deployment Procedures

#### Procedure DOCKER-001: Container Testing
**Test Cases:** TC-045 through TC-049

**Setup:**
1. Ensure Docker Desktop running
2. Clean previous containers

**Execution Steps:**
1. Run .\start-all.ps1
2. Check container status: docker ps
3. Verify service health endpoints
4. Test inter-container communication
5. Check logs for errors

**Verification:**
- All containers start successfully
- Health checks pass
- Services communicate correctly
- No container crashes

---

## 6. Test Execution Logs

### 6.1 Log Format
Each test execution must record:
- Test Case ID
- Execution Date/Time
- Tester Name
- Environment Details
- Preconditions Met
- Steps Executed
- Actual Results
- Pass/Fail Status
- Defects Found
- Evidence Files

### 6.2 Log Storage
- Digital logs in `docs/testing/logs/`
- Screenshots in `docs/testing/screenshots/`
- Test data backups in `docs/testing/data/`

---

## 7. Defect Reporting

### 7.1 Defect Discovery
When test fails:
1. Document exact failure conditions
2. Capture screenshots/videos
3. Record environment details
4. Note reproduction steps
5. Assign severity/priority

### 7.2 Defect Tracking
- Use GitHub Issues for defect tracking
- Label: bug, test-failure, critical/high/medium/low
- Assign to appropriate developer
- Track resolution progress

---

## 8. Test Completion Criteria

### 8.1 Individual Test Completion
- All steps executed
- Results documented
- Evidence collected
- Status recorded

### 8.2 Test Suite Completion
- All planned tests executed
- Pass rate meets requirements (95%+)
- Critical defects resolved
- Documentation complete

---

## 9. Contingency Procedures

### 9.1 Test Blockers
If test cannot be executed:
1. Document blocking condition
2. Attempt workaround
3. Report as blocked
4. Re-schedule when blocker resolved

### 9.2 Environment Failures
If environment issues occur:
1. Document failure details
2. Attempt environment recovery
3. Report infrastructure issues
4. Continue with available tests

### 9.3 Time Constraints
If time limited:
1. Execute critical/high priority tests first
2. Document remaining tests as "Not Run"
3. Prioritize based on risk assessment

---

## 10. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | Calvin Wkatoroy | _________ | _________ |
| Test Engineer | Calvin Wkatoroy | _________ | _________ |
| Quality Assurance | Calvin Wkatoroy | _________ | _________ |

---

## 11. References

1. IEEE 829-2008 Test Procedure Specification
2. Nexzy Test Case Specification (IEEE_829_TEST_CASES.md)
3. Nexzy Testing Guide (TESTING_GUIDE.md)
4. Pytest Documentation
5. React Testing Library Documentation

---

## 12. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 14, 2024 | Calvin Wkatoroy | Initial creation |
| 2.0 | Dec 14, 2024 | Calvin Wkatoroy | Updated for v2.0 procedures |