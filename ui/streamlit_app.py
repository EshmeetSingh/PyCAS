"""
Minimal Streamlit UI for PyCAS v1. This module handles input/output
and delegates all symbolic logic to the core engine. It does not 
contain any math logic.
"""

import streamlit as st
from pycas.core import integrate, differentiate
from pycas.parser import parse_string
from pycas.pretty_printer import to_string

def render_steps(steps):
    """
    Collects the step format in a list.

    Current step format:
        - Top-level strings (level 0)
            - Inner list's first element (level 1)
                - Inner list's remaining elements (level 2) 
    
    Deeper nesting is intentionally unsupported in v1.
    """
    lines = []

    for step in steps:
        if isinstance(step, str):
            lines.append(f"- {step}")
        
        elif isinstance(step, list) and len(step) > 0:
            parent = step[0]
            lines.append(f"  - {parent}")

            for child in step[1:]:
                lines.append(f"    - {child}")
    
    return lines

def render_calculus_result(operation, expr, mode, var_name):
    """
    Helper function to render calculus results in UI.
    """
    if operation == "Integration":
        result = integrate(expr, mode)
        st.subheader("Integral:")
        if "error" in result:
            st.error(f"Error: {result['reason']}")
        else:
            st.write(to_string(result['result'], mode, var_name))

            with st.expander("**Show Steps**"):
                lines = render_steps(result['steps'])
                st.markdown("\n".join(lines), unsafe_allow_html = False)
    else:
        # Differentiation
        result = differentiate(expr, mode)
        st.subheader("Derivative:")
        if "error" in result:
            st.error(f"Error: {result['reason']}")
        else:
            st.write(to_string(result['result'], mode, var_name))

st.title("PyCAS")

# Input
expression = st.text_input("**Enter the Expression**", placeholder = "x^2 + 2x + cos(x) + 1")

col1, col2 = st.columns([0.5, 0.5])

with col1:
    operation = st.radio("**Select Operation**", ["Integration", "Differentiation"])
with col2:
    mode = st.radio("**Select Output Mode**", ["Fraction", "Decimal"])

display_mode = mode.lower()

if st.button("Calculate"):
    # Normalized Expression
    if not expression:
        st.warning("Enter the expression first.")
    else:
        try:
            parsed = parse_string(expression)
            expr = parsed["ast"]
            var_name = parsed["var"]
        except Exception as e:
            st.error(e)
            st.stop()

        st.divider()
        normalized_str = to_string(expr, display_mode, var_name)
        st.subheader("Normalized Expression:")
        st.code(normalized_str)

        # Results
        st.divider()
        render_calculus_result(operation, expr, display_mode, var_name)            