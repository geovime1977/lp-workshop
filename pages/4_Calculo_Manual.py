import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from core.fmt import br
from core.modelo import resolver, DEFAULT_PARAMS, CULTURAS

st.set_page_config(page_title="Etapa IV — Cálculo Manual", page_icon="✏️", layout="wide")
st.title("Etapa IV — Resolução Manual")
st.caption("Derivando a solução ótima identificando restrições ativas e resolvendo o sistema linear — sem solver")
st.divider()

res = resolver()
p   = DEFAULT_PARAMS
qtds     = res["quantidades"]
receitas = res["receita_por_cultura"]
lucro    = res["lucro_otimo"]

st.markdown("""
Em Programação Linear a solução ótima **sempre ocorre em um vértice** da região viável —
um ponto onde um conjunto de restrições está ativo (folga zero) simultaneamente.

Com **4 variáveis** precisamos de **4 restrições ativas** para identificar o vértice ótimo.
A abordagem manual é: identificar quais restrições estão ativas e resolver o sistema resultante.
""")

st.divider()

# ── Passo 1 ──────────────────────────────────────────────────────────────────
st.header("Passo 1 — Identificar restrições ativas")

st.markdown("""
Analise o uso dos recursos na solução (obtida pelo solver ou por tentativa racional):
""")

uso = res["uso"]
labels = {"terra": "Terra", "orcamento": "Orçamento", "agua": "Água", "mao_obra": "Mão de Obra"}
unids  = {"terra": "ha", "orcamento": "R$", "agua": "m³", "mao_obra": "hh"}
for key, (usado, total, unit) in uso.items():
    pct   = usado / total * 100
    ativo = pct >= 99.9
    icone = "🔴 **ATIVA** (folga zero)" if ativo else f"🟢 com folga ({br(total - usado)} {unit} sobrando)"
    st.markdown(f"- **{labels[key]}**: {br(usado)} / {br(total)} {unit} → {icone}")

st.info("""
**Restrições ativas identificadas:**
- R2 — Orçamento (100% consumido)
- R4 — Mão de Obra (100% consumida)
- R5 — Demanda Soja: x₁ = 2.500 ha (no limite)
- R5 — Demanda Cana: x₄ = 1.000 ha (no limite)
""")

st.divider()

# ── Passo 2 ──────────────────────────────────────────────────────────────────
st.header("Passo 2 — Fixar variáveis nos limites de demanda")

st.markdown("""
Soja e Cana atingiram seus limites máximos de demanda → **valores fixados**:
""")

col1, col2 = st.columns(2)
col1.success("**x₁ = 2.500 ha** (Soja — limite de demanda atingido)")
col2.success("**x₄ = 1.000 ha** (Cana — limite de demanda atingido)")

st.markdown("Substituímos esses valores nas duas restrições ativas para eliminar x₁ e x₄:")

st.latex(r"""
\text{R2 (Orçamento):} \quad
4.500 \underbrace{(2.500)}_{x_1} + 3.200\,x_2 + 6.000\,x_3 + 2.800\underbrace{(1.000)}_{x_4} = 20.000.000
""")
st.latex(r"""
\Rightarrow \quad 3.200\,x_2 + 6.000\,x_3 = 20.000.000 - 11.250.000 - 2.800.000
""")
st.latex(r"""
\boxed{3.200\,x_2 + 6.000\,x_3 = 5.950.000} \quad \text{...(I)}
""")

st.latex(r"""
\text{R4 (Mão de Obra):} \quad
12\underbrace{(2.500)}_{x_1} + 15\,x_2 + 22\,x_3 + 8\underbrace{(1.000)}_{x_4} = 60.000
""")
st.latex(r"""
\Rightarrow \quad 15\,x_2 + 22\,x_3 = 60.000 - 30.000 - 8.000
""")
st.latex(r"""
\boxed{15\,x_2 + 22\,x_3 = 22.000} \quad \text{...(II)}
""")

st.divider()

# ── Passo 3 ──────────────────────────────────────────────────────────────────
st.header("Passo 3 — Resolver o sistema 2×2 por substituição")

st.markdown("**Isolar x₂ em (II):**")
st.latex(r"""
x_2 = \frac{22.000 - 22\,x_3}{15} \quad \text{...(III)}
""")

