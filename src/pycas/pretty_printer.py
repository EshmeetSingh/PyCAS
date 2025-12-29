"""
Pretty Printer for PyCAS.

This module converts normalized AST expressions into readable
mathematical strings. It assumes all AST invariants are already
enforced.
"""

from fractions import Fraction

def to_string(expr, mode="fraction", var_name = "x"):
    """
    Converts a normalized AST expression into a human-readable string.

    Parameters:
        expr (dict): Normalized AST node
        mode (str): "fraction" or "decimal" display mode
        var_name (str): Original variable name given by user as input
    Returns:
        str: Mathematical string representation
    """
    exp_type = expr["type"]

    if exp_type == "const":
        value = expr["value"]

        if isinstance(value, Fraction):
            if value.denominator == 1:
                return str(value.numerator)
            return (
                f"{value.numerator}/{value.denominator}"
                if mode == "fraction"
                else str(float(value))
            )

        return str(value)

    elif exp_type == "var":
        return var_name

    elif exp_type == "power":
        base_str = to_string(expr["base"], mode, var_name)
        exp = expr["exp"]

        # Parenthesize function bases: (sin(x))^2
        if expr["base"]["type"] == "func":
            base_str = f"({base_str})"

        return f"{base_str}^{exp}"

    elif exp_type == "mul":
        constant = expr["const"]
        expression = expr["expr"]

        inner_str = to_string(expression, mode, var_name)

        if expression["type"] in {"sum", "prod"}:
            inner_str = f"({inner_str})"

        if constant == -1:
            return f"-{inner_str}"

        constant_str = to_string({"type": "const", "value": constant}, mode)
        return f"{constant_str}{inner_str}"

    elif exp_type == "prod":
        parts = []

        for factor in expr["factors"]:
            s = to_string(factor, mode, var_name)
            parts.append(s)

        return "".join(parts)

    elif exp_type == "sum":
        terms = expr["terms"]
        result = to_string(terms[0], mode, var_name)

        for term in terms[1:]:
            s = to_string(term, mode, var_name)
            if s.startswith("-"):
                result += " - " + s[1:]
            else:
                result += " + " + s

        return result

    elif exp_type == "func":
        name = expr["name"]
        arg = var_name
        return f"{name}({arg})"
