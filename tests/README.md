# Test Suite Documentation

This directory contains comprehensive tests for the Local RAG application.

## Test Structure

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── unit/
│   ├── test_csv_processor.py   # CSV processing logic tests
│   ├── test_models_config.py   # Model configuration tests
│   └── test_chroma_helpers.py  # ChromaDB helper function tests
├── integration/                # Integration tests (future)
└── fixtures/                   # Sample test data files
    ├── sample_lora_data.csv
    ├── sample_document.md
    └── README.md
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Files

```bash
# CSV processor tests
pytest tests/unit/test_csv_processor.py -v

# Model config tests
pytest tests/unit/test_models_config.py -v

# ChromaDB helper tests
pytest tests/unit/test_chroma_helpers.py -v
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

### Run Only Fast Tests (exclude slow tests)

```bash
pytest tests/ -m "not slow"
```

## Test Coverage Summary

### Phase 1 Implementation (Current)

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| `csv_processor.py` | 30 tests | 100% | ✅ Complete |
| `models_config.py` | 43 tests | 100% | ✅ Complete |
| ChromaDB helpers (app.py) | 27 tests | 29% (app.py) | ✅ Helpers tested |

**Overall Results:**
- **Total Tests:** 100
- **Passing:** 98
- **Failing:** 2 (edge cases discovered)
- **Overall Code Coverage:** 26.25%

### Test Details

#### CSV Processor Tests (30 tests)

Tests cover:
- ✅ Time-based chunking with various intervals (2h, 4h, 6h)
- ✅ Date extraction from filenames
- ✅ Fallback to current date when filename has no date
- ✅ Explicit date parameter handling
- ✅ Content structure validation (TEMPERATURE, HUMIDITY, PRESSURE sections)
- ✅ Statistical calculations (min, max, average)
- ✅ Trend calculations (increasing/decreasing)
- ✅ Metadata structure and values
- ✅ System status information (battery, charging, RSSI, SNR)
- ✅ Data quality metrics
- ✅ Multiple file processing from directories
- ✅ File pattern matching
- ✅ Data summary generation
- ✅ Edge cases (missing columns, invalid timestamps, nonexistent files)
- ⚠️ Empty CSV handling (bug discovered - needs fix in csv_processor.py)

#### Models Config Tests (43 tests)

Tests cover:
- ✅ Configuration structure validation
- ✅ Model list retrieval
- ✅ Display name mapping
- ✅ Model configuration lookup
- ✅ Default model selection
- ✅ Provider validation (ollama, anthropic)
- ✅ Embedding model configuration
- ✅ Model name uniqueness
- ✅ Integration between all config functions
- ✅ Edge cases (empty models list, invalid model names)

#### ChromaDB Helper Tests (27 tests)

Tests cover:
- ✅ Client creation and initialization
- ✅ Directory management and permissions
- ✅ Collection listing and extraction
- ✅ PDF and Markdown filename extraction
- ✅ Underscore to space conversion in filenames
- ✅ Database clearing functionality
- ✅ Collection name generation and reverse mapping
- ✅ Complete workflow (create → list → clear)
- ✅ Persistence across client instances
- ✅ Error handling (permissions, corrupted databases)
- ⚠️ Client settings test (internal API check - minor issue)

## Known Issues

### Issue 1: Empty CSV Handling
**File:** `csv_processor.py:52`
**Issue:** Function doesn't handle empty CSVs (no data rows)
**Error:** `AttributeError: Can only use .dt accessor with datetimelike values`
**Fix Needed:** Add check for empty DataFrame before processing

```python
# Suggested fix in csv_processor.py
if df.empty:
    return []  # Return empty list for empty CSV
```

### Issue 2: ChromaDB Client Settings Test
**File:** `tests/unit/test_chroma_helpers.py:84`
**Issue:** Test checks for internal `_settings` attribute that may not be exposed
**Impact:** Minor - doesn't affect functionality, just test implementation
**Fix Needed:** Update test to check for public API methods instead

## Test Fixtures

### Available Fixtures (conftest.py)

- `sample_csv_data` - DataFrame with sample LoRa sensor data
- `sample_csv_file` - Temporary CSV file with date in filename
- `sample_csv_file_no_date` - CSV file without date in filename
- `empty_csv_file` - Empty CSV file for edge case testing
- `malformed_csv_file` - CSV with missing required columns
- `multiple_csv_directory` - Directory with multiple CSV files
- `temp_chroma_dir` - Temporary ChromaDB directory
- `mock_env_vars` - Mocked environment variables
- `sample_markdown_content` - Sample markdown text
- `sample_markdown_file` - Temporary markdown file

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.requires_ollama
def test_with_ollama():
    pass
```

Run specific markers:
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Exclude slow tests
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Next Steps (Phase 2 & 3)

### Phase 2: Integration Tests
- [ ] Document processing workflows (PDF/Markdown)
- [ ] Vector store creation and retrieval
- [ ] RAG chain functionality
- [ ] End-to-end query processing

### Phase 3: Application Tests
- [ ] Streamlit UI component tests
- [ ] Full user workflow tests
- [ ] Performance tests
- [ ] Error recovery tests

## Best Practices

1. **Run tests before committing:**
   ```bash
   pytest tests/
   ```

2. **Check coverage:**
   ```bash
   pytest tests/ --cov=. --cov-report=term-missing
   ```

3. **Fix failing tests immediately** - Don't let them accumulate

4. **Write tests for new features** - Maintain high coverage

5. **Use fixtures** - Don't repeat test setup code

6. **Test edge cases** - Empty inputs, large inputs, invalid inputs

7. **Mock external dependencies** - Ollama, Anthropic API, file system

## Contributing

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Add fixtures to `conftest.py` if they're reusable
4. Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
5. Add docstrings explaining what the test validates
6. Group related tests in classes
7. Update this README with new test information

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
