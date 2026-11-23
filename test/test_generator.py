import ipaddress
import json
import os
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import (
    DOMAIN_LIST_FILE,
    EMAIL_SUBDOMAINS,
    NETWORK_RANGE,
    PROFILE_FILE,
    QUERY_TYPES,
    SEED,
)
from core.log_formatter import Dns
from core.user_manager import UserManager


def _load_domains():
    with open(DOMAIN_LIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"default": data["domains"], "subdomains": data["subdomains"]}


def _make_manager(seed=SEED):
    return UserManager(
        profile_file=PROFILE_FILE,
        network_range=NETWORK_RANGE,
        domain_lists=_load_domains(),
        query_types=QUERY_TYPES,
        email_subdomains=EMAIL_SUBDOMAINS,
        seed=seed,
    )


def test_deterministic_seed_produces_identical_sequence():
    """Duas instâncias com SEED=129547711 devem gerar IP e 20 eventos idênticos."""
    m1 = _make_manager(SEED)
    m2 = _make_manager(SEED)

    u1 = m1.create_user("devops_engineer")
    u2 = m2.create_user("devops_engineer")

    assert u1.user_id == u2.user_id
    assert u1.ip == u2.ip

    t1 = datetime(2026, 6, 7, 10, 0, 0)
    t2 = datetime(2026, 6, 7, 10, 0, 0)
    events_1 = []
    events_2 = []

    for _ in range(20):
        ev1 = u1.generate_request(t1)
        ev2 = u2.generate_request(t2)
        events_1.append(ev1)
        events_2.append(ev2)
        t1 = u1.next_event_time
        t2 = u2.next_event_time

    assert events_1 == events_2
    assert all(ev is not None for ev in events_1)


def test_profiles_network_and_ephemeral_ports():
    """Valida carregamento dos 5 perfis, faixa 10.0.0.0/16 e portas efêmeras."""
    manager = _make_manager(SEED)
    expected_profiles = {
        "student_user",
        "office_employee",
        "home_user",
        "devops_engineer",
        "casual_mobile_user",
    }
    assert set(manager.profiles.keys()) == expected_profiles

    net = ipaddress.ip_network(NETWORK_RANGE)
    ts = datetime(2026, 6, 7, 12, 0, 0)  # horário ativo para todos os perfis

    for profile_name in expected_profiles:
        user = manager.create_user(profile_name)
        assert ipaddress.ip_address(user.ip) in net
        ev = user.generate_request(ts)
        assert ev is not None
        assert 49152 <= ev["source_port"] <= 65535
        assert ev["domain"]
        assert ev["query_type"]


def test_bind9_query_log_formatting_without_file_io():
    """Valida a sintaxe BIND 9 gerada por Dns.query() sem criar arquivos em logs/."""
    formatter = Dns(resolver_ip="192.168.0.10")
    line = formatter.query(
        timestamp="07-Jun-2026 10:00:00.123",
        domain="www.google.com",
        ip="10.0.12.34",
        port=54321,
        qtype="A",
    )
    pattern = (
        r"^\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}\.\d{3} "
        r"client @0x[0-9a-f]+ \d+\.\d+\.\d+\.\d+#\d+ \([^)]+\): "
        r"query: [^ ]+ IN [A-Z]+ \+E\(0\) \(192\.168\.0\.10\)$"
    )
    assert re.match(pattern, line)
