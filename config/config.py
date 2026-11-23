"""
Configurações centralizadas do sistema de geração de logs DNS
"""

from pathlib import Path

# ========================================================
# DIRETÓRIOS
# ========================================================

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Diretório de logs
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ========================================================
# CONFIGURAÇÕES GERAIS
# ========================================================

TOTAL_USERS = 25000
NETWORK_RANGE = "10.0.0.0/16"
SIMULATION_HOURS = 48  # Simula 48 horas contínuas (janela abrangente dos ataques de 07/06 a 08/06)
SEED = 129547711  # Seed determinística do experimento para reprodutibilidade científica

# Probabilidades de eventos anômalos
PROB_TIMEOUT = 0.02       # 2% de timeout
PROB_LOOP = 0.01          # 1% de loop detectado
PROB_CACHE_DENIED = 0.01  # 1% de cache negado

# ========================================================
# ARQUIVOS DE CONFIGURAÇÃO
# ========================================================

PROFILE_FILE = str(PROJECT_ROOT / "config" / "profiles.yaml")
DOMAIN_LIST_FILE = str(PROJECT_ROOT / "config" / "domain_list.json")

# ========================================================
# CONFIGURAÇÕES DE LOGGING
# ========================================================

# Arquivo de log principal (eventos do sistema)
LOG_FILE = LOG_DIR / "system.log"

# Arquivo de log de eventos DNS
DNS_LOG_FILE = LOG_DIR / "dns_events.log"

# Nível de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Formato de log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Tamanho máximo de arquivo de log (100GB)
LOG_MAX_SIZE = 100 * 1024 * 1024 * 1024

# Número de backups de logs a manter
LOG_BACKUP_COUNT = 5

# ========================================================
# DISTRIBUIÇÃO DE PERFIS
# ========================================================

PROFILE_DISTRIBUTION = [
    {"profile": "student_user", "percentage": 25},
    {"profile": "office_employee", "percentage": 25},
    {"profile": "home_user", "percentage": 25},
    {"profile": "devops_engineer", "percentage": 5},
    {"profile": "casual_mobile_user", "percentage": 20},
]

# ========================================================
# TIPOS DE QUERY DNS COM PROBABILIDADES
# ========================================================
# Formato: [tipo, probabilidade]
# Probabilidade entre 0.00 e 1.00 (soma recomendada = 1.00)
# https://radar.cloudflare.com/explorer?dataSet=dns&groupBy=query_type base de dados coleta da semana 09/06/2026 ultimos 7 dias

QUERY_TYPES = [
    ["A", 0.64],     # IPv4 dominante
    ["AAAA", 0.21],  # IPv6 comum
    ["MX", 0.031],    # e-mail
    ["TXT", 0.011],   # SPF/DKIM/verificações
    ["CNAME", 0.027], # aliases
    ["NS", 0.02],    # delegações
    ["PTR", 0.02],   # reverse lookup
]

# Subdomínios comuns de e-mail
EMAIL_SUBDOMAINS = [
    "mail", "smtp", "pop", "imap", "webmail", "mx", "email", "newsletter", "admin", "support"
]