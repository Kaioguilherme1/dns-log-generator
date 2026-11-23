import heapq
import json
from datetime import datetime, timedelta
from core.log_formatter import Dns
from core.user_manager import UserManager
from core.logger import LoggerManager, log_info, log_error
from config.config import (
    TOTAL_USERS, NETWORK_RANGE, PROFILE_FILE, DOMAIN_LIST_FILE,
    SIMULATION_HOURS, SEED, PROFILE_DISTRIBUTION, QUERY_TYPES, EMAIL_SUBDOMAINS
)


def load_domain_lists():
    """Carrega domínios e subdomínios do JSON"""
    try:
        with open(DOMAIN_LIST_FILE, "r") as f:
            data = json.load(f)
        log_info(f"Arquivo de domínios carregado: {DOMAIN_LIST_FILE}")
        return {
            "default": data["domains"],
            "subdomains": data["subdomains"]
        }
    except FileNotFoundError:
        log_error(f"Arquivo de domínios não encontrado: {DOMAIN_LIST_FILE}")
        raise
    except json.JSONDecodeError:
        log_error(f"JSON inválido em {DOMAIN_LIST_FILE}")
        raise


DOMAIN_LISTS = load_domain_lists()
dns_logger = Dns()  # Instância única reutilizável


def create_users(manager):
    """Cria usuários conforme distribuição de perfis"""
    users = []
    total_created = 0

    for item in PROFILE_DISTRIBUTION:
        profile_name = item["profile"]
        percentage = item["percentage"]
        count = int(TOTAL_USERS * (percentage / 100))

        log_info(f"Criando {count} usuários com perfil '{profile_name}' ({percentage}%)")

        for _ in range(count):
            try:
                users.append(manager.create_user(profile_name))
                total_created += 1
            except Exception as e:
                log_error(f"Erro ao criar usuário: {e}")
                raise

    log_info(f"Total de usuários criados: {total_created}")
    return users


def execute_event(user, event):
    """Executa evento DNS e grava no log"""
    try:
        timestamp = event["timestamp"].strftime("%d-%b-%Y %H:%M:%S.%f")[:-3]
        dns_logger.handle_query(
            timestamp=timestamp,
            ip=event["source_ip"],
            domain=event["domain"],
            port=event["source_port"],
            qtype=event["query_type"]
        )
    except Exception as e:
        log_error(f"Erro ao executar evento DNS: {e}")
        raise

# =========================================================
# SIMULAÇÃO COM FILA DE PRIORIDADE
# =========================================================

def run_simulation(users):
    """Executa simulação DNS com fila de prioridade"""
    try:
        # Janela de 48 horas cobrindo os dias 07 e 08 de Junho de 2026
        start_time = datetime(2026, 6, 7, 0, 0, 0)
        end_time = start_time + timedelta(hours=SIMULATION_HOURS)
        event_queue = []
        counter = 0
        events_processed = 0

        # Inicializa todos os usuários
        log_info("Inicializando fila de eventos...")
        for user in users:
            user.initialize(start_time)
            heapq.heappush(event_queue, (user.next_event_time, counter, user))
            counter += 1

        log_info(f"Iniciando simulação por {SIMULATION_HOURS} hora(s) a partir de {start_time}")
        print(f"\n--- INICIANDO SIMULAÇÃO ({start_time} até {end_time}) ---\n")

        # Processa eventos até o fim da simulação
        while event_queue:
            current_time, _, user = heapq.heappop(event_queue)
            if current_time > end_time:
                break

            event = user.generate_request(current_time)
            if event:
                execute_event(user, event)
                events_processed += 1
                if events_processed % 500000 == 0:
                    print(f"Progresso: {events_processed:,} eventos processados | Simulação em: {current_time.strftime('%d-%b-%Y %H:%M:%S')}")

            heapq.heappush(event_queue, (user.next_event_time, counter, user))
            counter += 1

        print("\n--- FIM DA SIMULAÇÃO ---\n")
        log_info(f"Simulação concluída. Total de eventos processados: {events_processed}")

    except Exception as e:
        log_error(f"Erro durante a simulação: {e}")
        raise


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    try:
        # Configura sistema de logging
        LoggerManager.setup()
        log_info("=" * 60)
        log_info("Sistema de Geração de Logs DNS Iniciado")
        log_info("=" * 60)

        # Cria gerenciador de usuários
        log_info(f"Inicializando UserManager com {TOTAL_USERS} usuários potenciais")
        manager = UserManager(
            profile_file=PROFILE_FILE,
            network_range=NETWORK_RANGE,
            domain_lists=DOMAIN_LISTS,
            query_types=QUERY_TYPES,
            email_subdomains=EMAIL_SUBDOMAINS,
            seed=SEED
        )

        experiment_seed = manager.get_seed()
        log_info(f"Seed do experimento: {experiment_seed}")
        print(f"\n[EXPERIMENTO] Seed: {experiment_seed}\n")

        # Cria usuários
        users = create_users(manager)
        print(f"Total de usuários criados: {len(users)}\n")

        # Executa simulação
        run_simulation(users)

        log_info("=" * 60)
        log_info("Simulação concluída com sucesso")
        log_info("=" * 60)

    except Exception as e:
        log_error(f"Erro fatal durante execução: {e}")
        print(f"\n❌ ERRO: {e}\n")
        exit(1)
