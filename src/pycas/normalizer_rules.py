"""
Normalization rules for PyCAS.

This module enforces AST invariants and converts expressions into
a canonical form. Normalization is bottom-up and may change node
types to eliminate redundant structure.

Constants may appear transiently during normalization, but not in
the result.

All symbolic rules return normalized output.
"""

from pycas.errors import unsupported

def prod_order_key(factor):
    order = {
        "var": 0,
        "power": 1,
        "func": 2
    }
    return order.get(factor["type"], 99)

def normalize_power(expr):
    """
    Normalizes power expressions.

    Applies:
    - x^0 → 1
    - x^1 → x

    Assumes exponent is a non-negative integer.
    """

    from .normalizer import normalize
    exp = expr["exp"]
    base = normalize(expr["base"])

    if exp == 0:
        return {"type": "const", "value": 1}
    if exp == 1:
        return base
   
    return {"type": "power", "base": base, "exp": exp}

def normalize_mul(expr):
    """
    Normalizes constant multiplication.

    - Absorbs constants
    - Flattens nested multiplications
    - Eliminates identity elements
    """

    from .normalizer import normalize

    constant = expr["const"]
    if constant == 0:
        return {"type": "const", "value": 0}
    
    inner_expr = normalize(expr["expr"])

    if inner_expr["type"] == "const":
        new_value = inner_expr["value"] * constant
        return {"type": "const", "value": new_value}
    
    if inner_expr["type"] == "mul":
        coeff = constant * inner_expr["const"]
        return {
            "type": "mul",
            "const": coeff,
            "expr": inner_expr["expr"]
        }
    
    
    if constant == 1:
        return inner_expr
    
    return {"type": "mul", "const": constant, "expr": inner_expr}

def normalize_prod(expr):
    """
    Normalizes product expressions.

    Responsibilities:
    - Flatten nested products
    - Absorb constant factors
    - Combine powers of the variable
    - Enforce canonical ordering of factors

    This function does NOT distribute products over sums.
    """
    
    from .normalizer import normalize

    # Step 1: normalize and flatten nested products
    factors = []
    for factor in expr["factors"]:
        f = normalize(factor)
        if f["type"] == "prod":
            factors.extend(f["factors"])
        else:
            factors.append(f)

    # Step 2: absorb constants and collect atomic factors
    product_of_const = 1
    atomic_factors = []

    for factor in factors:
        if factor["type"] == "const":
            if factor["value"] == 0:
                return {"type": "const", "value": 0}
            product_of_const *= factor["value"]
        elif factor["type"] in {"var", "power", "func"}:
            atomic_factors.append(factor)
        else:
            return unsupported(f"Unsupported Factor Type in Product: {factor['type']}")

    # Step 2.5: capture cannonical variable to avoid hardcoding it to x
    canonical_var = None
    for factor in atomic_factors:
        if factor["type"] == "var":
            canonical_var = factor
            break
        if factor["type"] == "power" and factor["base"]["type"] == "var":
            canonical_var = factor["base"]
            break

    # Step 3: combine powers of x
    power_sum = 0
    other_factors = []

    for factor in atomic_factors:
        if factor["type"] == "var":
            power_sum += 1
        elif factor["type"] == "power" and factor["base"]["type"] == "var":
            # The second condition assumes that parser restricts powers and invariants forbid other bases
            power_sum += factor["exp"]
        else:
            other_factors.append(factor)

    if power_sum == 1:
        other_factors.append(canonical_var)
    elif power_sum >= 2:  
        other_factors.append({
            "type": "power",
            "base": canonical_var,
            "exp": power_sum
        })

    # Step 4: canonical ordering
    other_factors = sorted(other_factors, key = prod_order_key)

    #step 5: rebuild node
    if len(other_factors) == 0:
        return {"type": "const", "value": product_of_const}

    if len(other_factors) == 1:
        if product_of_const == 1:
            return other_factors[0]
        return {"type": "mul", "const": product_of_const, "expr": other_factors[0]}
    
    prod_node = {"type": "prod", "factors": other_factors}
    if product_of_const != 1:
        return {"type": "mul", "const": product_of_const, "expr": prod_node}
    return prod_node                         

def normalize_sum(expr):
    """
    Normalizes sums.

    - Flattens nested sums
    - Removes zero terms
    - Eliminates degenerate sums
    """

    from .normalizer import normalize

    terms = [normalize(term) for term in expr["terms"]]
    
    new_terms = []
    for term in terms:
        if term["type"] == "sum":
            new_terms.extend(term["terms"])
        elif term["type"] == "const" and term["value"] == 0:
            pass
        else:
            new_terms.append(term)

    if len(new_terms) == 0:
        return {"type": "const", "value": 0}
    if len(new_terms) == 1:
        return new_terms[0]

    return {"type": "sum", "terms": new_terms}

def normalize_func(expr):
    """
    Normalizes function expressions.

    Ensures function arguments are valid variables.
    Functions are treated as atomic expressions.
    """

    from .normalizer import normalize

    arg = normalize(expr["arg"])

    if arg["type"] != "var":
        return unsupported(f"Unsupported argument in function: {expr['name']}")

    return {"type": expr["type"], "name": expr["name"], "arg": arg}