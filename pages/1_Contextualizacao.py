import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st

st.set_page_config(page_title="Contextualização", page_icon="🌾", layout="wide")
st.title("Etapa I — Contextualização do Problema")
st.divider()

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("A Empresa")
    st.markdown("""
A **Cooperativa AgroPrime** é uma empresa **fictícia** criada para fins didáticos,
inspirada no perfil típico de cooperativas agrícolas do Centro-Oeste brasileiro
— região responsável por mais de 60% da produção de grãos do país.

Para a safra 2025/2026, a cooperativa dispõe de **5.000 hectares** de área cultivável
e precisa decidir o **mix ideal de culturas** a ser plantado.
""")

    st.subheader("O Problema de Decisão")
    st.markdown("""
A diretoria da cooperativa enfrenta a seguinte questão:

> *"Quantos hectares devemos dedicar a cada cultura — Soja, Milho, Algodão e
> Cana-de-Açúcar — para **maximizar o lucro total da safra**, respeitando
> nossas limitações de terra, orçamento, água e mão de obra?"*

Este é um problema clássico de **Mix de Produção** em Pesquisa Operacional,
resolvido com eficiência pela **Programação Linear (PL)**.
""")

    st.subheader("Objetivo")
    st.success("**Maximizar** o lucro total da safra (R$), definindo a alocação ótima de hectares entre as quatro culturas.")

with col2:
    st.subheader("Recursos Disponíveis")
    recursos = {
        "Terra":          ("5.000 ha",       "Área total cultivável da cooperativa"),
        "Orçamento":      ("R$ 20.000.000",  "Budget para insumos (sementes, fertilizantes, defensivos)"),
        "Água":           ("4.000.000 m³",   "Disponibilidade hídrica para irrigação"),
        "Mão de Obra":    ("60.000 hh",      "Horas-homem disponíveis na safra"),
    }
    for nome, (valor, desc) in recursos.items():
        with st.container(border=True):
            st.metric(nome, valor)
            st.caption(desc)

    st.subheader("Contexto de Mercado")
    st.markdown("""
| Cultura | Relevância |
|---|---|
| Soja | Maior commodity do agronegócio brasileiro |
| Milho | 2ª maior produção, forte demanda interna |
| Algodão | Maior margem, exportação aquecida |
| Cana | Base do etanol e açúcar, contratos estáveis |
""")
