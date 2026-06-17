import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from core.fmt import br
from core.modelo import resolver, CULTURAS, DEFAULT_PARAMS


def _gerar_pdf(qtds, receitas, lucro, cond_orig, cond_norm, p) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def titulo(txt):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(10, 80, 40)
        pdf.multi_cell(0, 8, txt)
        pdf.ln(2)

    def subtitulo(txt):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 100, 60)
        pdf.multi_cell(0, 7, txt)
        pdf.ln(1)

    def corpo(txt):
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, txt)
        pdf.ln(2)

    def linha():
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    # Capa
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(10, 80, 40)
    pdf.cell(0, 12, "Tutorial - Programacao Linear", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "MBA em Pesquisa Operacional - Prof. Gabriel Capela", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, "Cooperativa AgroPrime - Mix de Culturas", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    linha()

    # 1. O Problema
    titulo("1. O Problema")
    corpo(
        "A Cooperativa AgroPrime tem 5.000 hectares de terra para a safra 2025/2026 "
        "e precisa decidir quanto plantar de cada cultura para maximizar o lucro.\n\n"
        "Culturas: Soja, Milho, Algodao e Cana-de-Acucar.\n\n"
        "Recursos disponiveis: Terra 5.000 ha | Orcamento R$ 20.000.000 | "
        "Agua 4.000.000 m3 | Mao de Obra 60.000 hh"
    )
    linha()

    # 2. O que e PL
    titulo("2. O que e Programacao Linear?")
    corpo(
        "Programacao Linear (PL) e uma ferramenta matematica para tomar a melhor decisao "
        "possivel quando temos recursos limitados.\n\n"
        "O nome 'linear' significa que tudo e proporcional: 2 hectares de soja geram "
        "exatamente o dobro do lucro de 1 hectare.\n\n"
        "Tres componentes:\n"
        "  - Variaveis de decisao: o que o modelo vai calcular (hectares de cada cultura)\n"
        "  - Funcao objetivo: o que queremos maximizar (lucro total em R$)\n"
        "  - Restricoes: limites que nao podemos ultrapassar (terra, orcamento, agua, MO)"
    )
    linha()

    # 3. O modelo
    titulo("3. O Modelo Matematico")
    subtitulo("Funcao Objetivo")
    corpo("Maximizar Z = 3500*x1 + 2300*x2 + 4200*x3 + 3400*x4")
    subtitulo("Restricoes")
    corpo(
        "R1 Terra:      x1 + x2 + x3 + x4 <= 5.000 ha\n"
        "R2 Orcamento:  4500x1 + 3200x2 + 6000x3 + 2800x4 <= 20.000.000 R$\n"
        "R3 Agua:       600x1 + 800x2 + 500x3 + 1500x4 <= 4.000.000 m3\n"
        "R4 Mao Obra:   12x1 + 15x2 + 22x3 + 8x4 <= 60.000 hh\n"
        "R5 Demanda:    x1<=2500, x2<=2000, x3<=1500, x4<=1000\n"
        "R6:            x1, x2, x3, x4 >= 0"
    )
    linha()

    # 4. Normalizacao
    titulo("4. Por que Normalizar os Dados?")
    corpo(
        f"Os coeficientes variam de 1 a 20.000.000 - diferenca enorme de escala.\n\n"
        f"Numero de condicionamento original: {br(cond_orig, 0)} (muito alto)\n"
        f"Numero de condicionamento normalizado: {br(cond_norm)}\n"
        f"Melhora: {cond_orig/cond_norm:.0f}x\n\n"
        "Solucao: dividir orcamento por 1.000 (R$ -> R$ mil) e agua por 1.000 (m3 -> mil m3).\n"
        "As variaveis (hectares) nao mudam. O resultado e identico."
    )
    linha()

    # 5. Solucao
    titulo("5. A Solucao Encontrada")
    culturas_nomes = ["Soja", "Milho", "Algodao", "Cana-de-Acucar"]
    for i, c in enumerate(culturas_nomes):
        corpo(f"  {c}: {br(qtds[i])} ha  ->  R$ {br(receitas[i])}")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(10, 80, 40)
    pdf.cell(0, 8, f"Lucro Total Otimo: R$ {br(lucro)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    linha()

    # 5a. Por que nao so algodao
    titulo("5a. Por que nao plantar so Algodao?")
    corpo(
        "O Algodao tem a maior margem absoluta (R$ 4.200/ha), mas e o pior em eficiencia:\n\n"
        f"  Soja:           Margem/Custo={p['margem'][0]/p['custo'][0]:.2f}  "
        f"Margem/MO={p['margem'][0]/p['mao_obra'][0]:.0f}\n"
        f"  Milho:          Margem/Custo={p['margem'][1]/p['custo'][1]:.2f}  "
        f"Margem/MO={p['margem'][1]/p['mao_obra'][1]:.0f}\n"
        f"  Algodao:        Margem/Custo={p['margem'][2]/p['custo'][2]:.2f}  "
        f"Margem/MO={p['margem'][2]/p['mao_obra'][2]:.0f}\n"
        f"  Cana-de-Acucar: Margem/Custo={p['margem'][3]/p['custo'][3]:.2f}  "
        f"Margem/MO={p['margem'][3]/p['mao_obra'][3]:.0f}\n\n"
        "Quando orcamento e mao de obra sao os gargalos, o solver prefere culturas que "
        "rendem mais por recurso escasso. Por isso Cana e Soja dominam a alocacao."
    )
    linha()

    # 6. Restricoes ativas
    titulo("6. Restricoes Ativas - os Gargalos")
    corpo(
        "Uma restricao ativa e aquela em que o recurso foi totalmente consumido.\n\n"
        "GARGALOS (100% consumidos):\n"
        "  - Orcamento: mais credito rural = mais lucro\n"
        "  - Mao de Obra: mecanizacao liberaria capacidade\n\n"
        "COM FOLGA:\n"
        "  - Terra: ~90% utilizada (sobram ~482 ha)\n"
        "  - Agua: ~88% utilizada (sobram ~474.000 m3)\n\n"
        "O limite do lucro nao e a terra - e o orcamento e a mao de obra."
    )
    linha()

    # 7. Limitacoes
    titulo("7. Limitacoes do Modelo")
    corpo(
        "Sazonalidade ignorada:\n"
        "  - Soja e Milho: ciclo anual (~4 meses)\n"
        "  - Algodao: ciclo semianual (~6 meses)\n"
        "  - Cana-de-Acucar: ciclo plurianual (12 a 18 meses)\n\n"
        "O modelo trata todas as culturas como se competissem pelo mesmo hectare "
        "no mesmo periodo. Um modelo mais realista usaria LP multiperiodo.\n\n"
        "Outras simplificacoes:\n"
        "  - Precos de mercado fixos (na realidade variam com cambio e demanda)\n"
        "  - Terra considerada homogenea (aptidoes diferentes por cultura)\n"
        "  - Demanda maxima definida a priori\n"
        "  - Custos fixos nao incluidos"
    )
    linha()
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Tutorial gerado pelo app AgroPrime LP - MBA PO BSBr - Prof. Gabriel Capela", new_x="LMARGIN", new_y="NEXT", align="C")

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()

st.set_page_config(page_title="Tutorial — Entendendo o Exercício", page_icon="📚", layout="wide")
st.title("Tutorial — Entendendo o Exercício")
st.caption("Guia para quem está vendo Programação Linear pela primeira vez")

# ── Dados do exercício ──────────────────────────────────────────────────────
res = resolver()
qtds    = res["quantidades"]
receitas = res["receita_por_cultura"]
lucro   = res["lucro_otimo"]
p       = DEFAULT_PARAMS

A_orig = np.array([
    [1,    1,    1,    1   ],
    [4500, 3200, 6000, 2800],
    [600,  800,  500,  1500],
    [12,   15,   22,   8   ],
], dtype=float)
A_norm = np.array([
    [1,   1,   1,   1  ],
    [4.5, 3.2, 6.0, 2.8],
    [0.6, 0.8, 0.5, 1.5],
    [12,  15,  22,  8  ],
], dtype=float)
cond_orig = np.linalg.cond(A_orig)
cond_norm = np.linalg.cond(A_norm)

# ── Índice ──────────────────────────────────────────────────────────────────
with st.expander("O que você vai aprender neste tutorial", expanded=True):
    st.markdown("""
1. **O problema** — qual é a situação real e o que precisamos decidir
2. **Programação Linear** — o que é, em linguagem simples
3. **Como montar o modelo** — variáveis, função objetivo e restrições
4. **O que é normalização** — por que os números muito diferentes causam problema
5. **A solução** — o que o computador encontrou e o que isso significa
6. **Restrições ativas** — quais recursos são os gargalos
""")

st.divider()

# ── Download no topo ────────────────────────────────────────────────────────
tutorial_md = f"""# Tutorial — Entendendo o Exercício de Programação Linear
## MBA em Pesquisa Operacional e Tomada de Decisão — BSBr
### Prof. Gabriel Capela

---

## 1. O Problema

A Cooperativa AgroPrime tem 5.000 hectares de terra e precisa decidir
quanto plantar de cada cultura para ganhar o máximo possível.

As culturas disponíveis são: Soja, Milho, Algodão e Cana-de-Açúcar.

Cada cultura tem:
- Uma margem de lucro diferente (R$/ha)
- Um custo de insumos diferente (R$/ha)
- Um consumo de água diferente (m³/ha)
- Uma demanda de mão de obra diferente (horas/ha)

A pergunta é simples: **quanto plantar de cada cultura para maximizar o lucro?**

---

## 2. O que é Programação Linear?

Programação Linear é uma ferramenta matemática para tomar a **melhor decisão possível**
quando temos recursos limitados.

Exemplo do dia a dia: você tem R$ 100 e quer comprar frutas para maximizar vitaminas.
Cada fruta custa um valor diferente e tem uma quantidade diferente de vitaminas.
Programação Linear resolve esse tipo de problema automaticamente.

No nosso caso:
- Recursos limitados: terra, orçamento, água e mão de obra
- Decisão: quantos hectares de cada cultura plantar
- Objetivo: maximizar o lucro total

O nome "linear" significa que tudo é proporcional:
2 hectares de soja = 2x o lucro de 1 hectare de soja. Simples assim.

---

## 3. Como montamos o modelo

### Variáveis de decisão (o que o modelo vai calcular)
- x1 = hectares de Soja
- x2 = hectares de Milho
- x3 = hectares de Algodão
- x4 = hectares de Cana-de-Açúcar

### Função objetivo (o que queremos maximizar)
Maximizar Z = 3.500·x1 + 2.300·x2 + 4.200·x3 + 3.400·x4

Tradução: cada hectare de Soja gera R$ 3.500 de lucro, cada hectare de Milho gera R$ 2.300, etc.

### Restrições (os limites que não podemos ultrapassar)
1. Terra:       x1 + x2 + x3 + x4 ≤ 5.000 ha
2. Orçamento:   4.500x1 + 3.200x2 + 6.000x3 + 2.800x4 ≤ R$ 20.000.000
3. Água:        600x1 + 800x2 + 500x3 + 1.500x4 ≤ 4.000.000 m³
4. Mão de Obra: 12x1 + 15x2 + 22x3 + 8x4 ≤ 60.000 hh
5. Demanda:     x1≤2.500, x2≤2.000, x3≤1.500, x4≤1.000
6. Não negatividade: x1, x2, x3, x4 ≥ 0

---

## 4. Por que normalizar?

Olhe as restrições: temos valores entre 1 e 20.000.000.
Essa diferença enorme de escala causa problemas numéricos no computador.

Número de condicionamento original: {br(cond_orig, 0)}
Número de condicionamento normalizado: {br(cond_norm)}
Redução: {cond_orig/cond_norm:.0f}x melhor

A normalização é simples: mudamos as unidades.
- Orçamento: de R$ para R$ mil (dividimos por 1.000)
- Água: de m³ para mil m³ (dividimos por 1.000)

As variáveis (hectares) não mudam. O resultado é idêntico.

---

## 5. A solução encontrada

| Cultura         | Hectares      | Lucro                 |
|-----------------|---------------|-----------------------|
| Soja            | {br(qtds[0])} ha | R$ {br(receitas[0])} |
| Milho           | {br(qtds[1])} ha | R$ {br(receitas[1])} |
| Algodão         | {br(qtds[2])} ha | R$ {br(receitas[2])} |
| Cana-de-Açúcar  | {br(qtds[3])} ha | R$ {br(receitas[3])} |
| **TOTAL**       | **{br(sum(qtds))} ha** | **R$ {br(lucro)}** |

Lucro Total Ótimo: R$ {br(lucro)}

Por que esse resultado?
- Soja e Cana chegaram ao máximo permitido pela demanda (2.500 e 1.000 ha)
- Algodão ficou limitado pelo custo alto (R$ 6.000/ha) e uso intenso de mão de obra (22 hh/ha)
- Milho ficou com o que sobrou — menor margem (R$ 2.300/ha)

---

## 5a. Por que não plantar só Algodão?

| Cultura        | Margem R$/ha | Custo R$/ha | MO hh/ha | Margem/Custo | Margem/MO |
|----------------|-------------|------------|---------|-------------|---------|
| Soja           | 3.500       | 4.500      | 12      | 0,78        | 291     |
| Milho          | 2.300       | 3.200      | 15      | 0,72        | 153     |
| Algodão        | 4.200       | 6.000      | 22      | 0,70        | 191     |
| Cana-de-Açúcar | 3.400       | 2.800      | 8       | 1,21        | 425     |

O Algodão tem a maior margem absoluta (R$ 4.200/ha), mas é o pior em Margem/Custo (0,70)
e pior em Margem/MO (191) entre as culturas relevantes.

Quando orçamento e mão de obra são os gargalos, o solver prefere culturas que
rendem mais por recurso escasso — não as que rendem mais por hectare.

Por isso: Cana vai primeiro (melhor ratio), depois Soja, depois Algodão com o que sobrou.
Milho fica com apenas 56 ha porque perde para todas as outras no critério de eficiência.

---

## 6. Restrições ativas — os gargalos

Uma restrição é "ativa" quando o recurso foi totalmente consumido.
Isso significa que esse recurso é um gargalo: se tivéssemos mais dele, o lucro aumentaria.

GARGALOS (restrições ativas):
- Orçamento: 100% utilizado — mais crédito rural = mais lucro
- Mão de Obra: 100% utilizada — mecanização liberaria capacidade

COM FOLGA (restrições inativas):
- Terra: ~90% utilizada — sobram ~482 ha que não puderam ser plantados por falta de orçamento/MO
- Água: ~88% utilizada — sobram ~474.000 m³ disponíveis

Conclusão: o limite do lucro não é a terra — é o orçamento e a mão de obra.

---

## 7. Limitações do modelo

**Sazonalidade ignorada**

As culturas têm ciclos de produção muito diferentes:
- Soja e Milho: ciclo anual (~4 meses)
- Algodão: ciclo semianual (~6 meses)
- Cana-de-Açúcar: ciclo plurianual (12 a 18 meses, com socas nos anos seguintes)

O modelo trata todas como se competissem pelo mesmo hectare no mesmo período.
Na prática, 1 ha de Cana ocupa a terra por 18 meses, impedindo rotação nesse intervalo.
Um modelo mais realista usaria LP multiperiodo ou programação inteira com ciclos.

**Outras simplificações:**
- Preços de mercado fixos (na realidade variam com câmbio e demanda global)
- Terra considerada homogênea (na prática cada área tem aptidão diferente por cultura)
- Demanda máxima definida a priori (depende de contratos e capacidade de armazenamento)
- Custos fixos não incluídos (apenas custos variáveis por hectare)

---

*Tutorial gerado pelo app AgroPrime LP — MBA PO BSBr — Prof. Gabriel Capela*
"""

pdf_bytes = _gerar_pdf(qtds, receitas, lucro, cond_orig, cond_norm, p)
col_md, col_pdf, _ = st.columns([1, 1, 2])
with col_md:
    st.download_button(
        "Baixar Tutorial (.md)",
        data=tutorial_md.encode("utf-8"),
        file_name="Tutorial_LP_AgroPrime.md",
        mime="text/markdown",
        use_container_width=True,
    )
with col_pdf:
    st.download_button(
        "Baixar Tutorial (.pdf)",
        data=pdf_bytes,
        file_name="Tutorial_LP_AgroPrime.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary",
    )

st.divider()

# ── 1. O Problema ───────────────────────────────────────────────────────────
st.header("1. O Problema")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
A **Cooperativa AgroPrime** tem **5.000 hectares** de terra disponíveis para a safra 2025/2026.

Ela pode plantar quatro culturas: **Soja, Milho, Algodão e Cana-de-Açúcar**.

Cada cultura tem lucratividade diferente — mas também consome recursos diferentes
(dinheiro, água e mão de obra). A cooperativa não tem recursos ilimitados.

**A pergunta é:** *quanto plantar de cada cultura para ganhar o máximo possível?*

Essa é exatamente a pergunta que a Programação Linear responde.
""")
with col2:
    st.info("""
**Recursos disponíveis:**

- Terra: 5.000 ha
- Orçamento: R$ 20.000.000
- Água: 4.000.000 m³
- Mão de Obra: 60.000 hh
""")

st.divider()

# ── 2. O que é PL ───────────────────────────────────────────────────────────
st.header("2. O que é Programação Linear?")

st.markdown("""
Imagine que você tem R$ 100 para comprar frutas. Laranja custa R$ 2 e tem 50mg de vitamina C.
Limão custa R$ 1 e tem 30mg. Você quer o máximo de vitamina C.

**Qual a combinação ideal de laranjas e limões?**

Isso é um problema de Programação Linear. O computador resolve em milissegundos.

No caso da cooperativa:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.success("""
**Variáveis**
O que decidimos:
- Hectares de cada cultura
""")
with col2:
    st.success("""
**Objetivo**
O que maximizamos:
- Lucro total (R$)
""")
with col3:
    st.success("""
**Restrições**
Limites que não podemos ultrapassar:
- Terra, orçamento, água, MO
""")

st.markdown("""
O nome "linear" significa que tudo é **proporcional**:
2 hectares de soja gera exatamente o dobro do lucro de 1 hectare.
Sem curvas, sem fórmulas complicadas.
""")

st.divider()

# ── 3. O modelo ─────────────────────────────────────────────────────────────
st.header("3. Como montamos o modelo")

tab1, tab2, tab3 = st.tabs(["Variáveis", "Função Objetivo", "Restrições"])

with tab1:
    st.markdown("""
As variáveis são as **incógnitas** — os valores que o modelo vai calcular.

Cada variável representa uma decisão quantificável:
""")
    for i, (c, m) in enumerate(zip(CULTURAS, res["params"]["margem"])):
        st.markdown(f"- **x{i+1}** = hectares de {c} → R$ {br(m, 0)}/ha de margem")

    st.info("O solver vai encontrar os valores exatos de x1, x2, x3 e x4 que maximizam o lucro.")

with tab2:
    st.markdown("A função objetivo é a **fórmula do lucro** que queremos maximizar:")
    st.latex(r"\text{Maximizar } Z = 3500x_1 + 2300x_2 + 4200x_3 + 3400x_4")
    st.markdown("""
Cada coeficiente é a margem líquida por hectare:
- 3.500 = lucro por ha de Soja
- 4.200 = lucro por ha de Algodão (maior margem!)
- 2.300 = lucro por ha de Milho (menor margem)
""")

with tab3:
    st.markdown("As restrições são os **limites** que a cooperativa não pode ultrapassar:")
    st.latex(r"x_1 + x_2 + x_3 + x_4 \leq 5000 \quad \text{(terra, ha)}")
    st.latex(r"4500x_1 + 3200x_2 + 6000x_3 + 2800x_4 \leq 20{,}000{,}000 \quad \text{(orçamento, R\$)}")
    st.latex(r"600x_1 + 800x_2 + 500x_3 + 1500x_4 \leq 4{,}000{,}000 \quad \text{(água, m³)}")
    st.latex(r"12x_1 + 15x_2 + 22x_3 + 8x_4 \leq 60{,}000 \quad \text{(mão de obra, hh)}")
    st.markdown("**Demanda máxima:** x1≤2.500, x2≤2.000, x3≤1.500, x4≤1.000")
    st.markdown("**Não negatividade:** x1, x2, x3, x4 ≥ 0 (não plantamos hectares negativos)")

st.divider()

# ── 4. Normalização ─────────────────────────────────────────────────────────
st.header("4. Por que normalizar os dados?")

st.markdown("""
Olhe a diferença de escala nos coeficientes:
- Mão de obra: coeficiente **8** (Cana)
- Orçamento: coeficiente **6.000** (Algodão)

E nos recursos disponíveis:
- Terra: **5.000** ha
- Orçamento: **20.000.000** R$

Essa diferença de escala (de 1 a 20 milhões) causa **instabilidade numérica** no solver.
Medimos isso com o número de condicionamento da matriz:
""")

col1, col2, col3 = st.columns(3)
col1.metric("Cond. Original", f"{br(cond_orig, 0)}", help="Acima de 1.000 é problemático")
col2.metric("Cond. Normalizado", f"{br(cond_norm, 1)}", help="Muito melhor!")
col3.metric("Melhora", f"{cond_orig/cond_norm:.0f}x", delta=f"-{(1-cond_norm/cond_orig)*100:.0f}%")

st.warning(f"""
**Número de condicionamento original: {br(cond_orig, 0)}** — muito alto.

Quanto maior esse número, mais impreciso fica o cálculo numérico do computador.
Normalizar os dados reduz esse número para {br(cond_norm, 1)} — {cond_orig/cond_norm:.0f}x melhor.
""")

st.markdown("""
### Como normalizar? Mudança de unidades

Simplesmente dividimos os coeficientes por 1.000 nas linhas de orçamento e água:
- Orçamento: de **R$** para **R$ mil** (dividir por 1.000)
- Água: de **m³** para **mil m³** (dividir por 1.000)

As variáveis (hectares) **não mudam**. O resultado é exatamente o mesmo.
""")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Modelo Original")
    st.latex(r"4500x_1 + \ldots \leq 20{,}000{,}000")
    st.caption("Coeficientes: 4.500 a 6.000 | RHS: 20.000.000")

with col2:
    st.subheader("Modelo Normalizado")
    st.latex(r"4{,}5x_1 + \ldots \leq 20{,}000")
    st.caption("Coeficientes: 4,5 a 6,0 | RHS: 20.000")

st.success("O resultado (hectares e lucro) é idêntico nos dois modelos. Só a escala muda.")

st.divider()

# ── 5. A solução ─────────────────────────────────────────────────────────────
st.header("5. A solução encontrada pelo solver")

st.markdown("""
Depois de rodar o algoritmo Simplex (via PuLP/CBC), a solução ótima foi:
""")

col1, col2, col3, col4 = st.columns(4)
for col, c, q, r in zip([col1, col2, col3, col4], CULTURAS, qtds, receitas):
    col.metric(c, f"{br(q)} ha", f"R$ {br(r)}")

st.metric("Lucro Total Ótimo", f"R$ {br(lucro)}")

st.markdown(f"""
### Por que o modelo escolheu esse mix?

1. **Soja (x1 = {br(qtds[0])} ha):** Atingiu o limite máximo de demanda (2.500 ha).
   Bom equilíbrio entre margem (R$ 3.500/ha), custo (R$ 4.500/ha) e mão de obra (12 hh/ha).

2. **Algodão (x3 = {br(qtds[2])} ha):** Maior margem (R$ 4.200/ha), mas também o mais caro
   (R$ 6.000/ha) e mais intensivo em mão de obra (22 hh/ha). Ficou limitado pelos gargalos.

3. **Cana (x4 = {br(qtds[3])} ha):** Atingiu o limite máximo (1.000 ha).
   Menor custo de MO (8 hh/ha) e insumos (R$ 2.800/ha) — excelente para usar o que sobrou.

4. **Milho (x2 = {br(qtds[1])} ha):** Menor margem (R$ 2.300/ha). Ficou com a sobra
   dos recursos após alocar os demais.
""")

st.success(f"""
**R$ {br(lucro)} é o máximo possível.**

Qualquer outra combinação de hectares geraria um lucro igual ou menor.
""")

# ── Por que não plantar só Algodão? ─────────────────────────────────────────
st.subheader("Por que não plantar só Algodão, se ele tem a maior margem?")

p = DEFAULT_PARAMS
df_comp = pd.DataFrame({
    "Cultura":          CULTURAS,
    "Margem (R$/ha)":   p["margem"],
    "Custo (R$/ha)":    p["custo"],
    "MO (hh/ha)":       p["mao_obra"],
    "Demanda máx. (ha)":p["demanda_max"],
    "Margem/Custo":     [round(p["margem"][i] / p["custo"][i], 2) for i in range(4)],
    "Margem/MO":        [round(p["margem"][i] / p["mao_obra"][i], 2) for i in range(4)],
})
st.dataframe(df_comp, use_container_width=True, hide_index=True)

st.markdown("""
Olhe as duas últimas colunas:

- **Margem/Custo** — quanto de lucro você ganha por real investido
- **Margem/MO** — quanto de lucro você ganha por hora de mão de obra

O **Algodão** tem a maior margem bruta (R$ 4.200/ha), mas:
- Custa **R$ 6.000/ha** — o mais caro de todos
- Exige **22 hh/ha** de mão de obra — o mais intensivo

Com orçamento e MO limitados, cada hectare de Algodão "consome" recursos que poderiam
ir para outras culturas com melhor retorno sobre o recurso escasso.

A **Soja** tem Margem/MO de 291 — muito melhor que o Algodão (191).
Isso significa que, quando a mão de obra é o gargalo, a Soja rende mais por hora trabalhada.

A **Cana** tem o melhor Margem/Custo (1,21) e o melhor Margem/MO (425).
Por isso o solver aloca Cana até o limite de demanda (1.000 ha) antes de tudo.

O **Milho** tem a pior margem absoluta (R$ 2.300/ha) e não se destaca em nenhum ratio.
Por isso fica apenas com o "resto" dos recursos — 56 ha.

> Em resumo: o solver não olha só a margem. Ele considera qual cultura rende mais
> **dado o recurso que está faltando**. Quando orçamento e MO são os gargalos,
> Soja e Cana ganham do Algodão.
""")

st.divider()

# ── 6. Restrições ativas ─────────────────────────────────────────────────────
st.header("6. Restrições ativas — os gargalos da operação")

st.markdown("""
Uma **restrição ativa** é aquela em que o recurso foi **totalmente consumido** — sem sobra.

Isso é importante porque revela onde estão os **gargalos**:
se a cooperativa conseguir mais desse recurso, o lucro aumenta.
Se não conseguir, o recurso limita o crescimento.
""")

uso = res["uso"]
labels_rec = {"terra": "Terra", "orcamento": "Orçamento", "agua": "Água", "mao_obra": "Mão de Obra"}
unidades = {"terra": "ha", "orcamento": "R$", "agua": "m³", "mao_obra": "hh"}

for key, (usado, total, unit) in uso.items():
    pct = usado / total * 100
    ativo = pct >= 99.9
    label = f"{'🔴 GARGALO' if ativo else '🟢 Com folga'} — {labels_rec[key]}: {br(usado)} / {br(total)} {unit} ({pct:.1f}%)"
    st.progress(min(1.0, pct / 100), text=label)

col1, col2 = st.columns(2)
with col1:
    st.error("""
**Gargalos (100% consumidos):**
- Orçamento — mais crédito rural = mais lucro
- Mão de Obra — mecanização liberaria capacidade
""")
with col2:
    st.success("""
**Com folga:**
- Terra — sobram ~482 ha não plantados
- Água — sobram ~474.000 m³

Esses recursos não limitam o lucro atual.
""")

st.info("""
**O preço-sombra** (dual value) de uma restrição ativa diz exatamente quanto o lucro aumenta
se você tiver mais 1 unidade desse recurso.
Por exemplo: quanto a mais de lucro se o banco liberar R$ 1.000 a mais de crédito?
Essa é a **análise de sensibilidade** — o próximo passo após resolver o modelo.
""")

st.divider()

# ── Exercício Resolvido ──────────────────────────────────────────────────────
st.header("Exercício Resolvido")
st.caption("Método gráfico + cálculo completo passo a passo")

# ── Gráficos de resultado ─────────────────────────────────────────────────────
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Alocação Ótima de Hectares")
    fig_bar, ax_bar = plt.subplots(figsize=(6, 4), facecolor="#0A1A0D")
    ax_bar.set_facecolor("#1A2E1D")
    colors_bar = ["#52B788", "#95D5B2", "#2D6A4F", "#F4D03F"]
    bars = ax_bar.bar(CULTURAS, qtds, color=colors_bar, edgecolor="#0A1A0D", linewidth=0.5)
    for bar, q in zip(bars, qtds):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                    f"{br(q)}", ha="center", va="bottom", color="white", fontsize=10)
    ax_bar.set_ylabel("Hectares", color="white")
    ax_bar.tick_params(colors="white", labelsize=9)
    ax_bar.set_title("Hectares por Cultura", color="white", fontsize=12)
    for sp in ax_bar.spines.values():
        sp.set_edgecolor("#2D6A4F")
    plt.tight_layout()
    st.pyplot(fig_bar)
    plt.close(fig_bar)

with col_g2:
    st.subheader("Participação na Receita")
    fig_pie, ax_pie = plt.subplots(figsize=(6, 4), facecolor="#0A1A0D")
    wedges, texts, autotexts = ax_pie.pie(
        receitas, labels=CULTURAS, autopct="%1.1f%%",
        colors=["#52B788", "#95D5B2", "#2D6A4F", "#F4D03F"],
        textprops={"color": "white", "fontsize": 10},
        pctdistance=0.75, wedgeprops={"edgecolor": "#0A1A0D", "linewidth": 1.5}
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontsize(9)
    ax_pie.set_facecolor("#0A1A0D")
    ax_pie.set_title("Participação na Receita Total", color="white", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig_pie)
    plt.close(fig_pie)

# ── Gráfico cartesiano ───────────────────────────────────────────────────────
st.subheader("Método Gráfico — Região Viável e Ponto Ótimo")
st.markdown("""
Para visualizar o problema em 2D, fixamos **Milho** e **Cana** nos valores ótimos
e plotamos apenas **Soja (x₁) × Algodão (x₃)**.
As restrições são ajustadas descontando o consumo já alocado.
""")

x2_fix, x4_fix = qtds[1], qtds[3]
terra_adj = 5000        - x2_fix       - x4_fix
orc_adj   = 20_000_000  - 3200*x2_fix  - 2800*x4_fix
mo_adj    = 60_000      - 15*x2_fix    - 8*x4_fix
dem1, dem3 = 2500.0, 1500.0

x_max, y_max = 2700.0, 1600.0
xv = np.linspace(0, x_max, 1000)

fig_g, ax_g = plt.subplots(figsize=(9, 5.5), facecolor="#0A1A0D")
ax_g.set_facecolor("#0F1F12")

ax_g.plot(xv, terra_adj - xv,             color="#52B788", lw=2,   label="Terra")
ax_g.plot(xv, (orc_adj - 4500*xv)/6000,   color="#F4D03F", lw=2.5, label="Orçamento ★ gargalo")
ax_g.plot(xv, (mo_adj - 12*xv)/22,        color="#E74C3C", lw=2.5, label="Mão de Obra ★ gargalo")
ax_g.axvline(dem1, color="#95D5B2", lw=1.8, ls="--", label=f"Dem. Soja ≤ {br(dem1, 0)} ha")
ax_g.axhline(dem3, color="#AED6F1", lw=1.8, ls="--", label=f"Dem. Algodão ≤ {br(dem3, 0)} ha")

xs = np.linspace(0, x_max, 3000)
y_up = np.minimum(np.minimum(terra_adj - xs, (orc_adj - 4500*xs)/6000),
                  np.minimum((mo_adj - 12*xs)/22, dem3))
y_up = np.clip(y_up, 0, y_max)
ax_g.fill_between(xs[xs <= dem1], 0, y_up[xs <= dem1],
                  alpha=0.20, color="#52B788", label="Região viável")

Z_opt = 3500*qtds[0] + 4200*qtds[2]
for frac in [0.5, 0.75, 1.0]:
    Z = Z_opt * frac
    ax_g.plot(xv, (Z - 3500*xv)/4200,
              color="#BDC3C7", lw=2.0 if frac == 1.0 else 0.8,
              ls="-" if frac == 1.0 else ":",
              alpha=0.9 if frac == 1.0 else 0.5,
              label=f"Isolucro R$ {br(Z/1e6, 1)}M" if frac == 1.0 else None)

eps = 0.5
verts_g = []
try:
    pv = np.linalg.solve([[4500,6000],[12,22]], [orc_adj, mo_adj])
    if -eps<=pv[0]<=dem1+eps and -eps<=pv[1]<=dem3+eps:
        verts_g.append((pv[0], pv[1]))
except Exception:
    pass
x3_d1 = (mo_adj - 12*dem1)/22
if -eps<=x3_d1<=dem3+eps:
    verts_g.append((dem1, x3_d1))
x1_d3 = (mo_adj - 22*dem3)/12
if -eps<=x1_d3<=dem1+eps:
    verts_g.append((x1_d3, dem3))

seen = set()
for vx, vy in verts_g:
    key = (round(vx), round(vy))
    if key not in seen:
        seen.add(key)
        ax_g.scatter(vx, vy, color="white", s=60, zorder=5, edgecolors="#AAAAAA", lw=0.8)

ax_g.scatter(qtds[0], qtds[2], color="#F4D03F", s=260, zorder=10, marker="*",
             label=f"★ Ótimo ({br(qtds[0], 0)}, {br(qtds[2], 0)})")
ax_g.annotate(
    f"★ ({br(qtds[0], 0)}, {br(qtds[2], 0)})",
    xy=(qtds[0], qtds[2]),
    xytext=(qtds[0] - 600, qtds[2] - 280),
    color="#F4D03F", fontsize=9, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#0A1A0D", edgecolor="#F4D03F", alpha=0.9),
    arrowprops=dict(arrowstyle="->", color="#F4D03F", lw=1.5),
)

ax_g.set_xlim(0, x_max)
ax_g.set_ylim(0, y_max)
ax_g.set_xlabel("x₁ — Soja (ha)", color="white", fontsize=11)
ax_g.set_ylabel("x₃ — Algodão (ha)", color="white", fontsize=11)
ax_g.set_title("Região Viável e Ponto Ótimo (projeção 2D)", color="white", fontsize=12, fontweight="bold")
ax_g.tick_params(colors="white", labelsize=9)
for sp in ax_g.spines.values():
    sp.set_edgecolor("#2D6A4F")
handles_g, labels_g = ax_g.get_legend_handles_labels()
fig_g.legend(handles_g, labels_g, loc="lower center", bbox_to_anchor=(0.5, 0.01),
             ncols=4, fontsize=8, facecolor="#1A2E1D", labelcolor="white", edgecolor="#2D6A4F")
fig_g.subplots_adjust(bottom=0.20, top=0.95)
st.pyplot(fig_g)
plt.close(fig_g)

st.caption("Retas amarela (Orçamento) e vermelha (MO) passam pelo ponto ótimo — confirmam os gargalos.")

# ── Cálculos passo a passo ───────────────────────────────────────────────────
st.subheader("Cálculos — Passo a Passo")

st.markdown("**Passo 1 — Solução encontrada pelo solver (CBC/Simplex):**")
col1, col2, col3, col4 = st.columns(4)
for col, c, q in zip([col1,col2,col3,col4], CULTURAS, qtds):
    col.metric(c, f"{br(q)} ha")

st.markdown("**Passo 2 — Substituição na Função Objetivo:**")
st.code(f"""
Z* = 3.500 × x₁  +  2.300 × x₂  +  4.200 × x₃  +  3.400 × x₄

Z* = 3.500 × {br(qtds[0], 4)}  +  2.300 × {br(qtds[1], 4)}  +  4.200 × {br(qtds[2], 4)}  +  3.400 × {br(qtds[3], 4)}

Z* = {br(receitas[0])}  +  {br(receitas[1])}  +  {br(receitas[2])}  +  {br(receitas[3])}

Z* = R$ {br(lucro)}  ← LUCRO MÁXIMO
""", language=None)

st.markdown("**Passo 3 — Verificação das restrições:**")
uso = res["uso"]
r_terra    = sum(qtds)
r_orc      = sum(p["custo"][i]*qtds[i] for i in range(4))
r_agua     = sum(p["agua"][i]*qtds[i] for i in range(4))
r_mo       = sum(p["mao_obra"][i]*qtds[i] for i in range(4))

st.code(f"""
R1 Terra:      {br(qtds[0], 4)} + {br(qtds[1], 4)} + {br(qtds[2], 4)} + {br(qtds[3], 4)} = {br(r_terra)} ha  ≤  5.000,00 ha  ✓  (folga: {br(5000-r_terra)} ha)

R2 Orçamento:  4.500×{br(qtds[0], 4)} + 3.200×{br(qtds[1], 4)} + 6.000×{br(qtds[2], 4)} + 2.800×{br(qtds[3], 4)}
             = R$ {br(r_orc)}  ≤  R$ 20.000.000,00  ✓  ★ ATIVA (folga zero)

R3 Água:       600×{br(qtds[0], 4)} + 800×{br(qtds[1], 4)} + 500×{br(qtds[2], 4)} + 1.500×{br(qtds[3], 4)}
             = {br(r_agua)} m³  ≤  4.000.000,00 m³  ✓  (folga: {br(4_000_000-r_agua)} m³)

R4 Mão de Obra: 12×{br(qtds[0], 4)} + 15×{br(qtds[1], 4)} + 22×{br(qtds[2], 4)} + 8×{br(qtds[3], 4)}
              = {br(r_mo)} hh  ≤  60.000,00 hh  ✓  ★ ATIVA (folga zero)

R5 Demanda:    x₁={br(qtds[0], 4)}≤2.500  x₂={br(qtds[1], 4)}≤2.000  x₃={br(qtds[2], 4)}≤1.500  x₄={br(qtds[3], 4)}≤1.000  ✓
""", language=None)

st.success(f"""
**Resposta final: Z\\* = R$ {br(lucro)}**

As restrições ativas (★) são Orçamento e Mão de Obra — os gargalos da operação.
Ampliar qualquer um desses recursos permitiria aumentar o lucro além de R$ {br(lucro)}.
""")

st.divider()

# ── 7. Resolução Manual — Passo a Passo ─────────────────────────────────────
st.header("7. Resolução Manual — Passo a Passo")

st.markdown("""
Em PL, a solução ótima **sempre ocorre em um vértice** da região viável — onde um conjunto de
restrições está ativo (folga zero) simultaneamente. Com 4 variáveis precisamos de 4 restrições
ativas para identificar o vértice ótimo.
""")

st.subheader("Passo 1 — Identificar restrições ativas")

st.markdown("""
Analise o uso de cada recurso na solução ótima (obtida pelo solver):
""")

uso = res["uso"]
labels_uso = {"terra": "Terra", "orcamento": "Orçamento", "agua": "Água", "mao_obra": "Mão de Obra"}
unids_uso  = {"terra": "ha", "orcamento": "R$", "agua": "m³", "mao_obra": "hh"}
for key, (usado, total, unit) in uso.items():
    pct   = usado / total * 100
    ativo = pct >= 99.9
    icone = "**ATIVA** (folga zero)" if ativo else f"com folga ({br(total - usado)} {unit} sobrando)"
    st.markdown(f"- **{labels_uso[key]}**: {br(usado)} / {br(total)} {unit} → {icone}")

st.info("""
**Restrições ativas identificadas:**
- R2 — Orçamento (100% consumido)
- R4 — Mão de Obra (100% consumida)
- R5 — Demanda Soja: x₁ = 2.500 ha (no limite)
- R5 — Demanda Cana: x₄ = 1.000 ha (no limite)
""")

st.subheader("Passo 2 — Fixar variáveis nos limites de demanda")

st.markdown("""
Soja e Cana atingiram seus limites máximos de demanda → **valores fixados**:
x₁ = 2.500 ha · x₄ = 1.000 ha

Substituindo nas restrições ativas para obter sistema 2×2:
""")

st.latex(r"""
\text{R2 (Orçamento):} \quad
4.500(2.500) + 3.200\,x_2 + 6.000\,x_3 + 2.800(1.000) = 20.000.000
""")
st.latex(r"""
\boxed{3.200\,x_2 + 6.000\,x_3 = 5.950.000} \quad \text{...(I)}
""")
st.latex(r"""
\text{R4 (Mão de Obra):} \quad
12(2.500) + 15\,x_2 + 22\,x_3 + 8(1.000) = 60.000
""")
st.latex(r"""
\boxed{15\,x_2 + 22\,x_3 = 22.000} \quad \text{...(II)}
""")

st.subheader("Passo 3 — Resolver o sistema 2×2 por substituição")

st.markdown("**Isolar x₂ em (II) e substituir em (I):**")

st.latex(r"""
x_2 = \frac{22.000 - 22\,x_3}{15} \quad \text{...(III)}
""")
st.latex(r"""
3.200 \cdot \frac{22.000 - 22\,x_3}{15} + 6.000\,x_3 = 5.950.000
""")
st.latex(r"""
4.693.333{,}33 - 4.693{,}33\,x_3 + 6.000\,x_3 = 5.950.000
\quad \Rightarrow \quad 1.306{,}67\,x_3 = 1.256.666{,}67
""")
st.latex(r"""
\boxed{x_3 \approx 961{,}73 \text{ ha (Algodão)}}
\qquad
\boxed{x_2 \approx 56{,}12 \text{ ha (Milho)}}
""")

st.subheader("Passo 4 — Calcular Z*")

x1r, x2r, x3r, x4r = 2500, 56.12, 961.73, 1000
p1m = 3500 * x1r; p2m = 2300 * x2r; p3m = 4200 * x3r; p4m = 3400 * x4r
z_manual = p1m + p2m + p3m + p4m

st.code(f"""
Z* = 3.500 × {br(x1r, 4)}  +  2.300 × {br(x2r, 4)}  +  4.200 × {br(x3r, 4)}  +  3.400 × {br(x4r, 4)}
Z* = {br(p1m, 0)}  +  {br(p2m, 0)}  +  {br(p3m, 0)}  +  {br(p4m, 0)}
Z* ≈ R$ {br(z_manual, 0)}
""", language=None)

st.success(f"""
**Z\\* ≈ R$ {br(z_manual, 0)}** — equivalente ao ótimo do solver (diferença de R$ {br(lucro - z_manual, 0)} por arredondamento nos valores intermediários de x₂ e x₃).

A solução completa é: x₁ = 2.500 ha (Soja) | x₂ ≈ 56,12 ha (Milho) | x₃ ≈ 961,73 ha (Algodão) | x₄ = 1.000 ha (Cana)
""")

st.subheader("Passo 5 — Verificar as demais restrições")

st.markdown("Confirmar que a solução encontrada **respeita todas as restrições**:")

r_terra_m = x1r + x2r + x3r + x4r
r_agua_m  = 600*x1r + 800*x2r + 500*x3r + 1500*x4r

st.code(f"""
R1 Terra:      {br(x1r, 4)} + {br(x2r, 4)} + {br(x3r, 4)} + {br(x4r, 4)} = {br(r_terra_m)} ha  ≤  5.000,00 ha  ✓

R2 Orçamento:  4.500×{br(x1r, 0)} + 3.200×{br(x2r, 4)} + 6.000×{br(x3r, 4)} + 2.800×{br(x4r, 0)}
             ≈ R$ 20.000.000,00  ≤  R$ 20.000.000,00  ✓  ★ ATIVA

R3 Água:       600×{br(x1r, 0)} + 800×{br(x2r, 4)} + 500×{br(x3r, 4)} + 1.500×{br(x4r, 0)}
             ≈ {br(r_agua_m, 0)} m³  ≤  4.000.000,00 m³  ✓

R4 Mão de Obra: 12×{br(x1r, 0)} + 15×{br(x2r, 4)} + 22×{br(x3r, 4)} + 8×{br(x4r, 0)}
              ≈ 60.000,00 hh  ≤  60.000,00 hh  ✓  ★ ATIVA

R5 Demanda:    x₁={br(x1r, 0)}≤2.500  x₂={br(x2r, 4)}≤2.000  x₃={br(x3r, 4)}≤1.500  x₄={br(x4r, 0)}≤1.000  ✓
""", language=None)

st.divider()

# ── 8. Limitações do modelo ──────────────────────────────────────────────────
st.header("8. Limitações do modelo")

st.markdown("""
Todo modelo matemático é uma **simplificação da realidade**. Este modelo de LP assume condições
que nem sempre se verificam na prática. Conhecer as limitações é tão importante quanto
saber interpretar o resultado.
""")

st.warning("""
**Sazonalidade ignorada**

As quatro culturas têm ciclos de produção completamente diferentes:
- **Soja e Milho:** ciclo anual (~4 meses de plantio, colheita em 1 safra)
- **Algodão:** ciclo semianual (~6 meses)
- **Cana-de-Açúcar:** ciclo plurianual (12 a 18 meses, com socas nos anos seguintes)

O modelo trata todas como se competissem pelo mesmo hectare no mesmo período.
Na prática, 1 ha de Cana ocupa a terra por 18 meses — impedindo rotação nesse intervalo.
Um modelo mais realista usaria **LP multiperiodo** (múltiplas safras) ou
**programação inteira** com variáveis binárias de ciclo.
""")

with st.expander("Outras limitações do modelo"):
    st.markdown("""
**Preços de mercado fixos**

O modelo assume margens constantes (ex.: Soja = R$ 3.500/ha).
Na realidade, os preços das commodities variam com câmbio, clima e demanda global.
Uma extensão seria usar **programação estocástica** com cenários de preço.

**Recursos considerados homogêneos**

O modelo não distingue qual parte da terra é mais fértil para cada cultura,
nem qual mão de obra é especializada em qual operação.
Em realidade, 5.000 ha pode ter solos com aptidões diferentes.

**Demanda máxima como dado fixo**

Os limites de demanda (ex.: Soja ≤ 2.500 ha) foram definidos a priori.
Na prática, a demanda depende de contratos firmados, capacidade de armazenamento e logística.

**Ausência de custos fixos**

O modelo só inclui custos variáveis (por hectare).
Custos fixos como infraestrutura, maquinário e depreciação não estão modelados.
""")

st.divider()
st.subheader("Download do Tutorial")
col_md2, col_pdf2, _ = st.columns([1, 1, 2])
with col_md2:
    st.download_button(
        "Baixar Tutorial (.md)",
        data=tutorial_md.encode("utf-8"),
        file_name="Tutorial_LP_AgroPrime.md",
        mime="text/markdown",
        use_container_width=True,
    )
with col_pdf2:
    st.download_button(
        "Baixar Tutorial (.pdf)",
        data=pdf_bytes,
        file_name="Tutorial_LP_AgroPrime.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary",
    )
