"""
Parser for PyCAS.

This module converts input strings into raw AST representation.
The parser guarantees syntactic correctness and basic semantic
validity (e.g. exponent constraints) but does NOT enforce algebraic
invariants or canonical structure.

All structural cleanup and validation is performed by the normalizer.
"""
from pycas.normalizer import normalize
import re

def desugar_string(s):
    """
    Preprocessed input strings to remove syntactic sugar.

    Currently supported:
    - sin^2(x) -> (sin(x))^2

    This step exists purely to simplify parsing and does not
    perform any algebraic transformation.

    Note: arguments must not contain nested parentheses.
    """

    pattern = r"(sin|cos|exp)\^(\d+)\(([^()]*)\)"
    replacement = r"(\1(\3))^\2"

    return re.sub(pattern, replacement, s)

def tokenize(s):
    """
    Converts an input string into a list of tokens.

    Token types include:
    - NUMBER
    - VAR
    - NAME (function names)
    - OP
    - LPAREN / RPAREN

    This tokenizer is intentionally simple and context-free.
    """
    i = 0
    tokens = []
    seen_var = None

    while i < len(s):
        ch = s[i]

        # Ignoring Whitespaces
        if ch.isspace():
            i += 1
            continue

        # Tokenizing Numbers
        if ch.isdigit():
            start = i
            dot_seen = False
            while i < len(s) and (s[i].isdigit() or (s[i] == "." and not dot_seen)):
                if s[i] == ".":
                    dot_seen = True
                i += 1
            number_str = s[start:i]
            if number_str.count(".") == 1:
                number = float(number_str)
            else:
                number = int(number_str)
            tokens.append(("NUMBER", number))
            continue
        
        # Tokenizing text
        # Single character as a variable, rest as function names
        if ch.isalpha():
            start = i
            while i < len(s) and s[i].isalpha():
                i += 1
            name = s[start:i]
            if len(name) == 1:
                if seen_var is None:
                    seen_var = name
                elif name != seen_var:
                    raise SyntaxError(f"Multiple Variables not supported: {seen_var}, {name}")
                tokens.append(("VAR", name))
            else:
                tokens.append(("NAME", name))
            continue
        
        # Tokenizing Symbols
        if ch in "+-^*()":
            if ch == "(":
                tokens.append(("LPAREN", ch))
            elif ch == ")":
                tokens.append(("RPAREN", ch))
            else:
                tokens.append(("OP", ch))
            i += 1
            continue

        else:
            raise SyntaxError(f"Invalid Input Character: {ch}")
        
    return tokens, seen_var

def current_pos(tokens, pos):
    """
    Returns the token at the current position if it exists.
    """
    return tokens[pos] if pos < len(tokens) else None

def consume(tokens, pos):
    """
    Returns the token at the current position and advances to next position.
    """
    return tokens[pos], pos+1

def can_start_term(token):
    """
    Checks if a token can start a term.

    A token can start a term only if it is a:
    - NUMBER
    - VAR
    - NAME
    - LPAREN
    """
    return (token[0] in {"NUMBER", "VAR", "NAME", "LPAREN"})

def parse_expr(tokens, pos):
    """
    Parse a sum-level expression.

    Grammar:
        expr := mul (('+' | '-') mul)*

    Returns:
        (ast, new_pos)
    """
    terms = []
    leftnode, new_pos = parse_mul(tokens, pos)
    terms.append(leftnode)

    token = current_pos(tokens, new_pos)
    while token is not None and token[0] == "OP" and token[1] in "+-":
        op, new_pos = consume(tokens, new_pos)
        rightnode, new_pos = parse_mul(tokens, new_pos)
        if op[1] == "-":
            rightnode = {"type": "mul", "const": -1, "expr": rightnode}
        terms.append(rightnode)
        token = current_pos(tokens, new_pos)

    if len(terms) == 1:
        return terms[0], new_pos
    else:
        return {"type": "sum", "terms": terms}, new_pos

