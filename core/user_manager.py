import yaml
import ipaddress
import hashlib
import random
from core.user import User
from core.logger import log_info, log_error, log_debug, log_warning


class UserManager:
    """Gerenciador de usuários e geração de IPs determinísticos"""

    def __init__(self, profile_file, network_range, domain_lists, query_types,email_subdomains, seed=None):
        if seed is None:
            seed = random.randint(1, 2**31 - 1)

        self.seed = seed
        self.master_random = random.Random(seed)

        # Validar e configurar rede
        try:
            self.network = ipaddress.ip_network(network_range)
        except ValueError as e:
            log_error(f"Erro ao processar NETWORK_RANGE '{network_range}': {e}")
            raise

        self.domain_lists = domain_lists
        self.query_types = query_types
        self.email_subdomains = email_subdomains
        self.profiles = self._load_profiles(profile_file)
        self.users = {}
        self.used_ips = set()
        self.user_counter = 0
        self.available_hosts = list(self.network.hosts())

        log_info(f"UserManager inicializado com seed: {self.seed}")
        log_debug(f"Rede: {network_range} | Hosts disponíveis: {len(self.available_hosts)}")

    # =========================================================
    # Carregamento de Perfis
    # =========================================================

    def _load_profiles(self, profile_file):
        """Carrega perfis de usuários do arquivo YAML"""
        try:
            with open(profile_file, "r") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            log_error(f"Arquivo de perfis não encontrado: {profile_file}")
            raise
        except yaml.YAMLError as e:
            log_error(f"Erro ao ler YAML {profile_file}: {e}")
            raise

        profiles = {}

        for item in data.get("profiles", []):
            profile = item["profile"]
            name = profile["name"]

            if name in profiles:
                log_error(f"Perfil duplicado detectado: {name}")
                raise ValueError(f"Perfil duplicado: {name}")

            profiles[name] = profile

        log_info(f"Carregados {len(profiles)} perfis de usuários")
        return profiles

    # =========================================================
    # Geração de IP Determinística
    # =========================================================

    def _generate_ip(self):
        """Gera IP único para usuário dentro da faixa de rede"""
        if len(self.used_ips) >= len(self.available_hosts):
            log_error(f"Sem IPs disponíveis na rede {self.network}")
            raise RuntimeError("Sem IPs disponíveis na rede")

        while True:
            ip = str(self.master_random.choice(self.available_hosts))
            if ip not in self.used_ips:
                self.used_ips.add(ip)
                return ip

    # =========================================================
    # Seed Determinística por Usuário
    # =========================================================

    def _derive_user_seed(self, profile_name):
        raw = f"{self.seed}-{self.user_counter}-{profile_name}"
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return int(hashed[:16], 16)

    # =========================================================
    # ID Determinístico
    # =========================================================


    def _generate_user_id(self):
        raw = f"{self.seed}-{self.user_counter}"
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return hashed[:16]

    # =========================================================
    # Criação de Usuário
    # =========================================================

    def create_user(self, profile_name):
        """Cria novo usuário com perfil especificado"""
        if profile_name not in self.profiles:
            log_error(f"Perfil não encontrado: {profile_name}")
            raise ValueError(f"Perfil não encontrado: {profile_name}")

        user_seed = self._derive_user_seed(profile_name)
        user_id = self._generate_user_id()
        ip = self._generate_ip()

        user = User(
            user_id=user_id,
            ip=ip,
            profile=self.profiles[profile_name],
            domain_lists=self.domain_lists,
            query_types=self.query_types,
            email_subdomains=self.email_subdomains,
            seed=user_seed
        )

        self.users[user_id] = user
        self.user_counter += 1

        log_debug(f"Usuário criado: {user_id} | IP: {ip} | Perfil: {profile_name}")
        return user

    # =========================================================
    # Obtenção de Seed
    # =========================================================

    def get_seed(self):
        """Retorna a seed do experimento"""
        return self.seed

    def list_users(self):
        return list(self.users.values())

    # =========================================================
    # Remoção
    # =========================================================

    def delete_user(self, user_id):
        """Remove usuário e libera IP"""
        if user_id in self.users:
            ip = self.users[user_id].ip
            if ip in self.used_ips:
                self.used_ips.remove(ip)
            del self.users[user_id]
            log_debug(f"Usuário removido: {user_id}")
        else:
            log_warning(f"Tentativa de remover usuário inexistente: {user_id}")

    # =========================================================
    # Modificação de Perfil
    # =========================================================

    def modify_user(self, user_id, new_profile_name):
        """Modifica o perfil de um usuário existente"""
        if user_id not in self.users:
            log_error(f"Usuário não encontrado para modificação: {user_id}")
            raise ValueError("Usuário não encontrado")

        if new_profile_name not in self.profiles:
            log_error(f"Perfil inválido para modificação: {new_profile_name}")
            raise ValueError("Perfil inválido")

        self.users[user_id].profile = self.profiles[new_profile_name]
        log_info(f"Perfil do usuário {user_id} modificado para {new_profile_name}")
