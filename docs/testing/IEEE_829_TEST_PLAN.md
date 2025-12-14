# IEEE 829 Test Plan - Nexzy OSINT Platform

**Project:** Nexzy - AI-Powered Credential Leak Detection System  
**Version:** 2.0  
**Date:** December 14, 2024  
**Author:** Calvin Wkatoroy  
**Document Status:** Draft

---

## 1. Test Plan Identifier
**NEXZY-TP-001**

---

## 2. Introduction

### 2.1 Purpose
This document describes the comprehensive testing strategy for the Nexzy OSINT platform, an AI-powered credential leak detection system. The testing ensures all features work correctly, securely, and meet user requirements.

### 2.2 Scope
Testing covers:
- Backend API endpoints (FastAPI)
- Frontend UI components (React 19)
- AI scoring system (RoBERTa + Gemini)
- Database operations (Supabase PostgreSQL)
- Real-time features (WebSocket)
- Security (Authentication, Authorization, RLS)
- Docker deployment

### 2.3 System Overview
Nexzy is a 3-tier web application:
- **Frontend**: React 19.2 + Vite + TailwindCSS (Port 5173/80)
- **Backend**: FastAPI + Python 3.11 (Port 8001)
- **AI Service**: RoBERTa + Google Gemini (Port 8000)
- **Database**: Supabase PostgreSQL with RLS

---

## 3. Test Items

### 3.1 Features Under Test
1. **User Authentication** (Supabase Auth)
2. **Dashboard Statistics** (Real-time stats display)
3. **Credential Scanning** (Email/domain search)
4. **AI Vulnerability Scoring** (RoBERTa 0-100 scale)
5. **Alert Management** (CRUD operations)
6. **Real-time Notifications** (WebSocket updates)
7. **Evidence Management** (Notes, status updates)
8. **Dark Web Scanning** (Tor integration)
9. **Pastebin Search** (Google CSE)
10. **Auto-discovery** (Related email detection)

### 3.2 Features Not Tested
- Third-party APIs (Google CSE, Tor network) - external dependencies
- Supabase infrastructure - managed service
- Docker registry operations - deployment infrastructure

---

## 4. Approach

### 4.1 Testing Strategy

#### 4.1.1 Automated Testing
- **Backend**: pytest with FastAPI TestClient
- **Frontend**: Vitest + React Testing Library
- **Coverage Target**: 70%+ code coverage
- **CI/CD**: Run on every commit

#### 4.1.2 Manual Testing
- **Functional Testing**: User workflows end-to-end
- **UI/UX Testing**: Visual validation with screenshots
- **Security Testing**: Authentication, authorization, RLS
- **Performance Testing**: Response times, concurrent users
- **Compatibility Testing**: Chrome, Firefox, Edge

### 4.2 Test Levels

#### Level 1: Unit Testing
- Individual functions and components
- Mock external dependencies
- Fast execution (<5 minutes)

#### Level 2: Integration Testing
- API endpoint integration
- Database operations
- AI service communication

#### Level 3: System Testing
- Complete user workflows
- End-to-end scenarios
- Real data with test accounts

#### Level 4: Acceptance Testing
- User acceptance criteria
- Performance benchmarks
- Security requirements

---

## 5. Item Pass/Fail Criteria

### 5.1 Pass Criteria
- **Automated Tests**: 95%+ pass rate
- **Code Coverage**: 70%+ coverage
- **Performance**: API responses <500ms (p95)
- **Security**: No critical vulnerabilities
- **Functionality**: All test cases pass
- **UI/UX**: No blocking visual bugs

### 5.2 Fail Criteria
- Critical security vulnerability detected
- Data loss or corruption
- Authentication bypass possible
- System crash or unrecoverable error
- Performance degradation >2x baseline

---

## 6. Suspension and Resumption Criteria

### 6.1 Suspension Criteria
Testing will be suspended if:
- Critical blocker bug prevents further testing
- Test environment unavailable
- Major code changes require test updates

### 6.2 Resumption Criteria
Testing resumes when:
- Blocker bugs fixed and verified
- Test environment restored
- Test cases updated for code changes

