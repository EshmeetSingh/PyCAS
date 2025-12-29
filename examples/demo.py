"""
PyCAS Demo

Demonstrates parsing, normalization differentiation, and integration
of symbolic expressions using the public API.
"""

from pycas.core import integrate_string, differentiate_string
from pycas.parser import parse_string
from pycas.pretty_printer import to_string


def show_expression(s, mode="decimal"):
    """
    Parse and display the normalized form of an expression.
    """
    parsed = parse_string(s)
    expr = parsed["ast"]
    var_name = parsed["var"]
    print("Original expression:")
    print("  ", to_string(expr, mode, var_name))
    print()


def show_derivative(s, mode="decimal"):
    """
    Compute and display the derivative of an expression.
    """
    d = differentiate_string(s, mode)

    print("Derivative:")
    if "error" in d:
        print("  Error:", d["reason"])
    else:
        print("  ", d["string"])
    print()

def print_steps(steps, indent=0):
    for step in steps:
        if isinstance(step, list):
            print_steps(step, indent + 1)
        else:
            print("  " * indent + "- " + step)

def show_integral(s, mode="decimal", show_steps=True):
    """
    Compute and display the integral of an expression.
    """
    i = integrate_string(s, mode)

    print("Integral:")
    if "error" in i:
        print("  Error:", i["reason"])
        return

    print("  ", i["string"])
    print()

    if show_steps:
        print("Integration steps:")
        print_steps(i["steps"])
        print()


if __name__ == "__main__":
    # Example inputs
    s = "7x^3 + 13x^2 - 12x + 10"
    # s = "2cos(x)^3"
    # s = "exp^2(x)"

    show_expression(s)
    show_derivative(s)
    show_integral(s)
