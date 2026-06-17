import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pandas as pd
from core.fmt import br
from core.modelo import resolver, DEFAULT_PARAMS, DEFAULT_RECURSOS
from core.slides import gerar_pptx

st.set_page_config(page_title="Resultados e Slides", page_icon="📊", layout="wide")
st.title("Resultados e Downloads")
st.divider()

resultado = st.session_state.get("resultado_lp") or resolver()
culturas  = resultado["culturas"]
qtds      = resultado["quantidades"]
receitas  = resultado["receita_por_cultura"]
lucro     = resultado["lucro_otimo"]

st.metric("Lucro Total Ótimo", f"R$ {br(lucro)}")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hectares por Cultura")
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="#0A1A0D")
    ax.set_facecolor("#1A2E1D")
    colors = ["#52B788", "#95D5B2", "#2D6A4F", "#F4D03F"]
    bars = ax.bar(culturas, qtds, color=colors, edgecolor="#0A1A0D", linewidth=0.5)
    for bar, q in zip(bars, qtds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                f"{br(q)}", ha="center", va="bottom", color="white", fontsize=10)
    ax.set_ylabel("Hectares", color="white")
    ax.tick_params(colors="white", labelsize=9)
    ax.set_title("Alocação Ótima de Hectares", color="white", fontsize=12)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2D6A4F")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Participação na Receita")
    fig2, ax2 = plt.subplots(figsize=(6, 4), facecolor="#0A1A0D")
    cores_pie = ["#52B788", "#95D5B2", "#2D6A4F", "#F4D03F"]
    wedges, texts, autotexts = ax2.pie(
        receitas, labels=culturas, autopct="%1.1f%%",
        colors=cores_pie, textprops={"color": "white", "fontsize": 10},
        pctdistance=0.75, wedgeprops={"edgecolor": "#0A1A0D", "linewidth": 1.5}
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
    ax2.set_facecolor("#0A1A0D")
    ax2.set_title("Participação na Receita Total", color="white", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.divider()
st.subheader("Uso dos Recursos")
labels_rec = {"terra": "Terra (ha)", "orcamento": "Orçamento (R$)", "agua": "Água (m³)", "mao_obra": "MO (hh)"}
df_uso = pd.DataFrame([
    {
        "Recurso": labels_rec[k],
        "Utilizado": f"{br(v[0])}",
        "Disponível": f"{br(v[1])}",
        "Uso (%)": f"{v[0]/v[1]*100:.2f}%",
        "Folga": f"{br(v[1]-v[0])} {v[2]}",
    }
    for k, v in resultado["uso"].items()
])
st.dataframe(df_uso, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Downloads")
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("**Apresentação em Slides (PPTX)**")
    pptx_bytes = gerar_pptx(resultado)
    st.download_button(
        "Baixar Apresentação (.pptx)",
        data=pptx_bytes,
        file_name="AgroPrime_LP_Workshop.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
        type="primary",
    )

with col_d2:
    st.markdown("**Documento de Modelagem (.md)**")
    doc = f"""# Otimização do Mix de Culturas — Cooperativa AgroPrime

## Etapa I — Contextualização

A Cooperativa AgroPrime dispõe de 5.000 ha para a safra 2025/2026 e precisa decidir
a alocação ótima entre Soja, Milho, Algodão e Cana-de-Açúcar para maximizar o lucro.

## Etapa II — Modelagem Matemática

### Variáveis de Decisão
- x1 = ha de Soja
- x2 = ha de Milho
- x3 = ha de Algodão
- x4 = ha de Cana-de-Açúcar

### Função Objetivo
Maximizar Z = 3500·x1 + 2300·x2 + 4200·x3 + 3400·x4

### Restrições
1. Terra:       x1 + x2 + x3 + x4 ≤ 5.000
2. Orçamento:   4500x1 + 3200x2 + 6000x3 + 2800x4 ≤ 20.000.000
3. Água:        600x1 + 800x2 + 500x3 + 1500x4 ≤ 4.000.000
4. Mão de Obra: 12x1 + 15x2 + 22x3 + 8x4 ≤ 60.000
5. Demanda:     x1≤2500, x2≤2000, x3≤1500, x4≤1000
6. x1, x2, x3, x4 ≥ 0

## Etapa III — Solução (Python / PuLP)

### Resultado Ótimo
{chr(10).join(f"- {culturas[i]}: {br(qtds[i])} ha" for i in range(len(culturas)))}

### Lucro Total Ótimo
Z* = R$ {br(lucro)}

### Uso dos Recursos
{chr(10).join(f"- {labels_rec[k]}: {br(v[0])} / {br(v[1])} ({v[0]/v[1]*100:.2f}%)" for k, v in resultado['uso'].items())}
"""
    st.download_button(
        "Baixar Documento (.md)",
        data=doc.encode("utf-8"),
        file_name="AgroPrime_Modelagem_LP.md",
        mime="text/markdown",
        use_container_width=True,
    )
