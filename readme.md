# PyCAS — A Minimal Symbolic Calculus Engine in Python

PyCAS is a **minimal, invariant-driven symbolic calculus engine** written in Python.
It supports symbolic **differentiation** and **integration** over a deliberately constrained algebraic domain, with a strong emphasis on **correctness, canonical representations, and explicit failure modes**.

Rather than maximizing feature coverage, PyCAS prioritizes **structural discipline**, **predictable behavior**, and **clear architectural boundaries**.

---

## 🔗 Live Demo

A deployed Streamlit demo is available here:

**[https://eshmeetsingh-pycas-uistreamlit-app-n3wvfl.streamlit.app](https://eshmeetsingh-pycas-uistreamlit-app-n3wvfl.streamlit.app)**

The demo allows you to:

* enter symbolic expressions
* inspect their canonical normalized form
* compute derivatives and integrals (within the supported domain)
* observe explicit failure messages for unsupported mathematics

---

## ✨ Core Capabilities

* Symbolic differentiation
* Symbolic integration (restricted domain)
* Exact arithmetic using rational numbers (`fractions.Fraction`)
* Canonical AST normalization
* Step-by-step reasoning output
* Loud, explicit failure for unsupported operations

---

## 🧮 Supported Expressions

PyCAS operates over a **single-variable algebraic domain** and supports:

* Constants
* A single variable (internally canonicalized)
* Monomials (`x^n`, `n ≥ 0`)
* Constant multiples
* Sums
* Products of atomic factors (normalized form)
* Elementary functions:

  * `sin(x)`
  * `cos(x)`
  * `exp(x)`

Expressions outside this domain are **rejected explicitly**, rather than being approximated or simplified heuristically.

---

## 🧠 Design Philosophy

PyCAS is built around the following principles:

* **Correctness over coverage**
* **Explicit invariants over ad-hoc simplification**
* **Canonical representations**
* **Clear separation of concerns**
* **No silent fallbacks**

Unsupported mathematics is treated as an error condition, not an opportunity for guesswork.

---

## 🏗 Architecture Overview

PyCAS is structured as a small, clearly layered system:

### 1. Parser

* Recursive-descent parser
* Converts user input (`str`) into an AST
* Supports:

  * implicit multiplication (`2x`, `xsin(x)`)
  * explicit multiplication (`*`)
  * powers (`^`)
  * unary minus
  * function calls (`sin(x)`, `cos(x)`, `exp(x)`)
* Performs desugaring (e.g. `sin^2(x) → (sin(x))^2`)
* Preserves the user’s original variable name

---

### 2. Abstract Syntax Tree (AST)

All expressions are represented as explicit AST nodes:

```python
# Constant
{"type": "const", "value": number}

# Variable
{"type": "var", "variable": "x"}

# Power (monomial only)
{"type": "power", "base": <var>, "exp": n}

# Constant multiple
{"type": "mul", "const": c, "expr": <expression>}

# Product of atomic factors
{"type": "prod", "factors": [<atomic_expr>, ...]}

# Sum of expressions
{"type": "sum", "terms": [<expression>, ...]}

# Elementary function
{"type": "func", "name": "sin|cos|exp", "arg": <var>}
```

Only **atomic expressions** may appear as factors inside a product.
This restriction is enforced consistently throughout the system.

---

### 3. Normalization

Normalization is **bottom-up** and invariant-preserving.

Responsibilities include:

* Flattening nested sums and products
* Absorbing constants
* Combining powers of the variable
* Enforcing canonical ordering
* Eliminating redundant structure

After normalization, **all AST invariants must hold**.

---

### 4. Invariants (Core of the System)

Structural invariants are enforced aggressively via assertion-based checks.

Examples include:

* No nested `mul` nodes
* No `mul` wrapping constants
* `power` exponents are `≥ 2` post-normalization
* `prod` contains only atomic factors
* At most one constant per product
* Function arguments must be atomic variables
* Only supported function names are allowed

Invariants are asserted on:

* normalized input expressions
* differentiation outputs
* integration outputs

This prevents silent regressions and guarantees internal consistency.

---

### 5. Calculus Rules

Symbolic calculus is implemented as explicit, rule-based transformations over normalized ASTs.

#### Differentiation

* Linearity
* Power rule
* Constant multiple rule
* Elementary functions (`sin`, `cos`, `exp`)

#### Integration

* Linearity
* Power rule
* Constant multiple rule
* Elementary functions (`sin`, `cos`, `exp`)

Operations outside the supported rule set fail explicitly.

---

### 6. Pretty Printer

* Converts normalized ASTs into readable mathematical strings
* Handles precedence, parentheses, and negative coefficients
* Supports exact fraction and decimal display modes
* Preserves the user’s original variable name

---

## 🖥 User Interface

PyCAS includes a **minimal Streamlit-based UI**.

Design constraints:

* No mathematical logic lives in the UI
* The UI acts purely as a presentation layer
* All computation is delegated to the core engine

This separation keeps the system modular, testable, and predictable.

---

## 📂 Project Structure

```
PyCAS/
├── src/
│   └── pycas/
│       ├── core.py
│       ├── parser.py
│       ├── normalizer.py
│       ├── normalizer_rules.py
│       ├── rules.py
│       ├── pretty_printer.py
│       └── errors.py
│
├── ui/
│   └── streamlit_app.py
│
├── examples/
│   ├── demo.py
│   └── invariants.py
│
├── README.md
└── pyproject.toml
```

---

## 📌 Why PyCAS Exists

PyCAS was built as a **discipline-focused systems project**, emphasizing:

* invariant-driven design
* canonical internal representations
* explicit reasoning over symbolic mathematics
* correctness guarantees through restriction

It intentionally avoids heuristic simplification in favor of **clarity, predictability, and correctness**.

---

## 👤 Author

Built by **Eshmeet Singh**


