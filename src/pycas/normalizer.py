from pycas.normalizer_rules import *

def normalize(expr):
    """
    Normalize an AST expression into canonical form.

    Normalization:
    - is bottom up (children first)
    - may change node types
    - enforces all AST invariants via normalization rules
    """
    expr_type = expr["type"]

    if expr_type == "const":
        return expr
    elif expr_type == "var":
        return expr
    elif expr_type == "power":
        return normalize_power(expr)
    elif expr_type == "mul":
        return normalize_mul(expr)
    elif expr_type == "prod":
        return normalize_prod(expr)
    elif expr_type == "sum":
        return normalize_sum(expr)
    elif expr_type == "func":
        return normalize_func(expr)
    else:
        raise ValueError(f"Unknown expression type in normalization: {expr_type}")