"""
=============================================================================
MÓDULO DE CONFIGURAÇÕES GLOBAIS
=============================================================================
Este módulo centraliza todas as configurações do sistema de trading,
incluindo parâmetros da API, timeframes, e configurações de segurança.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class TradingConfig:
    """
    Classe principal de configurações do sistema de trading.
    Centraliza todos os parâmetros configuráveis da aplicação.
    """
    
    # ==========================================================================
    # CONFIGURAÇÕES DA API BINANCE
    # ==========================================================================
    
    # URLs base para diferentes ambientes
    BINANCE_API_URLS = {
        'mainnet': 'https://api.binance.com',
        'testnet': 'https://testnet.binance.vision',
        'futures_mainnet': 'https://fapi.binance.com',
        'futures_testnet': 'https://testnet.binancefuture.com'
    }
    
    # WebSocket URLs
    BINANCE_WS_URLS = {
        'mainnet': 'wss://stream.binance.com:9443/ws/',
        'testnet': 'wss://testnet.binance.vision/ws/',
        'futures_mainnet': 'wss://fstream.binance.com/ws/',
        'futures_testnet': 'wss://stream.binancefuture.com/ws/'
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES DE TIMEFRAMES
    # ==========================================================================
    
    AVAILABLE_TIMEFRAMES = [
        '1m', '3m', '5m', '15m', '30m', '1h', 
        '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
    ]
    
    DEFAULT_TIMEFRAME = '1h'
    
    # ==========================================================================
    # CONFIGURAÇÕES DE DADOS
    # ==========================================================================
    
    # Quantidade máxima de candles para histórico
    MAX_HISTORICAL_CANDLES = 1000
    
    # Intervalo de atualização dos dados em tempo real (segundos)
    REALTIME_UPDATE_INTERVAL = 1
    
    # ==========================================================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ==========================================================================
    
    # Timeout para requisições API (segundos)
    API_TIMEOUT = 30
    
    # Máximo de tentativas de reconexão
    MAX_RECONNECTION_ATTEMPTS = 5
    
    # Intervalo entre tentativas de reconexão (segundos)
    RECONNECTION_INTERVAL = 5
    
    # ==========================================================================
    # CONFIGURAÇÕES DA INTERFACE
    # ==========================================================================
    
    # Configurações do Streamlit
    STREAMLIT_CONFIG = {
        'page_title': 'Professional Trading Bot',
        'page_icon': '📈',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
    
    # Cores para gráficos
    CHART_COLORS = {
        'bullish': '#00ff88',
        'bearish': '#ff4444',
        'neutral': '#ffaa00',
        'background': '#0e1117',
        'grid': '#262730'
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES DE TRADING
    # ==========================================================================
    
    # Pares de moedas padrão para monitoramento
    DEFAULT_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'LINKUSDT'
    ]
    
    # Configurações de gestão de risco padrão
    DEFAULT_RISK_SETTINGS = {
        'max_position_size_percent': 2.0,  # % do capital por posição
        'max_daily_loss_percent': 5.0,     # % máxima de perda diária
        'max_open_positions': 3,           # Número máximo de posições abertas
        'default_stop_loss_percent': 2.0,  # % padrão para stop loss
        'default_take_profit_percent': 4.0 # % padrão para take profit
    }
    
    @classmethod
    def get_api_credentials(cls) -> Dict[str, str]:
        """
        Recupera credenciais da API de variáveis de ambiente.
        
        Returns:
            Dict contendo as credenciais da API
        """
        return {
            'api_key': os.getenv('BINANCE_API_KEY', ''),
            'api_secret': os.getenv('BINANCE_API_SECRET', ''),
            'testnet_api_key': os.getenv('BINANCE_TESTNET_API_KEY', ''),
            'testnet_api_secret': os.getenv('BINANCE_TESTNET_API_SECRET', '')
        }
    
    @classmethod
    def validate_credentials(cls, credentials: Dict[str, str]) -> bool:
        """
        Valida se as credenciais estão presentes e não vazias.
        
        Args:
            credentials: Dicionário com credenciais
            
        Returns:
            True se credenciais válidas, False caso contrário
        """
        required_keys = ['api_key', 'api_secret']
        return all(credentials.get(key, '').strip() != '' for key in required_keys)
