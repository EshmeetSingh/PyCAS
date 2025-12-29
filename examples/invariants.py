"""
Structural invariant tests for PyCAS ASTs.

These invariants verify that normalized expressions satisfy all
AST structural and semantic rules. They are used to detect structural
regressions during development.
"""

from pycas.core import integrate, differentiate
from pycas.normalizer import normalize
from pycas.pretty_printer import to_string

def walk(expr, fn):
    """
    Walk the AST and apply fn to every node.
    """
    fn(expr)

    t = expr["type"]

    if t == "const" or t == "var":
        pass
    
    elif t == "sum":
        for term in expr["terms"]:
            walk(term, fn)

    elif t == "mul":
        walk(expr["expr"], fn)

    elif t == "power":
        walk(expr["base"], fn)
    
    elif t == "prod":
        for factor in expr["factors"]:
            walk(factor, fn) 

    elif t == "func":
        walk(expr["arg"], fn)

    else:
        raise AssertionError(f"Unknown node type during invariant walk: {t}")

def assert_mul_expr_not_const(expr):
    """
    Mul nodes must not wrap a const expression.
    """
    def check(node):
        if node["type"] == "mul":
            assert node["expr"]["type"] != "const", "Mul wrapping const found"

    walk(expr, check)

def assert_no_nested_mul(expr):
    """
    Ensure that no Mul node directly contains another Mul node.
    """
    def check(node):
        if node["type"] == "mul":
            assert node["expr"]["type"] != "mul", "Nested mul found"
    
    walk(expr, check)

def assert_normalized_power(expr):
    """
    After normalization, power nodes must have exponent >= 2.
    """
    def check(node):
        if node["type"] == "power":
            assert node["exp"] >= 2, f"Invalid Power Exponent: {node['exp']}"

    walk(expr, check)

def assert_valid_sum(expr):
    """
    Sums must contain at least two terms after normalization.
    """
    def check(node):
        if node["type"] == "sum":
            assert len(node["terms"]) >= 2, "Sum with fewer than 2 terms"
    
    walk(expr, check)

def assert_prod_atomic(expr):
    """
    All prod factors must be atomic.
    """
    ATOMIC = {"var", "power", "func"}
    def check(node):
        if node["type"] == "prod":
            for factor in node["factors"]:
                assert factor["type"] in ATOMIC, f"Non-atomic factor in prod: {factor}"

    walk(expr, check)

def assert_no_nested_prod(expr):
    """
    Prod nodes must not contain nested prod nodes.
    """
    def check(node):
        if node["type"] == "prod":
            for factor in node["factors"]:
                assert factor["type"] != "prod", "Nested prod found"

    walk(expr, check)

def assert_valid_prod(expr):
    """
    Prod nodes must contain at least two atomic factors.
    """
    def check(node):
        if node["type"] == "prod":
            assert len(node["factors"]) >= 2 , "Prod with fewer than 2 factors"

    walk(expr, check)


def assert_prod_power_base(expr):
    """
    Ensure that any power node factor of prod node has a variable as a base.
    """
    def check(node):
        if node["type"] == "prod":
            for factor in node["factors"]:
                if factor["type"] == "power":
                    assert factor["base"]["type"] == "var", f"Non-var base in power inside prod: {factor}"

    walk(expr, check)

def assert_valid_func_name(expr):
    """
    Ensure that the function name is one of the supported names (sin, cos, exp).
    """
    ALLOWED_FUNCS = {"sin", "cos", "exp"}
    def check(node):
        if node["type"] == "func":
            assert node["name"] in ALLOWED_FUNCS, f"Invalid function name: {node['name']}"

    walk(expr, check)

def assert_func_arg_is_var(expr):
    """
    Ensure that all function nodes take a variable as argument.
    """
    def check(node):
        if node["type"] == "func":
            assert node["arg"]["type"] == "var", "Function argument must be a variable"

    walk(expr, check)

def assert_printable(expr):
    """
    Ensure that the expression can be converted to a string
    without crashing the pretty-printer.
    """
    try:
        to_string(expr)

    except Exception as e:
        assert False, f"Pretty-printer crashed: {e}"

def assert_all_invariants(expr):
    """
    Run all structural invariants on a normalized AST.
    """
    assert_no_nested_mul(expr)
    assert_mul_expr_not_const(expr)
    assert_normalized_power(expr)
    assert_valid_sum(expr)

    assert_valid_prod(expr)
    assert_no_nested_prod(expr)
    assert_prod_atomic(expr)
    assert_prod_power_base(expr)

    assert_valid_func_name(expr)
    assert_func_arg_is_var(expr)

def assert_valid_and_renderable(expr):
    assert_all_invariants(expr)
    assert_printable(expr)

# ----------------------------Testing-------------------------------------------------
x = {"type": "var", "variable": "x"}

expr = {
    "type": "sum",
    "terms": [
        {"type": "mul", "const": 7, "expr": {"type": "power", "base": x, "exp": 3}},
        {"type": "mul", "const": 4, "expr": {"type": "power", "base": x, "exp": 2}},
        {"type": "mul", "const": 3, "expr": x},
        {"type": "const", "value": 10},
        {"type": "func", "name": "cos", "arg": {"type": "var", "variable": "x"}}
    ]
}

if __name__ == "__main__":
    normalized = normalize(expr)
    assert_valid_and_renderable(normalized)

    d = differentiate(normalized)["result"]
    assert_valid_and_renderable(d)

    i = integrate(normalized)["result"]
    assert_valid_and_renderable(i)