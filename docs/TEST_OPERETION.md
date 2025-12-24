```
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_data/test_base_data.py

# Run with coverage
pytest --cov=review_radar

# Run only unit tests
pytest -m unit

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_data/test_base_data.py::TestBaseData::test_client_is_stored
```

```
pytest --cov=review_radar --cov-report=html
# Open htmlcov/index.html in browser
```