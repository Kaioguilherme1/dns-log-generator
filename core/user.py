import random
import string
from datetime import timedelta
from core.utils import select_weighted

class User:
    def __init__(self, user_id, ip, profile, domain_lists, query_types, email_subdomains, seed):
        self.user_id = user_id
        self.ip = ip
        self.profile = profile
        self.domain_lists = domain_lists
        query_dict = dict(query_types)
        self.query_types_MX = query_dict.get("MX", 0)
        self.query_types = [q for q in query_types if q[0] != "MX"]
        self.email_subdomains = email_subdomains
        # RNG determinístico
        self.random = random.Random(seed)

        self.next_event_time = None
        self.last_domain = None

        # ===============================
        # Controle de Sessão e Porta
        # ===============================
        self.session_active = False
        self.session_end_time = None
        self.current_port = None

    # =========================================================
    # Inicialização
    # =========================================================

    def initialize(self, start_timestamp):
        self.next_event_time = start_timestamp

    # =========================================================
    # Sessão
    # =========================================================

    def _generate_ephemeral_port(self):
        return self.random.randint(49152, 65535)

    def _start_session(self, current_timestamp):
        self.session_active = True
        self.current_port = self._generate_ephemeral_port()

        # duração log-normal (comportamento humano realista)
        duration_minutes = self.random.lognormvariate(2.0, 0.5)

        self.session_end_time = current_timestamp + timedelta(
            minutes=duration_minutes
        )

    def _ensure_session(self, current_timestamp):

        if not self.session_active:
            self._start_session(current_timestamp)
            return

        if current_timestamp >= self.session_end_time:
            self._start_session(current_timestamp)

    # =========================================================
    # Janela de Atividade
    # =========================================================

    def _is_active(self, timestamp):
        hour = timestamp.hour
        start = self.profile["usability_window"]["start"]
        end = self.profile["usability_window"]["end"]

        if start <= end:
            return start <= hour < end
        else:
            return hour >= start or hour < end

    # =========================================================
    # Seleção de Domínio
    # =========================================================

    def _select_query_type(self):
        """Seleciona tipo de query DNS baseado em probabilidades"""
        return select_weighted(self.query_types, self.random) or "A"

    def _select_base_domain(self):
        """Seleciona domínio base com pesos configuráveis"""
        list_name = self.profile["domain_base"]["list_name"]
        domains = self.domain_lists[list_name]
        return select_weighted(domains, self.random)

    def _generate_nxdomain(self):
        name = ''.join(self.random.choices(string.ascii_lowercase, k=10))
        return f"{name}.invalid"

    def _maybe_add_subdomain(self, domain):
        """Adiciona subdomínio com probabilidade configurada"""
        prob = self.profile["behavior_controls"]["subdomain_probability"]
        if self.random.random() < prob:
            if "subdomains" in self.domain_lists:
                sub = select_weighted(self.domain_lists["subdomains"], self.random)
            else:
                sub = ''.join(self.random.choices(string.ascii_lowercase, k=5))

            return f"{sub}.{domain}"
        return domain

    def _select_domain(self):
        controls = self.profile["behavior_controls"]

        if (
                self.last_domain
                and self.random.random() < controls["reuse_domain_probability"]
        ):
            return self.last_domain

        if self.random.random() < controls["nxdomain_probability"]:
            domain = self._generate_nxdomain()
            self.last_domain = domain
            return domain

        domain = self._select_base_domain()
        domain = self._maybe_add_subdomain(domain)

        self.last_domain = domain
        return domain

    # =========================================================
    # Intervalo entre requisições (Poisson)
    # =========================================================

    def _calculate_interval(self):
        traffic = self.profile["traffic_profile"]
        base_rpm = traffic["base_requests_per_minute"]

        if base_rpm <= 0:
            return None

        effective_rpm = base_rpm

        if self.random.random() < traffic["burst_probability"]:
            effective_rpm *= traffic["burst_multiplier"]

        mean_interval = 60.0 / effective_rpm

        return self.random.expovariate(1.0 / mean_interval)

    # =========================================================
    # Geração de Requisição
    # =========================================================

    def generate_request(self, current_timestamp):

        if self.next_event_time is None:
            self.initialize(current_timestamp)

        if current_timestamp < self.next_event_time:
            return None

        if not self._is_active(current_timestamp):
            self.next_event_time = current_timestamp + timedelta(minutes=5)
            return None

        interval = self._calculate_interval()
        if interval is None:
            return None

        # Garantir sessão válida
        self._ensure_session(current_timestamp)

        domain = self._select_domain()
        is_email_subdomain = any(sub in domain.split('.')[0] for sub in self.email_subdomains)

        if is_email_subdomain:
            if self.random.random() < self.query_types_MX:
                query_type = "MX"
            else:
                query_type = self._select_query_type()
        else:
            query_type = self._select_query_type()

        self.next_event_time = current_timestamp + timedelta(seconds=interval)

        return {
            "timestamp": current_timestamp,
            "user_id": self.user_id,
            "source_ip": self.ip,
            "source_port": self.current_port,
            "domain": domain,
            "query_type": query_type,
            "next_event_timestamp": self.next_event_time,
            "category": self.profile["category"],
            "label_flag": self.profile["labeling"]["default_flag"],
            "label_tag": self.profile["labeling"]["tag"]
        }