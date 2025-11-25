"""
=============================================================================
CLIENTE BINANCE API - MÓDULO PRINCIPAL
=============================================================================
Cliente robusto para conexão com a API da Binance, incluindo
tratamento de erros, reconexão automática e WebSocket.
"""

import ccxt
import asyncio
import websocket
import json
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import pandas as pd

from ..config.settings import TradingConfig
from ..utils.logger import trading_logger

class BinanceClient:
    """
    Cliente principal para interação com a API da Binance.
    Gerencia conexões REST e WebSocket de forma robusta.
    """
    
    def __init__(self):
        """Inicializa o cliente Binance."""
        self.exchange = None
        self.ws_connection = None
        self.is_connected = False
        self.is_testnet = True  # Inicia em testnet por segurança
        self.account_type = 'spot'  # 'spot' ou 'futures'
        self.reconnection_attempts = 0
        self.max_reconnection_attempts = TradingConfig.MAX_RECONNECTION_ATTEMPTS
        
        # Callbacks para dados em tempo real
        self.price_callbacks: List[Callable] = []
        self.order_callbacks: List[Callable] = []
        
        # Cache de dados
        self.symbol_info_cache = {}
        self.price_cache = {}
        
        trading_logger.log_info("Cliente Binance inicializado", 'api')
    
    def authenticate(self, api_key: str, api_secret: str, 
                    testnet: bool = True, account_type: str = 'spot') -> bool:
        """
        Autentica com a API da Binance.
        
        Args:
            api_key: Chave da API
            api_secret: Segredo da API
            testnet: Se True, usa testnet; se False, usa mainnet
            account_type: 'spot' ou 'futures'
            
        Returns:
            True se autenticação bem-sucedida, False caso contrário
        """
        try:
            self.is_testnet = testnet
            self.account_type = account_type
            
            # Configuração base do exchange
            exchange_config = {
                'apiKey': api_key,
                'secret': api_secret,
                'timeout': TradingConfig.API_TIMEOUT * 1000,  # ccxt usa millisegundos
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True,
                }
            }
            
            # Configuração específica por tipo de conta
            if account_type == 'futures':
                if testnet:
                    exchange_config['sandbox'] = True
                    exchange_config['urls'] = {
                        'api': TradingConfig.BINANCE_API_URLS['futures_testnet'],
                    }
                else:
                    exchange_config['urls'] = {
                        'api': TradingConfig.BINANCE_API_URLS['futures_mainnet'],
                    }
            else:  # spot
                if testnet:
                    exchange_config['sandbox'] = True
                    exchange_config['urls'] = {
                        'api': TradingConfig.BINANCE_API_URLS['testnet'],
                    }
            
            # Inicializa o exchange
            self.exchange = ccxt.binance(exchange_config)
            
            # Testa a conexão
            balance = self.exchange.fetch_balance()
            
            self.is_connected = True
            self.reconnection_attempts = 0
            
            env_type = "TESTNET" if testnet else "MAINNET"
            trading_logger.log_info(
                f"Autenticação bem-sucedida - {env_type} - {account_type.upper()}", 
                'api'
            )
            
            return True
            
        except Exception as e:
            self.is_connected = False
            trading_logger.log_error(f"Falha na autenticação: {str(e)}", e)
            return False
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """
        Obtém saldo da conta.
        
        Returns:
            Dicionário com informações de saldo ou None em caso de erro
        """
        if not self.is_connected or not self.exchange:
            trading_logger.log_error("Cliente não autenticado")
            return None
        
        try:
            start_time = time.time()
            balance = self.exchange.fetch_balance()
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                'fetch_balance', 'GET', 200, response_time
            )
            
            # Filtra apenas moedas com saldo > 0
            filtered_balance = {}
            for currency, info in balance.items():
                if isinstance(info, dict) and info.get('total', 0) > 0:
                    filtered_balance[currency] = info
            
            return {
                'total_balance': balance.get('total', {}),
                'free_balance': balance.get('free', {}),
                'used_balance': balance.get('used', {}),
                'currencies': filtered_balance
            }
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter saldo: {str(e)}", e)
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas de um símbolo.
        
        Args:
            symbol: Símbolo da moeda (ex: 'BTCUSDT')
            
        Returns:
            Informações do símbolo ou None em caso de erro
        """
        if not self.is_connected or not self.exchange:
            return None
        
        # Verifica cache primeiro
        if symbol in self.symbol_info_cache:
            return self.symbol_info_cache[symbol]
        
        try:
            start_time = time.time()
            markets = self.exchange.load_markets()
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                'load_markets', 'GET', 200, response_time
            )
            
            if symbol in markets:
                symbol_info = markets[symbol]
                
                # Cache das informações
                self.symbol_info_cache[symbol] = {
                    'symbol': symbol,
                    'base': symbol_info['base'],
                    'quote': symbol_info['quote'],
                    'active': symbol_info['active'],
                    'precision': symbol_info['precision'],
                    'limits': symbol_info['limits'],
                    'fees': symbol_info.get('fees', {}),
                    'info': symbol_info.get('info', {})
                }
                
                return self.symbol_info_cache[symbol]
            
            return None
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter info do símbolo {symbol}: {str(e)}", e)
            return None
    
    def get_historical_data(self, symbol: str, timeframe: str, 
                          limit: int = 500) -> Optional[pd.DataFrame]:
        """
        Obtém dados históricos de preços.
        
        Args:
            symbol: Símbolo da moeda
            timeframe: Timeframe dos dados
            limit: Número máximo de candles
            
        Returns:
            DataFrame com dados históricos ou None em caso de erro
        """
        if not self.is_connected or not self.exchange:
            return None
        
        try:
            start_time = time.time()
            
            # Limita o número de candles
            limit = min(limit, TradingConfig.MAX_HISTORICAL_CANDLES)
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                f'fetch_ohlcv/{symbol}/{timeframe}', 'GET', 200, response_time
            )
            
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                trading_logger.log_info(
                    f"Dados históricos obtidos: {symbol} - {len(df)} candles", 'api'
                )
                
                return df
            
            return None
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter dados históricos {symbol}: {str(e)}", e)
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obtém preço atual de um símbolo.
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Preço atual ou None em caso de erro
        """
        if not self.is_connected or not self.exchange:
            return None
        
        try:
            start_time = time.time()
            ticker = self.exchange.fetch_ticker(symbol)
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                f'fetch_ticker/{symbol}', 'GET', 200, response_time
            )
            
            price = ticker.get('last')
            if price:
                self.price_cache[symbol] = {
                    'price': price,
                    'timestamp': datetime.now()
                }
            
            return price
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter preço de {symbol}: {str(e)}", e)
            return None
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   amount: float, price: Optional[float] = None,
                   params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Executa uma ordem.
        
        Args:
            symbol: Símbolo da moeda
            side: 'buy' ou 'sell'
            order_type: 'market', 'limit', etc.
            amount: Quantidade
            price: Preço (para ordens limit)
            params: Parâmetros adicionais
            
        Returns:
            Informações da ordem ou None em caso de erro
        """
        if not self.is_connected or not self.exchange:
            trading_logger.log_error("Cliente não conectado para executar ordem")
            return None
        
        try:
            start_time = time.time()
            
            # Parâmetros padrão
            if params is None:
                params = {}
            
            # Executa a ordem baseada no tipo
            if order_type.lower() == 'market':
                order = self.exchange.create_market_order(symbol, side, amount, None, None, params)
            elif order_type.lower() == 'limit':
                if price is None:
                    trading_logger.log_error("Preço necessário para ordem limit")
                    return None
                order = self.exchange.create_limit_order(symbol, side, amount, price, None, params)
            else:
                trading_logger.log_error(f"Tipo de ordem não suportado: {order_type}")
                return None
            
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                f'create_{order_type}_order', 'POST', 200, response_time
            )
            
            trading_logger.log_trading_operation(
                side.upper(), symbol, amount, price or 0,
                f"Order ID: {order.get('id', 'N/A')} | Type: {order_type}"
            )
            
            return order
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao executar ordem: {str(e)}", e)
            return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtém ordens abertas.
        
        Args:
            symbol: Símbolo específico (opcional)
            
        Returns:
            Lista de ordens abertas
        """
        if not self.is_connected or not self.exchange:
            return []
        
        try:
            start_time = time.time()
            orders = self.exchange.fetch_open_orders(symbol)
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                f'fetch_open_orders/{symbol or "all"}', 'GET', 200, response_time
            )
            
            return orders
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter ordens abertas: {str(e)}", e)
            return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancela uma ordem.
        
        Args:
            order_id: ID da ordem
            symbol: Símbolo da moeda
            
        Returns:
            True se cancelada com sucesso, False caso contrário
        """
        if not self.is_connected or not self.exchange:
            return False
        
        try:
            start_time = time.time()
            result = self.exchange.cancel_order(order_id, symbol)
            response_time = time.time() - start_time
            
            trading_logger.log_api_request(
                f'cancel_order/{order_id}', 'DELETE', 200, response_time
            )
            
            trading_logger.log_trading_operation(
                'CANCEL', symbol, 0, 0, f"Order ID: {order_id}"
            )
            
            return True
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao cancelar ordem {order_id}: {str(e)}", e)
            return False
    
    def disconnect(self):
        """Desconecta do cliente e limpa recursos."""
        try:
            if self.ws_connection:
                self.ws_connection.close()
            
            self.is_connected = False
            self.exchange = None
            self.symbol_info_cache.clear()
            self.price_cache.clear()
            
            trading_logger.log_info("Cliente Binance desconectado", 'api')
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao desconectar: {str(e)}", e)

# Instância global do cliente
binance_client = BinanceClient()
