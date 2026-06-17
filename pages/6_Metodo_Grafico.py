import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from core.fmt import br
from core.modelo import resolver

st.set_page_config(page_title="Método Gráfico", page_icon="📐", layout="wide")
st.title("Método Gráfico — Visualização da Solução Ótima")
st.caption("Projeção 2D: Soja × Algodão (Milho e Cana fixos nos valores ótimos)")

res = resolver()
qtds = res["quantidades"]
x1_opt, x2_opt, x3_opt, x4_opt = qtds

st.info(f"""
**Como funciona a projeção 2D:**
Fixamos Milho = {x2_opt:.2f} ha e Cana = {x4_opt:.0f} ha nos valores ótimos
e mostramos o problema reduzido para **Soja (x₁)** e **Algodão (x₃)**.
As restrições são ajustadas descontando o consumo já alocado para Milho e Cana.
""")

# Adjusted RHS
terra_adj = 5000       - x2_opt        - x4_opt        # 3943.88
orc_adj   = 20_000_000 - 3200*x2_opt   - 2800*x4_opt   # 17_020_408
mo_adj    = 60_000     - 15*x2_opt     - 8*x4_opt      # 51_158
dem1      = 2500.0
dem3      = 1500.0

st.divider()

col_graf, col_exp = st.columns([3, 2])

with col_graf:
    st.subheader("Gráfico: Região Viável e Ponto Ótimo")

    x_max = 2700.0
    y_max = 1600.0
    x = np.linspace(0, x_max, 800)

    fig, ax = plt.subplots(figsize=(8, 6.8), facecolor="#0A1A0D")
    ax.set_facecolor("#0F1F12")

    # ── Linhas das restrições ──────────────────────────────────────────────
    # Terra: x1 + x3 = terra_adj  →  x3 = terra_adj - x1
    y_terra = terra_adj - x
    # Orçamento: 4500x1 + 6000x3 = orc_adj  →  x3 = (orc_adj - 4500x1)/6000
    y_orc   = (orc_adj - 4500*x) / 6000
    # MO: 12x1 + 22x3 = mo_adj  →  x3 = (mo_adj - 12x1)/22
    y_mo    = (mo_adj - 12*x) / 22
    # Demandas: x1 = dem1 (vertical), x3 = dem3 (horizontal)

    cores = {
        "Terra":      "#52B788",
        "Orçamento":  "#F4D03F",
        "Mão de Obra":"#E74C3C",
        "Dem. Soja":  "#95D5B2",
        "Dem. Algodão":"#AED6F1",
    }

    ax.plot(x, y_terra, color=cores["Terra"],      lw=2, label=f"Terra: x₁+x₃ ≤ {terra_adj:.0f}")
    ax.plot(x, y_orc,   color=cores["Orçamento"],  lw=2, label=f"Orçamento (÷1000)")
    ax.plot(x, y_mo,    color=cores["Mão de Obra"],lw=2, label=f"Mão de Obra")
    ax.axvline(dem1, color=cores["Dem. Soja"],     lw=2, ls="--", label=f"Dem. Soja ≤ {dem1:.0f} ha")
    ax.axhline(dem3, color=cores["Dem. Algodão"],  lw=2, ls="--", label=f"Dem. Algodão ≤ {dem3:.0f} ha")

    # ── Região viável ──────────────────────────────────────────────────────
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection

    xs = np.linspace(0, x_max, 2000)
    ys_terra = terra_adj - xs
    ys_orc   = (orc_adj - 4500*xs) / 6000
    ys_mo    = (mo_adj - 12*xs) / 22
    ys_d1    = np.full_like(xs, dem1)  # x1 <= dem1 → mask
    ys_d3    = np.full_like(xs, dem3)  # x3 <= dem3

    # Feasible: x1 in [0,dem1], x3 in [0, min(terra, orc, mo, dem3)]
    y_upper = np.minimum(np.minimum(ys_terra, ys_orc), np.minimum(ys_mo, dem3))
    y_upper = np.clip(y_upper, 0, y_max)
    mask = (xs >= 0) & (xs <= dem1)
    ax.fill_between(xs[mask], 0, y_upper[mask],
                    alpha=0.18, color="#52B788", label="Região viável")

    # ── Isoprofit lines ────────────────────────────────────────────────────
    Z_opt = 3500*x1_opt + 4200*x3_opt
    for frac in [0.4, 0.7, 1.0]:
        Z = Z_opt * frac
        y_iso = (Z - 3500*x) / 4200
        style = "-" if frac == 1.0 else ":"
        lw    = 2.5 if frac == 1.0 else 1.0
        alpha = 1.0 if frac == 1.0 else 0.5
        label = f"Isolucro Z = R$ {Z/1e6:.2f}M" if frac == 1.0 else None
        ax.plot(x, y_iso, color="#BDC3C7", lw=lw, ls=style, alpha=alpha, label=label)

    # ── Vértices (pontos de canto) ─────────────────────────────────────────
    vertices = []

    # Interseção Terra × MO: x1+x3=terra_adj, 12x1+22x3=mo_adj
    eps = 0.5  # tolerância para comparações de fronteira

    def valido(vx, vy):
        return -eps <= vx <= dem1+eps and -eps <= vy <= dem3+eps

    A = np.array([[1, 1], [12, 22]])
    b = np.array([terra_adj, mo_adj])
    try:
        p = np.linalg.solve(A, b)
        if valido(p[0], p[1]):
            vertices.append((p[0], p[1], "Terra∩MO"))
    except Exception:
        pass

    A = np.array([[4500, 6000], [12, 22]])
    b = np.array([orc_adj, mo_adj])
    try:
        p = np.linalg.solve(A, b)
        if valido(p[0], p[1]):
            vertices.append((p[0], p[1], "Orç∩MO"))
    except Exception:
        pass

    x3_mo_at_d1 = (mo_adj - 12*dem1) / 22
    if valido(dem1, x3_mo_at_d1):
        vertices.append((dem1, x3_mo_at_d1, "Dem.Soja∩MO"))

    x3_orc_at_d1 = (orc_adj - 4500*dem1) / 6000
    if valido(dem1, x3_orc_at_d1) and abs(x3_orc_at_d1 - x3_mo_at_d1) > eps:
        vertices.append((dem1, x3_orc_at_d1, "Dem.Soja∩Orç"))

    x1_mo_at_d3 = (mo_adj - 22*dem3) / 12
    if valido(x1_mo_at_d3, dem3):
        vertices.append((x1_mo_at_d3, dem3, "MO∩Dem.Algodão"))

    for vx, vy, vlabel in vertices:
        ax.scatter(vx, vy, color="white", s=70, zorder=5, edgecolors="#AAAAAA", linewidth=0.8)

    # ── Ponto ótimo ────────────────────────────────────────────────────────
    ax.scatter(x1_opt, x3_opt, color="#F4D03F", s=250, zorder=10,
               marker="*", label=f"★ Ótimo ({x1_opt:.0f}, {x3_opt:.0f})")
    ax.annotate(
        f"★ ({x1_opt:.0f}, {x3_opt:.0f})",
        xy=(x1_opt, x3_opt),
        xytext=(x1_opt - 550, x3_opt - 220),
        color="#F4D03F", fontsize=9, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#0A1A0D", edgecolor="#F4D03F", alpha=0.85),
        arrowprops=dict(arrowstyle="->", color="#F4D03F", lw=1.5),
    )

    # ── Formatação ────────────────────────────────────────────────────────
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("x₁ — Soja (ha)", color="white", fontsize=11)
    ax.set_ylabel("x₃ — Algodão (ha)", color="white", fontsize=11)
    ax.set_title("Região Viável e Ponto Ótimo (Simplex)", color="white", fontsize=13, fontweight="bold")
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2D6A4F")

    # legenda fora da área do gráfico, abaixo
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc="lower center", bbox_to_anchor=(0.5, 0.01),
               ncols=3, fontsize=8, facecolor="#1A2E1D",
               labelcolor="white", edgecolor="#2D6A4F")
    fig.subplots_adjust(bottom=0.22, top=0.95)
    st.pyplot(fig)
    plt.close()

