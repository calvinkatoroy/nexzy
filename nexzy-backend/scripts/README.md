# Backend Scripts

Utility scripts for testing, debugging, and database operations.

## Database Inspection
- `check_alerts_schema.py` - Verify alerts table structure
- `check_database.py` - General database health check
- `check_scan_results.py` - Inspect scan results

## Testing
- `test_credential_detection.py` - Test PII pattern detection
- `test_direct_insert.py` - Test direct database inserts
- `test_manual_insert.py` - Manual data insertion tests
- `test_pii_detection.py` - PII detection algorithm tests
- `test_scan.py` - Scan functionality tests

## Data Population
- `insert_sample_alerts.py` - Generate sample alerts for testing

## Usage

```bash
# Run from nexzy-backend directory
python scripts/check_database.py
python scripts/test_scan.py
```
