# How to Run Tests

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage Report

```bash
pytest --cov=store
```

### Run Tests with HTML Coverage Report

```bash
pytest --cov=store --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

## Test Output

When you run the tests, you should see output similar to:

```
============================= test session starts =============================
platform linux -- Python 3.x.x, pytest-7.x.x, pluggy-1.x.x
django: settings = shopsite.settings (from ini)
rootdir: /path/to/myshop, configfile: pytest.ini
plugins: django-4.x.x, cov-4.x.x
collected X items

store/tests/test_commission.py ..                                       [ 50%]
store/tests/test_example.py ...                                         [100%]

============================== 5 passed in 2.45s ==============================
```

## Troubleshooting

### ImportError: No module named pytest

Make sure you've installed the dependencies:

```bash
pip install -r requirements.txt
```

### Django not configured

Make sure the `DJANGO_SETTINGS_MODULE` environment variable is set or pytest.ini is configured correctly.

### Database access not allowed

Make sure to use the `@pytest.mark.django_db` decorator for tests that require database access.