"""
Symbolic differentiation and integration rules.

This module implements rule-based calculus over a restricted,
well-defined algebraic domain.

Supported:
- constants
- variable x
- monomials x^n
- constant multiples
- sums
- basic functions: sin, cos, exp

Intentionally NOT supported (v1):
- product rule
- chain rule
- substitution-based integration
"""

from pycas.errors import unsupported
from fractions import Fraction

VAR = {"type": "var", "variable": "x"}

def integrate_const(expr):
    """
    ∫ c dx = c.x + C
    """
    c = expr["value"]

    result = {
        "type": "mul",
        "const": c,
        "expr": VAR
    }

    steps = [f"∫ {c} dx = {c}x + C"]

    return {
        "result": result,
        "steps": steps,
        "constant": True
    }

def integrate_var(expr):
    """
    ∫ x dx = x² / 2 + C
    """
    result = {
        "type": "mul",
        "const": Fraction(1, 2),
        "expr": {"type": "power", "base": expr, "exp": 2}
    }

    steps = ["∫ x dx = x^2/2 + C"]

    return {
        "result": result,
        "steps": steps,
        "constant": True
    }

def integrate_power(expr):
    """
    ∫ xⁿ dx = xⁿ⁺¹ / (n+1), n ≠ -1
    """
    base = expr["base"]
    if base["type"] != "var":
        return unsupported("Power rule only supports x^n (no chain rule yet)")


    n = expr["exp"]
    if n == -1:
        return unsupported("Integral of x^-1 needs Logarithms(not implemented yet)")
    
    result = {
        "type": "mul",
        "const": Fraction(1, (n + 1)),
        "expr": {
            "type": "power",
            "base": base,
            "exp": n + 1
        }
    }

    steps = [f"∫ x^{n} dx = x^{n + 1}/{n + 1} + C"]

    return {
        "result": result,
        "steps": steps,
        "constant": True
    }

def integrate_mul(expr, mode = "fraction", var_name = "x"):
    """
    ∫ c.f(x) dx = c.∫f(x) dx
    """
    from .core import integrate
    c = expr["const"]
    exp = expr["expr"]

    if c == 0:
        result = {"type": "const", "value": 0}
        steps = ["Integral of 0 is 0"]

        return {
            "result": result,
            "steps": steps,
            "constant": True
        }
    
    result = integrate(exp, mode, var_name)

    if "error" in result:
        return result
    
    if result["result"]["type"] == "const":
        final_result = {
            "type": "const",
            "value": c*result["result"]["value"]
        }

        steps = ["Combined Constant Factors"] + result["steps"]
    else:
        final_result = {
            "type": "mul",
            "const": c,
            "expr": result["result"]
        }

        steps = [f"Extracted the constant {c}:"] + result["steps"]

    return {
        "result": final_result,
        "steps": steps,
        "constant": True
    }

def integrate_sum(expr, mode = "fraction", var_name = "x"):
    """
    ∫ (f + g + ...)dx = ∫f dx + ∫g dx + ...

    Steps are returned as a hierarchical list.
    """
    from .core import integrate
    terms = expr["terms"]

    integrated_terms = []
    all_steps = []

    for term in terms:
        result = integrate(term, mode, var_name)

        if "error" in result:
            return result  
        

        integrated_terms.append(result["result"])
        all_steps.append(result["steps"])

    result = {
        "type": "sum",
        "terms": integrated_terms
    }

    steps = ["Using Linearity of Integration:"] + all_steps

    return {
        "result": result,
        "steps": steps,
        "constant": True
    }

def integrate_func(expr):
    """
    Integrals of elementary functions.
    """
    name = expr["name"]
    arg = expr["arg"]
    arg_var = arg["variable"]

    if name == "sin":
        result = {
            "type": "mul",
            "const": -1,
            "expr": {"type": "func", "name": "cos", "arg": arg}
        }
        steps = [f"∫ sin({arg_var}) dx = -cos({arg_var}) + C"]
    elif name == "cos":
        result = {"type": "func", "name": "sin", "arg": arg}
        steps = [f"∫ cos({arg_var}) dx = sin({arg_var}) + C"]
    elif name == "exp":
        result = {"type": "func", "name": "exp", "arg": arg}
        steps = [f"∫ exp({arg_var}) dx = exp({arg_var}) + C"]
    else:
        return unsupported(f"Unsupported function: {name}")

    return {
        "result": result,
        "steps": steps,
        "constant": True
    }


def differentiate_const(expr):
    """
    d/dx(c) = 0
    """
    c = expr["value"]
    result = {"type": "const", "value": 0}
    steps = [f"d/dx({c}) = 0"]

    return {
        "result": result,
        "steps": steps
    }

def differentiate_var(expr):
    """
    d/dx(x) = 1
    """
    return {
        "result": {"type": "const", "value": 1},
        "steps": ["d/dx(x) = 1"]
    }

def differentiate_power(expr):
    """
    d/dx(xⁿ) = n.xⁿ⁻¹
    """
    base = expr["base"]
    if base["type"] != "var":
        return unsupported("Power rule only supports x^n (no chain rule yet)")

    n = expr["exp"]

    if n == 0:
        result = {"type": "const", "value": 0}
        steps = ["d/dx(x^0) = d/dx(1) = 0"]

    else:
        result = {
            "type": "mul",
            "const": n,
            "expr": {
                "type": "power",
                "base": base,
                "exp": (n - 1)
            }
        }

        steps = [f"d/dx(x^{n}) = {n}x^({n-1})"]

    return {
        "result": result,
        "steps": steps
    }

def differentiate_sum(expr, mode = "fraction", var_name = "x"):
    """
    d/dx(f + g + ...) = f' + g' + ...
    """
    from .core import differentiate
    terms = expr["terms"]

    differentiated_terms = []
    all_steps = []

    for term in terms:
        result = differentiate(term, mode, var_name)

        if "error" in result:
            return result
        
        differentiated_terms.append(result["result"])
        all_steps.append(result["steps"])

    result = {
        "type": "sum",
        "terms": differentiated_terms
    }

    steps = ["Using Linearity of Differentiation:"] + all_steps

    return {
        "result": result,
        "steps": steps
    }

def differentiate_mul(expr, mode = "fraction", var_name = "x"):
    """
    d/dx(c.f(x)) = c.f'(x)
    """
    from .core import differentiate
    c = expr["const"]
    exp = expr["expr"]

    result = differentiate(exp, mode, var_name)

    if "error" in result:
        return result
    
    final_result = {
        "type": "mul",
        "const": c,
        "expr": result["result"]
    }

    steps = [f"Extracted the constant {c}:"] + result["steps"]

    return {
        "result": final_result,
        "steps": steps
    }

def differentiate_func(expr):
    """
    Derivatives of elementary functions.
    """
    name = expr["name"]
    arg = expr["arg"]
    arg_var = arg["variable"]

    if name == "sin":
        result = {"type": "func", "name": "cos", "arg": arg}
        steps = [f"d/dx(sin({arg_var})) = cos({arg_var})"]
    elif name == "cos":
        result = {
            "type": "mul",
            "const": -1,
            "expr": {"type": "func", "name": "sin", "arg": arg}
        }
        steps = [f"d/dx(cos({arg_var})) = -sin({arg_var})"]
    elif name == "exp":
        result = {"type": "func", "name": "exp", "arg": arg}
        steps = [f"d/dx(exp({arg_var})) = exp({arg_var})"]
    else:
        return unsupported(f"Unsupported Function: {name}")
    
    return {
        "result": result,
        "steps": steps
    }