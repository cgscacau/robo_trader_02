"""
=============================================================================
MÓDULO DE LOGGING PROFISSIONAL
=============================================================================
Sistema de logging robusto para rastreamento de operações,
erros e eventos do sistema de trading.
"""

import logging
import os
from datetime import datetime
from typing import Optional
import sys

class TradingLogger:
    """
    Classe para gerenciamento de logs do sistema de trading.
    Cria logs separados para diferentes tipos de eventos.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Inicializa o sistema de logging.
        
        Args:
            log_dir: Diretório onde os logs serão salvos
        """
        self.log_dir = log_dir
        self._create_log_directory()
        self._setup_loggers()
    
    def _create_log_directory(self):
        """Cria o diretório de logs se não existir."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_loggers(self):
        """Configura os diferentes tipos de loggers."""
        
        # Formatter padrão para todos os logs
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # =======================================================================
        # LOGGER PRINCIPAL DO SISTEMA
        # =======================================================================
        self.main_logger = logging.getLogger('trading_system')
        self.main_logger.setLevel(logging.INFO)
        
        # Handler para arquivo principal
        main_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'trading_system.log'),
            encoding='utf-8'
        )
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.main_logger.addHandler(console_handler)
        
        # =======================================================================
        # LOGGER PARA OPERAÇÕES DE TRADING
        # =======================================================================
        self.trading_logger = logging.getLogger('trading_operations')
        self.trading_logger.setLevel(logging.INFO)
        
        trading_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'trading_operations.log'),
            encoding='utf-8'
        )
        trading_handler.setFormatter(formatter)
        self.trading_logger.addHandler(trading_handler)
        
        # =======================================================================
        # LOGGER PARA ERROS
        # =======================================================================
        self.error_logger = logging.getLogger('trading_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'errors.log'),
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
        # =======================================================================
        # LOGGER PARA API
        # =======================================================================
        self.api_logger = logging.getLogger('api_requests')
        self.api_logger.setLevel(logging.INFO)
        
        api_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'api_requests.log'),
            encoding='utf-8'
        )
        api_handler.setFormatter(formatter)
        self.api_logger.addHandler(api_handler)
    
    def log_info(self, message: str, logger_type: str = 'main'):
        """
        Registra mensagem informativa.
        
        Args:
            message: Mensagem a ser registrada
            logger_type: Tipo de logger ('main', 'trading', 'api')
        """
        logger = getattr(self, f'{logger_type}_logger', self.main_logger)
        logger.info(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """
        Registra erro no sistema.
        
        Args:
            message: Mensagem de erro
            exception: Exceção capturada (opcional)
        """
        if exception:
            self.error_logger.error(f"{message} | Exception: {str(exception)}")
        else:
            self.error_logger.error(message)
    
    def log_warning(self, message: str, logger_type: str = 'main'):
        """
        Registra aviso no sistema.
        
        Args:
            message: Mensagem de aviso
            logger_type: Tipo de logger
        """
        logger = getattr(self, f'{logger_type}_logger', self.main_logger)
        logger.warning(message)
    
    def log_trading_operation(self, operation_type: str, symbol: str, 
                            quantity: float, price: float, 
                            additional_info: str = ""):
        """
        Registra operação de trading específica.
        
        Args:
            operation_type: Tipo da operação (BUY, SELL, etc.)
            symbol: Símbolo da moeda
            quantity: Quantidade
            price: Preço
            additional_info: Informações adicionais
        """
        message = f"{operation_type} | {symbol} | Qty: {quantity} | Price: {price}"
        if additional_info:
            message += f" | {additional_info}"
        
        self.trading_logger.info(message)
    
    def log_api_request(self, endpoint: str, method: str, 
                       status_code: Optional[int] = None,
                       response_time: Optional[float] = None):
        """
        Registra requisição para API.
        
        Args:
            endpoint: Endpoint da API
            method: Método HTTP
            status_code: Código de status da resposta
            response_time: Tempo de resposta em segundos
        """
        message = f"{method} {endpoint}"
        if status_code:
            message += f" | Status: {status_code}"
        if response_time:
            message += f" | Time: {response_time:.3f}s"
        
        self.api_logger.info(message)

# Instância global do logger
trading_logger = TradingLogger()
