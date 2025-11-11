# Testing Framework

This directory contains the automated tests for the MyShop e-commerce platform.

## Test Structure

- `test_commission.py` - Tests for the commission calculation system
- `test_payment.py` - Tests for the payment processing system
- `test_models.py` - Tests for data models
- `test_views.py` - Tests for view functions

## Running Tests

### Prerequisites

Make sure you have the testing dependencies installed:

```bash
pip install -r requirements.txt
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=store

# Run with HTML coverage report
pytest --cov=store --cov-report=html
```

### Running Specific Tests

```bash
# Run tests for a specific file
pytest store/tests/test_commission.py

# Run tests for a specific class
pytest store/tests/test_commission.py::TestCommissionSystem

# Run a specific test method
pytest store/tests/test_commission.py::TestCommissionSystem::test_get_commission_rate
```

## Test Types

### Unit Tests
Test individual functions and methods in isolation.

### Integration Tests
Test the interaction between different components of the system.

### Functional Tests
Test complete user workflows and business processes.

## Writing Tests

### Test Structure

Tests are written using pytest with Django integration via pytest-django.

```python
import pytest
from django.contrib.auth.models import User
from decimal import Decimal

@pytest.mark.django_db
class TestExample:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup test data
        pass

    def test_example_functionality(self):
        # Test implementation
        assert True
```

### Fixtures

- Use `@pytest.mark.django_db` for tests that require database access
- Use `@pytest.fixture(autouse=True)` for setup that should run before each test
- Use `pytest.fixture` for reusable test data

### Best Practices

1. Each test should be independent and not rely on the state from other tests
2. Use descriptive test names that clearly indicate what is being tested
3. Test both positive and negative cases
4. Use factories (factory-boy) for complex test data creation
5. Mock external services and dependencies
6. Test edge cases and error conditions

## Coverage

The test suite includes coverage analysis to ensure adequate test coverage.

To generate a coverage report:

```bash
pytest --cov=store --cov-report=html
```

This will create an HTML coverage report in the `htmlcov/` directory.

## Continuous Integration

Tests are automatically run on every commit to the repository as part of the CI pipeline.