st.markdown("**Substituir (III) em (I):**")
st.latex(r"""
3.200 \cdot \frac{22.000 - 22\,x_3}{15} + 6.000\,x_3 = 5.950.000
""")
st.latex(r"""
\frac{70.400.000 - 70.400\,x_3}{15} + 6.000\,x_3 = 5.950.000
""")
st.latex(r"""
4.693.333{,}33 - 4.693{,}33\,x_3 + 6.000\,x_3 = 5.950.000
""")
st.latex(r"""
1.306{,}67\,x_3 = 1.256.666{,}67
""")
st.latex(r"""
\boxed{x_3 = \frac{1.256.666{,}67}{1.306{,}67} \approx 961{,}73 \text{ ha} \quad \text{(Algodão)}}
""")

st.markdown("**Substituir x₃ de volta em (III):**")
st.latex(r"""
x_2 = \frac{22.000 - 22 \times 961{,}73}{15} = \frac{22.000 - 21.158{,}06}{15} = \frac{841{,}94}{15}
""")
st.latex(r"""
\boxed{x_2 \approx 56{,}12 \text{ ha} \quad \text{(Milho)}}
""")

st.divider()

# ── Passo 4 ──────────────────────────────────────────────────────────────────
st.header("Passo 4 — Calcular o lucro ótimo Z*")

x1r, x2r, x3r, x4r = 2500, 56.12, 961.73, 1000
p1 = 3500 * x1r
p2 = 2300 * x2r
p3 = 4200 * x3r
p4 = 3400 * x4r
z_manual = p1 + p2 + p3 + p4

st.code(f"""
Z* = 3.500 × {br(x1r, 4)}  +  2.300 × {br(x2r, 4)}  +  4.200 × {br(x3r, 4)}  +  3.400 × {br(x4r, 4)}

Z* = {br(p1, 0)}  +  {br(p2, 0)}  +  {br(p3, 0)}  +  {br(p4, 0)}

Z* ≈ R$ {br(z_manual, 0)}
""", language=None)

col1, col2, col3 = st.columns(3)
col1.metric("Z* (valores arredondados)", f"R$ {br(z_manual, 0)}")
col2.metric("Z* (solver — exato)", f"R$ {br(lucro, 0)}")
col3.metric("Diferença por arredondamento", f"R$ {br(lucro - z_manual, 0)}")

st.info("""
A diferença de R$ 25 é apenas arredondamento: x₂ e x₃ têm casas decimais infinitas.
O solver opera com precisão de máquina (~15 dígitos) e obtém Z* = R$ 16.318.367,33.
""")

st.divider()

# ── Passo 5 ──────────────────────────────────────────────────────────────────
st.header("Passo 5 — Verificar as demais restrições")

st.markdown("Confirmar que a solução encontrada **respeita todas as restrições**:")

r_terra = x1r + x2r + x3r + x4r
r_agua  = 600*x1r + 800*x2r + 500*x3r + 1500*x4r

st.code(f"""
R1 Terra:      {br(x1r, 4)} + {br(x2r, 4)} + {br(x3r, 4)} + {br(x4r, 4)} = {br(r_terra)} ha  ≤  5.000,00 ha  ✓

R2 Orçamento:  4.500×{br(x1r, 0)} + 3.200×{br(x2r, 4)} + 6.000×{br(x3r, 4)} + 2.800×{br(x4r, 0)}
             ≈ R$ 20.000.000,00  ≤  R$ 20.000.000,00  ✓  ★ ATIVA

R3 Água:       600×{br(x1r, 0)} + 800×{br(x2r, 4)} + 500×{br(x3r, 4)} + 1.500×{br(x4r, 0)}
             ≈ {br(r_agua, 0)} m³  ≤  4.000.000,00 m³  ✓

R4 Mão de Obra: 12×{br(x1r, 0)} + 15×{br(x2r, 4)} + 22×{br(x3r, 4)} + 8×{br(x4r, 0)}
              ≈ 60.000,00 hh  ≤  60.000,00 hh  ✓  ★ ATIVA

R5 Demanda:    x₁={br(x1r, 0)}≤2.500  x₂={br(x2r, 4)}≤2.000  x₃={br(x3r, 4)}≤1.500  x₄={br(x4r, 0)}≤1.000  ✓
""", language=None)

st.success(f"""
**Solução confirmada:**
x₁ = 2.500 ha (Soja) | x₂ ≈ 56,12 ha (Milho) | x₃ ≈ 961,73 ha (Algodão) | x₄ = 1.000 ha (Cana)

**Z\\* ≈ R$ {br(z_manual, 0)}** — equivalente ao ótimo do solver (diferença apenas por arredondamento)
""")