---

## 7. Test Deliverables

### 7.1 Before Testing
- [x] Test Plan (this document)
- [x] Test Cases Document
- [x] Test Data Preparation
- [x] Test Environment Setup

### 7.2 During Testing
- [ ] Test Execution Logs
- [ ] Defect Reports
- [ ] Progress Reports

### 7.3 After Testing
- [ ] Test Summary Report
- [ ] Code Coverage Report
- [ ] Performance Test Results
- [ ] Screenshots and Videos

---

## 8. Testing Tasks

| Task | Assigned To | Duration | Status |
|------|-------------|----------|--------|
| Setup pytest environment | Developer | 2 hours | ✅ Complete |
| Write backend unit tests | Developer | 4 hours | ✅ Complete |
| Write frontend unit tests | Developer | 4 hours | ✅ Complete |
| Execute manual test cases | Tester | 8 hours | 🔄 In Progress |
| Performance testing | Developer | 2 hours | ⏳ Pending |
| Security audit | Developer | 2 hours | ⏳ Pending |
| Document results | Tester | 2 hours | ⏳ Pending |

---

## 9. Environmental Needs

### 9.1 Hardware
- Development machine: 16GB RAM, i5/Ryzen 5+
- Network: Stable internet (API calls)

### 9.2 Software
- **OS**: Windows 11 / macOS / Linux
- **Runtime**: Node.js 20+, Python 3.11+
- **Database**: Supabase PostgreSQL
- **Docker**: Docker Desktop 4.x
- **Browsers**: Chrome, Firefox, Edge (latest)

### 9.3 Test Data
- Test user accounts: test1@ui.ac.id, test2@ui.ac.id
- Sample alerts: 93 pre-loaded alerts
- Mock credentials: Non-real sensitive data

### 9.4 External Services
- Supabase (https://oyziawmetogvilefpepl.supabase.co)
- Google Gemini API (AI scoring)
- Local Docker containers (3 services)

---

## 10. Responsibilities

| Role | Responsibility | Person |
|------|----------------|--------|
| Test Manager | Overall test coordination | Calvin Wkatoroy |
| Test Engineer | Execute test cases | Calvin Wkatoroy |
| Developer | Fix bugs, write automated tests | Calvin Wkatoroy |
| Reviewer | Review test results | Thesis Advisor |

---

## 11. Staffing and Training Needs

### 11.1 Staffing
- 1 Full-stack developer (also tester)
- Access to thesis advisor for reviews

### 11.2 Training
- pytest framework basics
- Vitest + React Testing Library
- IEEE 829 documentation standards

---

## 12. Schedule

| Phase | Start Date | End Date | Status |
|-------|------------|----------|--------|
| Test Planning | Dec 10, 2024 | Dec 14, 2024 | ✅ Complete |
| Test Case Design | Dec 14, 2024 | Dec 15, 2024 | 🔄 In Progress |
| Test Environment Setup | Dec 14, 2024 | Dec 14, 2024 | ✅ Complete |
| Test Execution | Dec 15, 2024 | Dec 18, 2024 | ⏳ Pending |
| Defect Fixing | Dec 18, 2024 | Dec 20, 2024 | ⏳ Pending |
| Test Reporting | Dec 20, 2024 | Dec 21, 2024 | ⏳ Pending |

---

## 13. Risks and Contingencies

### 13.1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API rate limiting (Google CSE) | High | Medium | Use test mode, cache results |
| External service downtime | Medium | High | Mock external APIs in tests |
| Docker build failures | Low | Medium | Pin dependency versions |
| Test data corruption | Low | High | Backup test database |

### 13.2 Contingencies
- **Backup test environment**: Local SQLite database
- **Offline testing**: Mock all external API calls
- **Alternative tools**: Postman for manual API testing

---

## 14. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Plan Author | Calvin Wkatoroy | ____________ | Dec 14, 2024 |
| Thesis Advisor | [Advisor Name] | ____________ | __________ |
| Department Head | [Head Name] | ____________ | __________ |

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | Dec 14, 2024 | Calvin Wkatoroy | Initial test plan |