with col_exp:
    st.subheader("Como ler o gráfico")
    st.markdown(f"""
**Eixos**
- Eixo X = hectares de Soja (x₁)
- Eixo Y = hectares de Algodão (x₃)

**Retas (restrições)**
Cada linha representa um limite máximo.
A solução deve ficar *abaixo e à esquerda* de todas elas.

**Região viável** (área verde sombreada)
Todos os pontos dentro dessa área satisfazem
as restrições simultaneamente.
O solver busca o ponto ótimo *dentro* dela.

**Pontos de vértice** (círculos brancos)
Em LP, a solução ótima sempre fica em um vértice
(canto) da região viável.
O Simplex percorre esses vértices até encontrar o melhor.

**Isoprofit** (linhas cinzas)
Mostram combinações de Soja × Algodão com
o mesmo lucro. Quanto mais para cima/direita,
maior o lucro — mas a região viável limita até onde chegar.

**Ponto ótimo** ⭐
`Soja = {x1_opt:.0f} ha | Algodão = {x3_opt:.0f} ha`

É onde a isoprofit mais alta toca a fronteira da região viável.
""")

    st.success(f"""
**Restrições ativas no ótimo:**
- Orçamento: 100% consumido
- Mão de Obra: 100% consumida

A reta de MO (vermelha) passa pelo ponto ótimo —
confirma que é o gargalo.
""")

st.divider()
st.subheader("Avaliando cada vértice")
st.markdown("""
O Simplex avalia o lucro em cada vértice e escolhe o maior.
Aqui estão os principais pontos de canto da região viável:
""")

import pandas as pd
rows = []
for vx, vy, vlabel in vertices:
    z = 3500*vx + 4200*vy
    rows.append({"Ponto": vlabel, "Soja (ha)": f"{vx:.2f}", "Algodão (ha)": f"{vy:.2f}",
                 "Lucro parcial (R$)": f"{br(z)}", "Ótimo?": "★ SIM" if abs(vx - x1_opt) < 1 and abs(vy - x3_opt) < 1 else ""})

# deduplicar vértices muito próximos
vistos, rows_uniq = [], []
for r in rows:
    coord = (r["Soja (ha)"], r["Algodão (ha)"])
    if coord not in vistos:
        vistos.append(coord)
        rows_uniq.append(r)
rows = rows_uniq

if rows:
    df_v = pd.DataFrame(rows)
    st.dataframe(df_v, use_container_width=True, hide_index=True)

st.caption("Nota: lucro parcial considera apenas Soja e Algodão. O lucro total inclui Milho e Cana.")
