"""A tiny calculator module, used as a scratch target for the factory to build on."""

import math


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def subtract(a, b):
    """Return the difference of a and b."""
    return a - b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def divide(a, b):
    """Return the quotient of a and b."""
    return a / b


def integrate(f, a, b, n=1000):
    """Return the integral of f from a to b by the trapezoidal rule with n steps."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return h * total


def sin(x):
    """Return the sine of x, where x is an angle in radians."""
    return math.sin(x)
