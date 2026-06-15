import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from core.fmt import br
from core.modelo import resolver, CULTURAS, DEFAULT_PARAMS, DEFAULT_RECURSOS

st.set_page_config(page_title="Solver Interativo", page_icon="⚙️", layout="wide")
st.title("Etapa III — Solver Interativo")
st.caption("Ajuste os parâmetros e resolva o modelo de Programação Linear")
st.divider()

col_param, col_res = st.columns([1, 2])

with col_param:
    st.subheader("Parâmetros do Modelo")

    with st.expander("Margens Líquidas (R$/ha)", expanded=True):
        margens = [
            st.number_input(f"Margem {c}", value=float(DEFAULT_PARAMS["margem"][i]),
                           step=100.0, key=f"m{i}")
            for i, c in enumerate(CULTURAS)
        ]

    with st.expander("Custos de Insumos (R$/ha)"):
        custos = [
            st.number_input(f"Custo {c}", value=float(DEFAULT_PARAMS["custo"][i]),
                           step=100.0, key=f"c{i}")
            for i, c in enumerate(CULTURAS)
        ]

    with st.expander("Consumo de Água (m³/ha)"):
        agua = [
            st.number_input(f"Água {c}", value=float(DEFAULT_PARAMS["agua"][i]),
                           step=50.0, key=f"a{i}")
            for i, c in enumerate(CULTURAS)
        ]

    with st.expander("Mão de Obra (hh/ha)"):
        mo = [
            st.number_input(f"MO {c}", value=float(DEFAULT_PARAMS["mao_obra"][i]),
                           step=1.0, key=f"mo{i}")
            for i, c in enumerate(CULTURAS)
        ]

    with st.expander("Demanda Máxima (ha)"):
        demanda = [
            st.number_input(f"Dem. {c}", value=float(DEFAULT_PARAMS["demanda_max"][i]),
                           step=100.0, key=f"d{i}")
            for i, c in enumerate(CULTURAS)
        ]

    st.subheader("Recursos Disponíveis")
    terra    = st.number_input("Terra (ha)", value=float(DEFAULT_RECURSOS["terra"]), step=100.0)
    orcamento = st.number_input("Orçamento (R$)", value=float(DEFAULT_RECURSOS["orcamento"]), step=100000.0)
    agua_tot = st.number_input("Água (m³)", value=float(DEFAULT_RECURSOS["agua"]), step=100000.0)
    mo_tot   = st.number_input("Mão de Obra (hh)", value=float(DEFAULT_RECURSOS["mao_obra"]), step=1000.0)

    rodar = st.button("Resolver Modelo", type="primary", use_container_width=True)

with col_res:
    if rodar or "resultado_lp" not in st.session_state:
        params = {
            "margem":      margens,
            "custo":       custos,
            "agua":        agua,
            "mao_obra":    mo,
            "demanda_max": demanda,
        }
        recursos = {
            "terra":     terra,
            "orcamento": orcamento,
            "agua":      agua_tot,
            "mao_obra":  mo_tot,
        }
        with st.spinner("Resolvendo..."):
            resultado = resolver(params, recursos)
        st.session_state["resultado_lp"] = resultado

    resultado = st.session_state["resultado_lp"]
    status = resultado["status"]

    if status == "Optimal":
        st.success(f"Status: {status} — Solução ótima encontrada")
    else:
        st.error(f"Status: {status}")

    st.subheader("Solução Ótima")
    lucro = resultado["lucro_otimo"]
    st.metric("Lucro Total Máximo", f"R$ {br(lucro)}")

    import pandas as pd
    df = pd.DataFrame({
        "Cultura":   resultado["culturas"],
        "Hectares*": [f"{br(q)} ha" for q in resultado["quantidades"]],
        "Receita":   [f"R$ {br(r)}" for r in resultado["receita_por_cultura"]],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Uso dos Recursos")
    labels = {"terra": "Terra", "orcamento": "Orçamento", "agua": "Água", "mao_obra": "Mão de Obra"}
    for key, (usado, total, unit) in resultado["uso"].items():
        pct = usado / total * 100 if total else 0
        st.progress(min(1.0, pct / 100), text=f"{labels[key]}: {br(usado)} / {br(total)} {unit} ({pct:.2f}%)")
