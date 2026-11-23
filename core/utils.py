"""
Funções auxiliares para seleção ponderada e validação
"""

def is_weighted_list(items):
    """Verifica se lista tem formato [item, peso]"""
    return items and isinstance(items[0], (list, tuple)) and len(items[0]) == 2


def select_weighted(items, random_gen):
    """Seleciona item de lista ponderada"""
    if is_weighted_list(items):
        names = [i[0] for i in items]
        weights = [i[1] for i in items]
        return random_gen.choices(names, weights=weights, k=1)[0]
    return random_gen.choice(items) if items else None