def parse_mul(tokens, pos):
    """
    Parses a multiplication-level expression.

    Handles both explicit (*) and implicit multiplication.
    Does NOT apply distributive laws or simplification.

    Grammar:
        mul := power (('*' power) | power)*
    """

    factors = []
    const_value = 1

    node, new_pos = parse_power(tokens, pos)

    if node["type"] == "const":
        const_value *= node["value"]
    else:
        factors.append(node)

    while True:
        token = current_pos(tokens, new_pos)

        explicit = token is not None and token[0] == "OP" and token[1] == "*"
        implicit = token is not None and can_start_term(token)

        if not explicit and not implicit:
            break

        if explicit:
            _, new_pos = consume(tokens, new_pos)

        node, new_pos = parse_power(tokens, new_pos)

        if node["type"] == "const":
            const_value *= node["value"]
        else:
            factors.append(node)

    if len(factors) == 0:
        return {"type": "const", "value": const_value}, new_pos 

    if len(factors) == 1:
        if const_value == 1:
            return factors[0], new_pos
        else:
            return {"type": "mul", "const": const_value, "expr": factors[0]}, new_pos
    
    prod_node = {"type": "prod", "factors": factors}

    if const_value != 1:
        return {"type": "mul", "const": const_value, "expr": prod_node}, new_pos
    else:
        return prod_node, new_pos
    
def parse_term(tokens, pos):
    """
    Parses an atomic term:
    - number
    - variable
    - function call
    - parenthesized expression
    - unary minus

    Note: Function arguments are parsed as expressions; validity is enforced later.
    """

    token = current_pos(tokens, pos)

    if token is not None and token[0] == "OP" and token[1] == "-":
        unary_minus, new_pos = consume(tokens, pos)
        next_term, new_pos = parse_term(tokens, new_pos)
        ast = {"type": "mul", "const": -1, "expr": next_term}
        return ast, new_pos
    
    elif token is not None and token[0] == "NUMBER":
        number, new_pos = consume(tokens, pos)
        ast = {"type": "const", "value": number[1]}

    elif token is not None and token[0] == "VAR":
        var, new_pos = consume(tokens, pos)
        ast = {"type": "var", "variable": var[1]}

    elif token is not None and token[0] == "NAME":
        name, new_pos = consume(tokens, pos)

        lp = current_pos(tokens, new_pos)
        if lp is None or lp[0] != "LPAREN":
            raise SyntaxError(f"Expected '(' after function name {name[1]}")

        _, new_pos = consume(tokens, new_pos)
        arg_expr, new_pos = parse_expr(tokens, new_pos)

        rp = current_pos(tokens, new_pos)
        if rp is None or rp[0] != "RPAREN":
            raise SyntaxError("Parenthesis mismatch in function call")

        _, new_pos = consume(tokens, new_pos)

        ast = {"type": "func", "name": name[1], "arg": arg_expr}
        
        return ast, new_pos

    elif token is not None and token[0] == "LPAREN":
        LP, new_pos = consume(tokens, pos)
        inner_expr, new_pos = parse_expr(tokens, new_pos)
        expectedRP = current_pos(tokens, new_pos)
        if expectedRP is not None and expectedRP[0] == "RPAREN":
            RP, new_pos = consume(tokens, new_pos)
            ast = inner_expr
        else:
            raise SyntaxError("Parenthesis Mismatch!!")
    
    else:
        raise IOError(f"Unexpected Token: {token}")
    
    return ast, new_pos

def parse_power(tokens, pos):
    """
    Parses exponentiation.

    Grammar:
        power := term ('^' power)?

    Only constant, non-negative integer exponents are allowed.
    """
    base, new_pos = parse_term(tokens, pos)

    token = current_pos(tokens, new_pos)
    if token is not None and token[0] == "OP" and token[1] == "^":
        raised, new_pos = consume(tokens, new_pos)
        exponent, new_pos = parse_power(tokens, new_pos)

        if exponent["type"] != "const":
            raise SyntaxError("Exponent must be a constant integer")

        if not isinstance(exponent["value"], int):
            raise SyntaxError("Exponent must be an integer")

        if exponent["value"] < 0:
            raise SyntaxError("Negative exponents not supported yet")

        exp_value = exponent["value"]

        ast = {"type": "power", "base": base, "exp": exp_value}
        return ast, new_pos    

    return base, new_pos

def parse_string(s):
    """
    Entry point for parsing.

    Performs:
    - desugaring
    - tokenization
    - parsing
    - normalization

    Returns a canonical AST.
    """
    
    s = desugar_string(s)
    tokens, seen_var = tokenize(s)
    ast, pos = parse_expr(tokens, 0)
    if pos != len(tokens):
        raise SyntaxError(f"string wasn't parsed beyond index {pos}")
    return {
        "ast": normalize(ast),
        "var": seen_var or "x"
    }