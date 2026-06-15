from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, lpSum, value, PULP_CBC_CMD

CULTURAS = ["Soja", "Milho", "Algodão", "Cana-de-Açúcar"]

DEFAULT_PARAMS = {
    "margem":      [3500, 2300, 4200, 3400],
    "custo":       [4500, 3200, 6000, 2800],
    "agua":        [600,  800,  500,  1500],
    "mao_obra":    [12,   15,   22,   8],
    "demanda_max": [2500, 2000, 1500, 1000],
}

DEFAULT_RECURSOS = {
    "terra":     5000,
    "orcamento": 20_000_000,
    "agua":      4_000_000,
    "mao_obra":  60_000,
}


def resolver(params: dict = None, recursos: dict = None) -> dict:
    p = params or DEFAULT_PARAMS
    r = recursos or DEFAULT_RECURSOS
    n = len(CULTURAS)

    prob = LpProblem("AgroPrime_Mix_Culturas", LpMaximize)
    x = [LpVariable(f"x{i}", lowBound=0) for i in range(n)]

    prob += lpSum(p["margem"][i] * x[i] for i in range(n)), "Lucro_Total"
    prob += lpSum(x[i] for i in range(n)) <= r["terra"], "Terra"
    prob += lpSum(p["custo"][i] * x[i] for i in range(n)) <= r["orcamento"], "Orcamento"
    prob += lpSum(p["agua"][i] * x[i] for i in range(n)) <= r["agua"], "Agua"
    prob += lpSum(p["mao_obra"][i] * x[i] for i in range(n)) <= r["mao_obra"], "Mao_Obra"
    for i in range(n):
        prob += x[i] <= p["demanda_max"][i], f"Demanda_{i}"

    prob.solve(PULP_CBC_CMD(msg=0))

    qtds = [max(0.0, value(x[i]) or 0.0) for i in range(n)]
    lucro = value(prob.objective) or 0.0

    uso_terra    = sum(qtds)
    uso_orcamento = sum(p["custo"][i] * qtds[i] for i in range(n))
    uso_agua     = sum(p["agua"][i] * qtds[i] for i in range(n))
    uso_mo       = sum(p["mao_obra"][i] * qtds[i] for i in range(n))

    return {
        "status":            LpStatus[prob.status],
        "lucro_otimo":       lucro,
        "quantidades":       qtds,
        "culturas":          CULTURAS,
        "margem_por_ha":     p["margem"],
        "receita_por_cultura": [p["margem"][i] * qtds[i] for i in range(n)],
        "params":            p,
        "uso": {
            "terra":     (uso_terra,    r["terra"],     "ha"),
            "orcamento": (uso_orcamento, r["orcamento"], "R$"),
            "agua":      (uso_agua,     r["agua"],      "m³"),
            "mao_obra":  (uso_mo,       r["mao_obra"],  "hh"),
        },
    }
