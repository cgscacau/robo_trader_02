"""
=============================================================================
MÓDULO DE CONFIGURAÇÕES GLOBAIS - VERSÃO CLOUD
=============================================================================
Este módulo centraliza todas as configurações do sistema de trading,
otimizado para uso em Streamlit Cloud com segurança aprimorada.
"""

import os
from typing import Dict, List, Any

class TradingConfig:
    """
    Classe principal de configurações do sistema de trading.
    Otimizada para ambiente cloud sem armazenamento de credenciais.
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
    
    # WebSocket URLs - Incluindo streams públicos
    BINANCE_WS_URLS = {
        'public_mainnet': 'wss://stream.binance.com:9443/ws/',
        'public_testnet': 'wss://testnet.binance.vision/ws/',
        'private_mainnet': 'wss://stream.binance.com:9443/ws/',
        'private_testnet': 'wss://testnet.binance.vision/ws/',
        'futures_public': 'wss://fstream.binance.com/ws/',
        'futures_private': 'wss://fstream.binance.com/ws/'
    }
    
    # ==========================================================================
    # MODOS DE OPERAÇÃO
    # ==========================================================================
    
    OPERATION_MODES = {
        'demo': {
            'name': 'Modo Demonstração',
            'description': 'Dados públicos via WebSocket, sem autenticação',
            'requires_api': False,
            'features': ['charts', 'indicators', 'backtesting', 'optimization']
        },
        'paper_trading': {
            'name': 'Paper Trading',
            'description': 'Simulação com dados reais, sem ordens reais',
            'requires_api': True,
            'environment': 'testnet',
            'features': ['charts', 'indicators', 'backtesting', 'simulation']
        },
        'live_trading': {
            'name': 'Trading Real',
            'description': 'Operações reais com dinheiro real',
            'requires_api': True,
            'environment': 'mainnet',
            'features': ['charts', 'indicators', 'backtesting', 'real_orders']
        }
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
    
    # Símbolos disponíveis para modo demo (WebSocket público)
    PUBLIC_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT',
        'BCHUSDT', 'XLMUSDT', 'VETUSDT', 'FILUSDT', 'TRXUSDT'
    ]
    
    # ==========================================================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ==========================================================================
    
    # Timeout para requisições API (segundos)
    API_TIMEOUT = 30
    
    # Máximo de tentativas de reconexão
    MAX_RECONNECTION_ATTEMPTS = 5
    
    # Intervalo entre tentativas de reconexão (segundos)
    RECONNECTION_INTERVAL = 5
    
    # Tempo limite para manter credenciais em memória (minutos)
    CREDENTIALS_TIMEOUT = 60
    
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
        'grid': '#262730',
        'demo_mode': '#ffa500',
        'paper_mode': '#00bfff',
        'live_mode': '#ff4444'
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES DE TRADING
    # ==========================================================================
    
    # Configurações de gestão de risco padrão
    DEFAULT_RISK_SETTINGS = {
        'max_position_size_percent': 2.0,  # % do capital por posição
        'max_daily_loss_percent': 5.0,     # % máxima de perda diária
        'max_open_positions': 3,           # Número máximo de posições abertas
        'default_stop_loss_percent': 2.0,  # % padrão para stop loss
        'default_take_profit_percent': 4.0 # % padrão para take profit
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES ESPECÍFICAS PARA WEBSOCKET PÚBLICO
    # ==========================================================================
    
    # Streams WebSocket públicos disponíveis
    PUBLIC_WEBSOCKET_STREAMS = {
        'ticker': '@ticker',           # Informações de preço 24h
        'kline': '@kline_{}',         # Candlesticks por timeframe
        'depth': '@depth20@100ms',    # Order book
        'trades': '@trade',           # Trades individuais
        'miniTicker': '@miniTicker'   # Mini ticker
    }
    
    @classmethod
    def get_operation_mode_config(cls, mode: str) -> Dict[str, Any]:
        """
        Obtém configuração específica do modo de operação.
        
        Args:
            mode: Modo de operação ('demo', 'paper_trading', 'live_trading')
            
        Returns:
            Configuração do modo selecionado
        """
        return cls.OPERATION_MODES.get(mode, cls.OPERATION_MODES['demo'])
    
    @classmethod
    def validate_credentials_format(cls, api_key: str, api_secret: str) -> Dict[str, Any]:
        """
        Valida formato das credenciais sem testá-las.
        
        Args:
            api_key: Chave da API
            api_secret: Segredo da API
            
        Returns:
            Dicionário com resultado da validação
        """
        errors = []
        
        # Validação básica de formato
        if not api_key or len(api_key.strip()) < 10:
            errors.append("API Key deve ter pelo menos 10 caracteres")
        
        if not api_secret or len(api_secret.strip()) < 10:
            errors.append("API Secret deve ter pelo menos 10 caracteres")
        
        # Validação de caracteres especiais suspeitos
        if api_key and (' ' in api_key or '\n' in api_key or '\t' in api_key):
            errors.append("API Key contém espaços ou caracteres inválidos")
        
        if api_secret and (' ' in api_secret or '\n' in api_secret or '\t' in api_secret):
            errors.append("API Secret contém espaços ou caracteres inválidos")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': [] if len(errors) == 0 else ["Verifique suas credenciais cuidadosamente"]
        }
    
    @classmethod
    def get_websocket_url(cls, mode: str, symbol: str, stream_type: str, 
                         timeframe: str = None) -> str:
        """
        Gera URL do WebSocket baseada no modo e parâmetros.
        
        Args:
            mode: Modo de operação
            symbol: Símbolo da moeda
            stream_type: Tipo de stream
            timeframe: Timeframe (para kline)
            
        Returns:
            URL completa do WebSocket
        """
        base_url = cls.BINANCE_WS_URLS['public_mainnet']  # Sempre público para demo
        
        symbol_lower = symbol.lower()
        
        if stream_type == 'kline' and timeframe:
            stream = f"{symbol_lower}@kline_{timeframe}"
        else:
            stream_template = cls.PUBLIC_WEBSOCKET_STREAMS.get(stream_type, '@ticker')
            stream = f"{symbol_lower}{stream_template}"
        
        return f"{base_url}{stream}"
