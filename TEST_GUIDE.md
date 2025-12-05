# Quick Test Guide

## Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

## Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_csv_processor.py

# Run specific test
pytest tests/unit/test_csv_processor.py::TestCreateTimeBasedChunks::test_basic_chunking_with_date_in_filename
```

## Coverage

```bash
# Run tests with coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open: htmlcov/index.html

# Show only uncovered lines
pytest --cov=. --cov-report=term-missing | grep -A 100 "Missing"
```

## Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip tests requiring external services
pytest -m "not requires_ollama and not requires_api_key"
```

## Debugging

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Enter debugger on failure
pytest --pdb

# Detailed traceback
pytest --tb=long
```

## Performance

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Show slowest 10 tests
pytest --durations=10
```

## Current Test Results (Phase 1)

✅ **100 tests implemented**
✅ **98 tests passing** (98% pass rate)
⚠️ **2 edge cases discovered** (bugs to fix)

### Coverage by Module
- `csv_processor.py`: 100% (50/50 statements)
- `models_config.py`: 100% (13/13 statements)
- `app.py`: 29% (121/417 statements) - ChromaDB helpers tested
- Overall: 26.25% (184/701 statements)

### Issues Found
1. Empty CSV handling in `csv_processor.py:52` - needs error handling
2. ChromaDB client settings test - minor test implementation issue

## Writing New Tests

```python
# tests/unit/test_example.py
import pytest
from my_module import my_function

class TestMyFunction:
    """Tests for my_function"""

    def test_basic_case(self):
        """Test basic functionality"""
        result = my_function("input")
        assert result == "expected"

    def test_edge_case(self, tmp_path):
        """Test edge case with fixture"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        result = my_function(str(test_file))
        assert result is not None
```

## CI Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Troubleshooting

### ModuleNotFoundError
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Tests Not Found
```bash
# Check pytest can discover tests
pytest --collect-only
```

### Import Errors
```bash
# Run from project root
cd /home/user/local-rag
pytest
```

### ChromaDB Errors
```bash
# Clear ChromaDB test directories
rm -rf test_chroma_db* /tmp/pytest-*
```

## Next Steps

1. Fix the 2 failing tests
2. Increase app.py coverage (currently 29%)
3. Add integration tests (Phase 2)
4. Add Streamlit UI tests (Phase 3)
5. Set up CI/CD pipeline
