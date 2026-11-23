"""
Sistema centralizado de logging para eventos do sistema e DNS
"""

import logging
from logging.handlers import RotatingFileHandler
from config.config import (
    LOG_FILE, DNS_LOG_FILE, LOG_LEVEL, LOG_FORMAT,
    LOG_MAX_SIZE, LOG_BACKUP_COUNT
)


class LoggerManager:
    """Gerenciador centralizado de logs do sistema"""

    _system_logger = None
    _dns_logger = None

    @classmethod
    def setup(cls):
        """Configura os loggers do sistema e DNS"""
        cls._setup_system_logger()
        cls._setup_dns_logger()

    @classmethod
    def _setup_system_logger(cls):
        """Configura logger de eventos do sistema"""
        cls._system_logger = logging.getLogger("system")
        cls._system_logger.setLevel(getattr(logging, LOG_LEVEL))

        # Remove handlers existentes
        cls._system_logger.handlers = []

        # Handler de arquivo com rotação
        file_handler = RotatingFileHandler(
            str(LOG_FILE),
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        # Formato nativo puro BIND9 (sem prefixos extras do Python para realismo e redução de espaço)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        cls._system_logger.addHandler(file_handler)

        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        cls._system_logger.addHandler(console_handler)

    @classmethod
    def _setup_dns_logger(cls):
        """Configura logger para eventos DNS"""
        cls._dns_logger = logging.getLogger("dns")
        cls._dns_logger.setLevel(getattr(logging, LOG_LEVEL))

        # Remove handlers existentes
        cls._dns_logger.handlers = []

        # Handler de arquivo com rotação
        file_handler = RotatingFileHandler(
            str(DNS_LOG_FILE),
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        # Formato nativo puro BIND9 (sem prefixos extras do Python para realismo e redução de espaço)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        cls._dns_logger.addHandler(file_handler)

    @classmethod
    def get_system_logger(cls):
        """Retorna o logger de sistema"""
        if cls._system_logger is None:
            cls.setup()
        return cls._system_logger

    @classmethod
    def get_dns_logger(cls):
        """Retorna o logger de DNS"""
        if cls._dns_logger is None:
            cls.setup()
        return cls._dns_logger


# Funções de conveniência global
def log_info(message):
    """Log de informação do sistema"""
    LoggerManager.get_system_logger().info(message)


def log_warning(message):
    """Log de aviso do sistema"""
    LoggerManager.get_system_logger().warning(message)


def log_error(message):
    """Log de erro do sistema"""
    LoggerManager.get_system_logger().error(message)


def log_debug(message):
    """Log de debug do sistema"""
    LoggerManager.get_system_logger().debug(message)


def log_dns_event(log_message):
    """Log de evento DNS (sem timestamp separado)"""
    LoggerManager.get_dns_logger().info(log_message)

