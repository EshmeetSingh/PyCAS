# PyCAS — A Minimal Symbolic Calculus Engine in Python

PyCAS is a **minimal, invariant-driven symbolic calculus engine** written in Python.
It supports symbolic **differentiation** and **integration** over a deliberately restricted algebraic domain, with a strong emphasis on **correctness, canonical representations, and explicit failure modes**.

This project was built as a **learning-first system**, focusing on principled design rather than feature breadth.

---

## ✨ Features (v1)

### Core Capabilities

* Symbolic differentiation
* Symbolic integration (restricted domain)
* Exact arithmetic using rational numbers (`fractions.Fraction`)
* Canonical AST normalization
* Step-by-step reasoning output
* Loud failure for unsupported mathematics

### Supported Expressions

* Constants
* Single variable (internally canonicalized)
* Monomials (`x^n`, `n ≥ 0`)
* Constant multiples
* Sums
* Products of atomic factors (normalized form)
* Elementary functions:

  * `sin(x)`
  * `cos(x)`
  * `exp(x)`

---

## 🧠 Design Philosophy

PyCAS was designed around the following principles:

* **Correctness over coverage**
* **Explicit invariants over ad-hoc simplification**
* **Single-variable calculus only**
* **Clear separation of concerns**
* **Unsupported math must fail loudly**

Rather than attempting to handle “everything a CAS should,” PyCAS defines a **strict algebraic domain** and enforces it rigorously.

---

## 🏗 Architecture Overview

PyCAS is split into clearly defined layers:

### 1. Parser

* Recursive-descent parser
* Converts user input (`str`) into AST
* Supports:

  * implicit multiplication (`2x`, `xsin(x)`)
  * explicit multiplication (`*`)
  * powers (`^`)
  * unary minus
  * function calls (`sin(x)`, `cos(x)`, `exp(x)`)
* Performs **desugaring** (e.g. `sin^2(x) → (sin(x))^2`)
* Outputs a normalized AST plus the original variable name

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

Atomic expressions are AST nodes that are treated as indivisible during algebraic manipulation (variables, powers, and elementary functions). Only atomic expressions may appear as factors inside a product.

---

### 3. Normalization

Normalization is **bottom-up** and may change node types.

Responsibilities:

* Flatten nested sums and products
* Absorb constants
* Combine powers of the variable
* Enforce canonical ordering of factors
* Eliminate redundant structure

After normalization, **all AST invariants must hold**.

---

### 4. Invariants (Core of the System)

PyCAS enforces structural invariants aggressively using assertion-based checks.

Examples:

* No nested `mul` nodes
* No `mul` wrapping constants
* `power` exponents are `≥ 2` post-normalization
* `prod` contains only atomic factors
* `prod` contains at least two factors
* At most one constant per product
* Function arguments must be atomic variables
* Only supported function names are allowed

**Invariants are asserted on:**

* normalized input expressions
* differentiation outputs
* integration outputs

This prevents silent regressions and enforces internal correctness.

---

### 5. Calculus Rules

Rule-based symbolic calculus is implemented over normalized ASTs.

#### Differentiation

* Linearity
* Power rule (`d/dx(x^n)`)
* Constant multiple rule
* Elementary functions (`sin`, `cos`, `exp`)

❌ Product rule intentionally **not implemented in v1**

---

#### Integration

* Linearity
* Power rule (`∫ x^n dx`)
* Constant multiple rule
* Elementary functions (`sin`, `cos`, `exp`)

❌ Logarithms, substitution, and product-based integration are intentionally excluded

---

### 6. Pretty Printer

* Converts normalized ASTs into readable mathematical strings
* Handles:

  * precedence
  * parentheses
  * negative coefficients
* Supports:

  * exact fraction mode
  * decimal display mode
* Preserves the **user’s original variable name**, even though the engine operates on a canonical internal variable

---

## 🖥 User Interface (v1)

PyCAS includes a **minimal Streamlit-based UI**.

The UI allows users to:

* input expressions as strings
* view the normalized canonical form
* compute symbolic derivatives or integrals
* inspect step-by-step reasoning

### UI Design Constraints

* No mathematical logic lives in the UI
* UI acts purely as a presentation layer
* All computation is delegated to the core engine

This keeps the system modular and testable.

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

## 🚀 Running the Project

### Install (editable mode)

```bash
pip install -e .
```

### Run the UI

```bash
streamlit run ui/streamlit_app.py
```

---

## 🔮 Planned Extensions (Intentionally Deferred)

The following are **out of scope for v1** to preserve correctness guarantees:

* Product rule
* Chain rule
* Logarithms
* Substitution-based integration
* Composite functions
* Advanced algebraic simplification

These will be considered only after v1 is frozen.

---

## 📌 Why This Project Exists

PyCAS was built as a **learning milestone**, not a feature race:

* From informal scripts → invariant-driven systems
* From symbolic manipulation → canonical representations
* From black-box results → explicit reasoning steps

The project prioritizes **clarity, discipline, and correctness** over completeness.

---

## 👤 Author

Built by **Eshmeet Singh**
As part of a focused effort to build principled, well-structured software systems.

---


