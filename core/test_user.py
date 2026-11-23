import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from config.config import PROFILE_FILE, QUERY_TYPES, EMAIL_SUBDOMAINS
from core.user_manager import UserManager


# =========================================================
# CONFIGURAÇÃO
# =========================================================

NETWORK_RANGE = "192.168.0.0/29"  # pequena para teste
SEED = 42

# Base de domínios compatível com UserManager/User
domain_lists = {
    "default": [
        ["google.com", 0.45],
        ["github.com", 0.30],
        ["wikipedia.org", 0.25],
    ],
    "subdomains": [
        ["www", 0.60],
        ["mail", 0.40],
    ],
}


# =========================================================
# FUNÇÃO DE EXECUÇÃO
# =========================================================

def run_simulation():
    print("=" * 80)
    print("INICIALIZANDO USER MANAGER")
    print("=" * 80)

    manager = UserManager(
        profile_file=PROFILE_FILE,
        network_range=NETWORK_RANGE,
        domain_lists=domain_lists,
        query_types=QUERY_TYPES,
        email_subdomains=EMAIL_SUBDOMAINS,
        seed=SEED,
    )

    print("\nCriando usuário...")
    user = manager.create_user("student_user")

    print(f"User ID: {user.user_id}")
    print(f"IP: {user.ip}")
    print(f"Profile: {user.profile['name']}")
    print("-" * 80)

    # Timestamp inicial dentro da janela ativa
    current_time = datetime(2025, 1, 1, 10, 0, 0)

    print("Simulação por 10 minutos")
    print("-" * 80)

    end_time = current_time + timedelta(minutes=10)

    while current_time < end_time:
        result = user.generate_request(current_time)

        if result:
            print(f"[{result['timestamp']}]")
            print(f"  user_id: {result['user_id']}")
            print(f"  ip: {result['source_ip']}")
            print(f"  port: {result['source_port']}")
            print(f"  domain: {result['domain']}")
            print(f"  qtype: {result['query_type']}")
            print(f"  next_event: {result['next_event_timestamp']}")
            print(f"  label: {result['label_flag']} ({result['label_tag']})")
            print("-" * 60)

        current_time += timedelta(seconds=5)

    print("=" * 80)
    print("FIM DA SIMULAÇÃO")
    print("=" * 80)


# =========================================================
# TESTE DE REPRODUTIBILIDADE
# =========================================================

def test_reproducibility():
    print("\n" + "=" * 80)
    print("TESTE DE REPRODUTIBILIDADE")
    print("=" * 80)

    manager1 = UserManager(
        PROFILE_FILE, NETWORK_RANGE, domain_lists, QUERY_TYPES, EMAIL_SUBDOMAINS, SEED
    )
    manager2 = UserManager(
        PROFILE_FILE, NETWORK_RANGE, domain_lists, QUERY_TYPES, EMAIL_SUBDOMAINS, SEED
    )

    user1 = manager1.create_user("student_user")
    user2 = manager2.create_user("student_user")

    timestamp = datetime(2025, 1, 1, 10, 0, 0)

    r1 = user1.generate_request(timestamp)
    r2 = user2.generate_request(timestamp)

    print("Comparando primeira requisição gerada:")
    print("Manager 1:", r1)
    print("Manager 2:", r2)

    assert r1 == r2, f"Divergência de determinismo: {r1} != {r2}"
    print("STATUS: COMPORTAMENTO REPRODUZÍVEL")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    run_simulation()
    test_reproducibility()
