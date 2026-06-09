from math import sqrt


def fn_add_numbers(a: int | float, b: int | float) -> int | float:
    """Add two numbers together and return their sum."""
    return (a + b)


def fn_greet(name: str) -> str:
    """Generate a greeting message for a person by name."""
    return f"Hello {name}"


def fn_reverse_string(s: str) -> str:
    """Reverse a string and return the reversed result."""
    return s[::-1]


def fn_get_square_root(a: int | float) -> int | float:
    """description": "Calculate the square root of a number."""
    return sqrt(a)


def fn_substitute_string_with_regex(
        source_string: str, regex: str, replacement: str) -> str:
    """Replace all occurrences matching a regex pattern in a string."""
    return source_string.replace(regex, replacement)
