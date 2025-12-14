# Nexzy Testing Guide

## Quick Start

### Run All Automated Tests
```powershell
.\run-tests.ps1
```

### Run Backend Tests Only
```powershell
cd nexzy-backend
.\venv\Scripts\pytest tests\ -v
```

### Run Frontend Tests Only
```powershell
cd nexzy-frontend
npm test
```

---

## Test Structure

### Automated Tests (30+ tests)
- **Backend**: 20+ pytest tests in `nexzy-backend/tests/`
- **Frontend**: 10+ vitest tests in `nexzy-frontend/src/test/`

### Manual Tests (75 test cases)
- **IEEE 829 Format**: See `docs/testing/IEEE_829_TEST_CASES.md`
- **Execution**: Manual with screenshots

---

## Running Tests

### 1. Backend Tests (pytest)

**Install dependencies:**
```powershell
cd nexzy-backend
.\venv\Scripts\pip install pytest pytest-asyncio httpx
```

**Run all tests:**
```powershell
pytest tests/ -v
```

**Run specific test file:**
```powershell
pytest tests/test_api_endpoints.py -v
```

**Run with coverage:**
```powershell
pytest tests/ --cov=api --cov=lib --cov-report=html
```

**Coverage report:** `nexzy-backend/htmlcov/index.html`

---

### 2. Frontend Tests (vitest)

**Install dependencies:**
```powershell
cd nexzy-frontend
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
```

**Add to package.json scripts:**
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

**Run all tests:**
```powershell
npm test
```

**Run with watch mode:**
```powershell
npm run test:watch
```

**Run with coverage:**
```powershell
npm run test:coverage
```

**Coverage report:** `nexzy-frontend/coverage/index.html`

---

## Manual Testing

### Executing IEEE 829 Test Cases

1. **Open test cases:** `docs/testing/IEEE_829_TEST_CASES.md`
2. **Execute each test case** following the steps
3. **Take screenshots** of results
4. **Update status** (Pass/Fail) in the document
5. **Document bugs** in separate defect report

### Screenshot Guidelines
- Capture full screen or relevant UI area
- Name format: `TC-XXX-description.png`
- Store in: `docs/testing/screenshots/`

### Example Manual Test Execution

**TC-001: User Registration**
1. Navigate to http://localhost/login ✅
2. Click "Sign Up" ✅
3. Enter test@ui.ac.id ✅
4. Enter Test1234! ✅
5. Click Create Account ✅
6. **Result:** Account created, redirected to dashboard ✅
7. **Status:** PASS ✅
8. **Screenshot:** `TC-001-registration-success.png`

---

## Test Reports

### Automated Test Report
```powershell
# Generate combined report
.\run-tests.ps1 > test-results.txt
```

### Manual Test Report
- Update `IEEE_829_TEST_CASES.md` with results
- Calculate pass rate: (passed / total) * 100
- Document in `IEEE_829_TEST_SUMMARY.md`

---

## CI/CD Integration (Optional)

### GitHub Actions (Example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Backend Tests
        run: |
          cd nexzy-backend
          pip install -r requirements.txt
          pytest tests/ -v
      - name: Frontend Tests
        run: |
          cd nexzy-frontend
          npm install
          npm test
```

---

## Test Coverage Goals

- **Backend**: 70%+ code coverage
- **Frontend**: 60%+ component coverage
- **Manual**: 95%+ test case pass rate

---

## Troubleshooting

### Backend tests fail with "ModuleNotFoundError"
```powershell
cd nexzy-backend
.\venv\Scripts\pip install -e .
```

### Frontend tests fail with "Cannot find module"
```powershell
cd nexzy-frontend
npm install
```

### Tests fail with "Database connection error"
- Ensure Supabase credentials in `.env`
- Check internet connection

### AI service tests skipped
- Start Docker containers: `docker-compose up -d`
- Or run services locally with `.\start-all.ps1`

---

## Next Steps

1. ✅ Run automated tests: `.\run-tests.ps1`
2. ⏳ Execute manual test cases (75 total)
3. ⏳ Take screenshots for each test
4. ⏳ Document results
5. ⏳ Write test summary report

**Estimated Time:**
- Automated tests: 5 minutes
- Manual testing: 4-6 hours
- Documentation: 2 hours
- **Total: ~6-8 hours**

---

## For Thesis Defense

**Show evaluators:**
1. **Test plan** (IEEE 829 format)
2. **Automated test results** (pytest + vitest output)
3. **Code coverage reports** (HTML reports)
4. **Manual test cases** (75 cases documented)
5. **Screenshots** (proof of execution)
6. **Test summary** (statistics, pass rate)

This demonstrates:
- ✅ Software engineering best practices
- ✅ Quality assurance rigor
- ✅ Professional development standards
- ✅ IEEE 829 compliance
