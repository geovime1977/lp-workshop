def br(v, d=2):
    """Formata número no padrão brasileiro: 1.234.567,89"""
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
