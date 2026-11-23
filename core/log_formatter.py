import hashlib
import random
from datetime import datetime
from config.config import PROB_TIMEOUT, PROB_LOOP, PROB_CACHE_DENIED
from core.logger import log_dns_event

class Dns:
    """
    Gerador de logs realistas no padrão do BIND.
    Inclui sucesso, falha, RPZ, cache deny, loop e timeout.
    """

    def __init__(self, resolver_ip="192.168.0.10", view="internal", default_flag=0):
        self.resolver_ip = resolver_ip
        self.view = view
        self.default_flag = default_flag

    # =====================================================
    # Utilidades
    # =====================================================

    def _client_ptr(self, ip: str, port: int) -> str:
        base = f"{ip}:{port}".encode()
        digest = hashlib.sha256(base).hexdigest()
        return "0x" + digest[:12]

    # =====================================================
    # Eventos principais
    # =====================================================

    def query(self, timestamp, domain, ip, port, qtype):
        return (
            f"{timestamp} client @{self._client_ptr(ip, port)} "
            f"{ip}#{port} ({domain}): query: {domain} IN {qtype} +E(0) "
            f"({self.resolver_ip})"
        )

    # =====================================================
    # RPZ / CNAME rewrite
    # =====================================================

    def rpz_rewrite(self, timestamp, domain, ip, port, qtype, target="google.com"):
        return (
            f"{timestamp} client @{self._client_ptr(ip, port)} "
            f"{ip}#{port} ({domain}): view {self.view}: "
            f"rpz QNAME CNAME rewrite {domain}/{qtype}/IN "
            f"via {domain}.rpz.zone "
            f"(CNAME to: {target})"
        )

    # =====================================================
    # Falhas e anomalias
    # =====================================================

    def timeout(self, timestamp, domain, qtype, authoritative_ip):
        return (
            f"{timestamp} timed out resolving "
            f"'{domain}/{qtype}/IN': {authoritative_ip}#53"
        )

    def loop_detected(self, timestamp, domain, qtype):
        return (
            f"{timestamp} loop detected resolving "
            f"'{domain}/{qtype}'"
        )

    def cache_denied(self, timestamp, domain, ip, port, qtype):
        return (
            f"{timestamp} client @{self._client_ptr(ip, port)} "
            f"{ip}#{port} ({domain}): view {self.view}: "
            f"query (cache) '{domain}/{qtype}/IN' denied"
        )

    def zone_refresh_error(self, timestamp, zone):
        path = f"/etc/bind/zones/slave/{zone}"
        return (
            f"{timestamp} zone {zone}/IN/{self.view}: refresh: "
            f"could not set file modification time of "
            f"'{path}': permission denied"
        )

    def handle_query(self, timestamp, domain, ip, port, qtype):
        """Processa query DNS e retorna log formatado"""
        R = random.random()

        if R < PROB_TIMEOUT:
            log_message = self.timeout(timestamp, domain, qtype, "234.21.34.20")
        elif R < PROB_TIMEOUT + PROB_LOOP:
            log_message = self.loop_detected(timestamp, domain, qtype)
        elif R < PROB_TIMEOUT + PROB_LOOP + PROB_CACHE_DENIED:
            log_message = self.cache_denied(timestamp, domain, ip, port, qtype)
        else:
            log_message = self.query(timestamp, domain, ip, port, qtype)

        # Registra evento em arquivo de log DNS
        log_dns_event(log_message)

        return log_message
