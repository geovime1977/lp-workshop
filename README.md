# AgroPrime LP — Otimização do Mix de Culturas

App Streamlit desenvolvido para o workshop de Programação Linear do MBA em Pesquisa Operacional (Prof. Gabriel Capela — BSBr).

Caso real: Cooperativa AgroPrime precisa decidir quantos hectares alocar entre Soja, Milho, Algodão e Cana-de-Açúcar para maximizar a margem de contribuição respeitando restrições de área, orçamento, água e mão de obra.

## Módulos

| Página | Conteúdo |
|---|---|
| Tutorial | Guia de uso do app e conceitos de LP |
| Contextualização | Problema da AgroPrime e dados de entrada |
| Modelagem Matemática | Função objetivo + restrições em notação formal |
| Solver Interativo | Resolução via PuLP + análise de sensibilidade |
| Resultados e Slides | PPTX (12 slides) + PDF com documento de modelagem |
| Método Gráfico | Visualização 2D da região viável (Soja × Milho) |

## Stack

- Python + Streamlit
- PuLP (solver LP)
- NumPy / Pandas / Matplotlib
- python-pptx + fpdf2 (exportação)

## Como rodar

```bash
git clone https://github.com/geovime1977/lp-workshop
cd lp-workshop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8505
```

Acesso: http://localhost:8505
