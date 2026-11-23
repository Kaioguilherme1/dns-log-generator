import pandas as pd
import numpy as np
import json

# Configurações
INPUT_CSV = "cloudflare-radar_top-100-domains_20260217.csv"   # CSV já ordenado por rank
OUTPUT_JSON = "domains_distribution.json"
ZIPF_EXPONENT = 1.0       # Exponente da lei de potência (1 = clássico Zipf)

# --- 1) Carrega CSV ---
df = pd.read_csv(INPUT_CSV)

# --- 2) Gera distribuição decrescente (Zipf-like) ---
N = len(df)
ranks = np.arange(1, N+1)                   # 1,2,3,...N
weights = 1 / (ranks ** ZIPF_EXPONENT)      # Zipf-like
weights = weights / weights.sum()           # normaliza para somar 1

# --- 3) Cria lista no formato ["dominio", percentual] ---
domains_list = [[domain, float(f"{weight:.4f}")] for domain, weight in zip(df["domain"], weights)]

# --- 4) Exporta JSON ---
output = {"domains": domains_list}
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4)

print(f"Distribuição gerada com sucesso em {OUTPUT_JSON}")