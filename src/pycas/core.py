"""
Core symbolic differentiation and integration dispatch.

This module connects:
- parsing
- rule application
- normalization
- pretty printing

It enforces a uniform public API for PyCAS.
"""

from pycas.rules import *
from pycas.errors import unsupported
from pycas.normalizer import normalize
from pycas.pretty_printer import to_string
from pycas.parser import parse_string
# from examples.invariants import assert_all_invariants
# assert_all_invariants(expr)

def integrate_string(s, mode="fraction"):
    """
    Parses and symbolically integrates an input string.

    Parameters:
        s (str): Input mathematical expression
        mode (str): "fraction" or "decimal" output mode

    Returns:
        dict: Integration result or error
    """
    try:
        parsed = parse_string(s)
        expr = parsed["ast"]
        var_name = parsed["var"]
    except Exception as e:
        return unsupported(str(e))

    return integrate(expr, mode, var_name)


def integrate(expr, mode="fraction", var_name = "x"):
    """
    Symbolically integrates a normalized AST expression.

    Assumes:
    - expr is already normalized
    - All AST invariants hold

    Returns:
        dict with keys: result, steps, string, constant?
    """
    expr_type = expr.get("type")

    if expr_type == "const":
        out = integrate_const(expr)
    elif expr_type == "var":
        out = integrate_var(expr)
    elif expr_type == "power":
        out = integrate_power(expr)
    elif expr_type == "mul":
        out = integrate_mul(expr, mode, var_name)
    elif expr_type == "prod":
        return unsupported("Integration of products not implemented yet")
    elif expr_type == "sum":
        out = integrate_sum(expr, mode, var_name)
    elif expr_type == "func":
        out = integrate_func(expr)
    else:
        return unsupported(f"Unsupported Expression Type: {expr_type}")

    if "error" in out:
        return out

    out["result"] = normalize(out["result"])
    out["string"] = to_string(out["result"], mode, var_name)
    # assert_all_invariants(out["result"])

    if out.get("constant"):
        out["string"] += " + C"

    return out


def differentiate_string(s, mode="fraction"):
    """
    Parses and symbolically differentiates an input string.
    """
    try:
        parsed = parse_string(s)
        expr = parsed["ast"]
        var_name = parsed["var"]
    except Exception as e:
        return unsupported(str(e))

    return differentiate(expr, mode, var_name)


def differentiate(expr, mode="fraction", var_name = "x"):
    """
    Symbolically differentiates a normalized AST expression.

    Product rule is intentionally unsupported in v1.
    """
    expr_type = expr.get("type")

    if expr_type == "const":
        out = differentiate_const(expr)
    elif expr_type == "var":
        out = differentiate_var(expr)
    elif expr_type == "power":
        out = differentiate_power(expr)
    elif expr_type == "mul":
        out = differentiate_mul(expr, mode, var_name)
    elif expr_type == "prod":
        return unsupported("Product rule not implemented yet")
    elif expr_type == "sum":
        out = differentiate_sum(expr, mode, var_name)
    elif expr_type == "func":
        out = differentiate_func(expr)
    else:
        return unsupported(f"Unsupported Expression Type: {expr_type}")

    if "error" in out:
        return out

    out["result"] = normalize(out["result"])
    out["string"] = to_string(out["result"], mode, var_name)
    # assert_all_invariants(out["result"])

    return out