import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st

st.set_page_config(page_title="Modelagem Matemática", page_icon="📐", layout="wide")
st.title("Etapa II — Modelagem Matemática")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Variáveis de Decisão")
    st.latex(r"""
    \begin{aligned}
    x_1 &= \text{hectares plantados de Soja} \\
    x_2 &= \text{hectares plantados de Milho} \\
    x_3 &= \text{hectares plantados de Algodão} \\
    x_4 &= \text{hectares plantados de Cana-de-Açúcar}
    \end{aligned}
    """)

    st.subheader("Função Objetivo")
    st.latex(r"""
    \text{Maximizar } Z = 3500x_1 + 2300x_2 + 4200x_3 + 3400x_4
    """)
    st.caption("onde os coeficientes representam a margem líquida em R$/ha de cada cultura")

with col2:
    st.subheader("Restrições")

    st.markdown("**R1 — Terra disponível (ha)**")
    st.latex(r"x_1 + x_2 + x_3 + x_4 \leq 5.000")

    st.markdown("**R2 — Orçamento de insumos (R$)**")
    st.latex(r"4500x_1 + 3200x_2 + 6000x_3 + 2800x_4 \leq 20.000.000")

    st.markdown("**R3 — Disponibilidade hídrica (m³)**")
    st.latex(r"600x_1 + 800x_2 + 500x_3 + 1500x_4 \leq 4.000.000")

    st.markdown("**R4 — Mão de obra (hh)**")
    st.latex(r"12x_1 + 15x_2 + 22x_3 + 8x_4 \leq 60.000")

    st.markdown("**R5 — Demanda máxima de mercado (ha)**")
    st.latex(r"x_1 \leq 2500, \quad x_2 \leq 2000, \quad x_3 \leq 1500, \quad x_4 \leq 1000")

    st.markdown("**R6 — Não-negatividade**")
    st.latex(r"x_1, x_2, x_3, x_4 \geq 0")

st.divider()
st.subheader("Modelo Completo")
st.latex(r"""
\begin{aligned}
&\text{Maximizar} \quad Z = 3500x_1 + 2300x_2 + 4200x_3 + 3400x_4 \\[6pt]
&\text{Sujeito a:} \\
&x_1 + x_2 + x_3 + x_4 \leq 5.000 \\
&4500x_1 + 3200x_2 + 6000x_3 + 2800x_4 \leq 20.000.000 \\
&600x_1 + 800x_2 + 500x_3 + 1500x_4 \leq 4.000.000 \\
&12x_1 + 15x_2 + 22x_3 + 8x_4 \leq 60.000 \\
&x_1 \leq 2500, \quad x_2 \leq 2000, \quad x_3 \leq 1500, \quad x_4 \leq 1000 \\
&x_1, x_2, x_3, x_4 \geq 0
\end{aligned}
""")
