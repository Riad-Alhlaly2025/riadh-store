import pytest

def test_example():
    """A simple test to verify the testing framework is working."""
    assert 1 + 1 == 2

def test_string_operations():
    """Test string operations."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    """Test square function with parametrized inputs."""
    assert input * input == expected