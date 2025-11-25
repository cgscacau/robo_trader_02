"""
=============================================================================
CLIENTE BINANCE API - VERSÃO CLOUD OTIMIZADA
=============================================================================
Cliente híbrido que suporta modo demo (WebSocket público) 
e modo autenticado para operações reais.
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
import requests

from ..config.settings import TradingConfig
from ..utils.logger import trading_logger

class BinanceClient:
    """
    Cliente híbrido para interação com a Binance.
    Suporta modo demo (público) e modo autenticado.
    """
    
    def __init__(self):
        """Inicializa o cliente Binance."""
        self.exchange = None
        self.ws_connection = None
        self.ws_thread = None
        
        # Estados de conexão
        self.is_connected = False
        self.is_authenticated = False
        self.operation_mode = 'demo'  # 'demo', 'paper_trading', 'live_trading'
        
        # Configurações atuais
        self.current_symbol = 'BTCUSDT'
        self.current_timeframe = '1h'
        
        # Callbacks para dados em tempo real
        self.price_callbacks: List[Callable] = []
        self.kline_callbacks: List[Callable] = []
        
        # Cache de dados
        self.symbol_info_cache = {}
        self.price_cache = {}
        self.kline_cache = {}
        
        # Credenciais temporárias (apenas em memória)
        self.temp_credentials = None
        self.credentials_timestamp = None
        
        trading_logger.log_info("Cliente Binance inicializado em modo DEMO", 'api')
    
    def set_operation_mode(self, mode: str) -> bool:
        """
        Define o modo de operação do cliente.
        
        Args:
            mode: 'demo', 'paper_trading', ou 'live_trading'
            
        Returns:
            True se modo definido com sucesso
        """
        if mode not in TradingConfig.OPERATION_MODES:
            trading_logger.log_error(f"Modo inválido: {mode}")
            return False
        
        self.operation_mode = mode
        mode_config = TradingConfig.get_operation_mode_config(mode)
        
        trading_logger.log_info(f"Modo alterado para: {mode_config['name']}", 'api')
        
        # Se modo demo, inicia WebSocket público
        if mode == 'demo':
            self.is_connected = True
            self.is_authenticated = False
            self._start_public_websocket()
        
        return True
    
    def authenticate(self, api_key: str, api_secret: str, 
                    testnet: bool = True, account_type: str = 'spot') -> Dict[str, Any]:
        """
        Autentica com a API da Binance com validação aprimorada.
        
        Args:
            api_key: Chave da API
            api_secret: Segredo da API
            testnet: Se True, usa testnet
            account_type: 'spot' ou 'futures'
            
        Returns:
            Dicionário com resultado da autenticação
        """
        # Validação inicial de formato
        validation = TradingConfig.validate_credentials_format(api_key, api_secret)
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors'],
                'message': 'Formato das credenciais inválido'
            }
        
        try:
            # Limpa credenciais anteriores
            self._clear_credentials()
            
            # Configuração do exchange
            exchange_config = {
                'apiKey': api_key.strip(),
                'secret': api_secret.strip(),
                'timeout': TradingConfig.API_TIMEOUT * 1000,
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True,
                }
            }
            
            # URLs baseadas no ambiente
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
            
            # Testa a conexão com timeout
            start_time = time.time()
            balance = self.exchange.fetch_balance()
            response_time = time.time() - start_time
            
            # Armazena credenciais temporariamente
            self.temp_credentials = {
                'api_key': api_key,
                'api_secret': api_secret,
                'testnet': testnet,
                'account_type': account_type
            }
            self.credentials_timestamp = datetime.now()
            
            # Define estados
            self.is_connected = True
            self.is_authenticated = True
            
            # Define modo baseado no ambiente
            if testnet:
                self.operation_mode = 'paper_trading'
            else:
                self.operation_mode = 'live_trading'
            
            env_type = "TESTNET" if testnet else "MAINNET"
            trading_logger.log_info(
                f"Autenticação bem-sucedida - {env_type} - {account_type.upper()} - {response_time:.2f}s", 
                'api'
            )
            
            return {
                'success': True,
                'message': f'Conectado com sucesso ao {env_type}',
                'environment': env_type,
                'account_type': account_type,
                'response_time': response_time,
                'balance_currencies': len([k for k, v in balance.get('total', {}).items() if v > 0])
            }
            
        except ccxt.AuthenticationError as e:
            self._clear_credentials()
            error_msg = "Credenciais inválidas ou sem permissão"
            trading_logger.log_error(f"Erro de autenticação: {str(e)}", e)
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'authentication',
                'suggestion': 'Verifique suas credenciais e permissões da API'
            }
            
        except ccxt.NetworkError as e:
            self._clear_credentials()
            error_msg = "Erro de conexão com a Binance"
            trading_logger.log_error(f"Erro de rede: {str(e)}", e)
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'network',
                'suggestion': 'Verifique sua conexão com a internet'
            }
            
        except Exception as e:
            self._clear_credentials()
            error_msg = f"Erro inesperado: {str(e)}"
            trading_logger.log_error(f"Erro na autenticação: {str(e)}", e)
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'unknown',
                'suggestion': 'Tente novamente ou contate o suporte'
            }
    
    def _clear_credentials(self):
        """Limpa credenciais da memória."""
        self.temp_credentials = None
        self.credentials_timestamp = None
        self.is_authenticated = False
        if hasattr(self, 'exchange'):
            self.exchange = None
    
    def _check_credentials_timeout(self) -> bool:
        """
        Verifica se as credenciais expiraram.
        
        Returns:
            True se credenciais ainda válidas
        """
        if not self.credentials_timestamp:
            return False
        
        timeout_minutes = TradingConfig.CREDENTIALS_TIMEOUT
        elapsed = datetime.now() - self.credentials_timestamp
        
        if elapsed.total_seconds() > (timeout_minutes * 60):
            trading_logger.log_warning("Credenciais expiraram por timeout", 'api')
            self._clear_credentials()
            return False
        
        return True
    
    def get_public_price_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de preço via API pública (sem autenticação).
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Dados de preço ou None em caso de erro
        """
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'symbol': data['symbol'],
                    'price': float(data['lastPrice']),
                    'change': float(data['priceChange']),
                    'change_percent': float(data['priceChangePercent']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume']),
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter dados públicos de {symbol}: {str(e)}", e)
            return None
    
    def get_public_historical_data(self, symbol: str, timeframe: str, 
                                 limit: int = 500) -> Optional[pd.DataFrame]:
        """
        Obtém dados históricos via API pública.
        
        Args:
            symbol: Símbolo da moeda
            timeframe: Timeframe dos dados
            limit: Número de candles
            
        Returns:
            DataFrame com dados históricos
        """
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': min(limit, 1000)  # Máximo da API pública
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Converte tipos
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
                
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df.set_index('timestamp', inplace=True)
                
                trading_logger.log_info(
                    f"Dados históricos públicos obtidos: {symbol} - {len(df)} candles", 'api'
                )
                
                return df
            
            return None
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao obter dados históricos públicos: {str(e)}", e)
            return None
    
    def _start_public_websocket(self):
        """Inicia WebSocket público para dados em tempo real."""
        if self.ws_thread and self.ws_thread.is_alive():
            return
        
        def websocket_worker():
            try:
                # URL para stream múltiplo
                symbols_lower = [s.lower() for s in TradingConfig.PUBLIC_SYMBOLS[:5]]  # Limita a 5 símbolos
                streams = []
                
                for symbol in symbols_lower:
                    streams.append(f"{symbol}@ticker")
                    streams.append(f"{symbol}@kline_1m")
                
                stream_names = '/'.join(streams)
                ws_url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
                
                def on_message(ws, message):
                    try:
                        data = json.loads(message)
                        if 'stream' in data and 'data' in data:
                            self._handle_websocket_message(data)
                    except Exception as e:
                        trading_logger.log_error(f"Erro ao processar mensagem WebSocket: {str(e)}", e)
                
                def on_error(ws, error):
                    trading_logger.log_error(f"Erro WebSocket: {str(error)}")
                
                def on_close(ws, close_status_code, close_msg):
                    trading_logger.log_info("WebSocket público desconectado", 'api')
                
                def on_open(ws):
                    trading_logger.log_info("WebSocket público conectado", 'api')
                
                # Cria conexão WebSocket
                self.ws_connection = websocket.WebSocketApp(
                    ws_url,
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                
                self.ws_connection.run_forever()
                
            except Exception as e:
                trading_logger.log_error(f"Erro no WebSocket worker: {str(e)}", e)
        
        self.ws_thread = threading.Thread(target=websocket_worker, daemon=True)
        self.ws_thread.start()
    
    def _handle_websocket_message(self, data: Dict):
        """Processa mensagens do WebSocket."""
        try:
            stream = data.get('stream', '')
            stream_data = data.get('data', {})
            
            if '@ticker' in stream:
                # Dados de ticker
                symbol = stream_data.get('s')
                if symbol:
                    price_data = {
                        'symbol': symbol,
                        'price': float(stream_data.get('c', 0)),
                        'change_percent': float(stream_data.get('P', 0)),
                        'volume': float(stream_data.get('v', 0)),
                        'timestamp': datetime.now()
                    }
                    
                    self.price_cache[symbol] = price_data
                    
                    # Chama callbacks
                    for callback in self.price_callbacks:
                        try:
                            callback(price_data)
                        except Exception as e:
                            trading_logger.log_error(f"Erro em callback de preço: {str(e)}", e)
            
            elif '@kline' in stream:
                # Dados de candlestick
                kline_data = stream_data.get('k', {})
                if kline_data:
                    symbol = kline_data.get('s')
                    
                    candle = {
                        'symbol': symbol,
                        'timestamp': pd.to_datetime(kline_data.get('t'), unit='ms'),
                        'open': float(kline_data.get('o', 0)),
                        'high': float(kline_data.get('h', 0)),
                        'low': float(kline_data.get('l', 0)),
                        'close': float(kline_data.get('c', 0)),
                        'volume': float(kline_data.get('v', 0)),
                        'is_closed': kline_data.get('x', False)
                    }
                    
                    # Armazena no cache
                    if symbol not in self.kline_cache:
                        self.kline_cache[symbol] = []
                    
                    self.kline_cache[symbol].append(candle)
                    
                    # Mantém apenas os últimos 100 candles
                    if len(self.kline_cache[symbol]) > 100:
                        self.kline_cache[symbol] = self.kline_cache[symbol][-100:]
                    
                    # Chama callbacks
                    for callback in self.kline_callbacks:
                        try:
                            callback(candle)
                        except Exception as e:
                            trading_logger.log_error(f"Erro em callback de kline: {str(e)}", e)
                            
        except Exception as e:
            trading_logger.log_error(f"Erro ao processar mensagem WebSocket: {str(e)}", e)
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Obtém saldo da conta (apenas modo autenticado)."""
        if not self.is_authenticated or not self._check_credentials_timeout():
            return None
        
        try:
            start_time = time.time()
            balance = self.exchange.fetch_balance()
            response_time = time.time() - start_time
            
            trading_logger.log_api_request('fetch_balance', 'GET', 200, response_time)
            
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
    
    def add_price_callback(self, callback: Callable):
        """Adiciona callback para atualizações de preço."""
        self.price_callbacks.append(callback)
    
    def add_kline_callback(self, callback: Callable):
        """Adiciona callback para atualizações de candlestick."""
        self.kline_callbacks.append(callback)
    
    def get_cached_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém preço do cache (WebSocket)."""
        return self.price_cache.get(symbol)
    
    def get_cached_klines(self, symbol: str) -> List[Dict[str, Any]]:
        """Obtém candlesticks do cache."""
        return self.kline_cache.get(symbol, [])
    
    def disconnect(self):
        """Desconecta e limpa todos os recursos."""
        try:
            if self.ws_connection:
                self.ws_connection.close()
            
            self._clear_credentials()
            self.is_connected = False
            self.operation_mode = 'demo'
            
            # Limpa caches
            self.symbol_info_cache.clear()
            self.price_cache.clear()
            self.kline_cache.clear()
            
            # Limpa callbacks
            self.price_callbacks.clear()
            self.kline_callbacks.clear()
            
            trading_logger.log_info("Cliente Binance desconectado completamente", 'api')
            
        except Exception as e:
            trading_logger.log_error(f"Erro ao desconectar: {str(e)}", e)

# Instância global do cliente
binance_client = BinanceClient()
