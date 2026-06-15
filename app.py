import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from core.modelo import DEFAULT_PARAMS, DEFAULT_RECURSOS, CULTURAS

st.set_page_config(
    page_title="AgroPrime — Otimização LP",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🌱 AgroPrime LP")
st.sidebar.caption("MBA em Pesquisa Operacional")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Navegação**
- Contextualização (Etapa I)
- Modelagem Matemática (Etapa II)
- Solver Interativo (Etapa III)
- Resultados e Slides
""")

st.title("Otimização do Mix de Culturas")
st.caption("Cooperativa AgroPrime — Programação Linear Aplicada ao Agronegócio")
st.divider()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Área Disponível", "5.000 ha")
c2.metric("Orçamento", "R$ 20.000.000")
c3.metric("Água Disponível", "4.000.000 m³")
c4.metric("Mão de Obra", "60.000 hh")

st.divider()
st.subheader("Culturas analisadas")

col1, col2, col3, col4 = st.columns(4)
culturas_info = [
    ("Soja", "R$ 3.500/ha", "2.500 ha máx"),
    ("Milho", "R$ 2.300/ha", "2.000 ha máx"),
    ("Algodão", "R$ 4.200/ha", "1.500 ha máx"),
    ("Cana-de-Açúcar", "R$ 3.400/ha", "1.000 ha máx"),
]
for col, (nome, margem, demanda) in zip([col1, col2, col3, col4], culturas_info):
    with col:
        st.info(f"**{nome}**\nMargem: {margem}\nDemanda: {demanda}")
