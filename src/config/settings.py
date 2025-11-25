"""
=============================================================================
MÓDULO DE CONFIGURAÇÕES GLOBAIS - VERSÃO CLOUD CORRIGIDA
=============================================================================
Configurações completas e corrigidas para o sistema de trading.
"""

import os
from typing import Dict, List, Any

class TradingConfig:
    """
    Classe principal de configurações - versão corrigida e completa.
    """
    
    # ==========================================================================
    # CONFIGURAÇÕES DA API BINANCE
    # ==========================================================================
    
    BINANCE_API_URLS = {
        'mainnet': 'https://api.binance.com',
        'testnet': 'https://testnet.binance.vision',
        'futures_mainnet': 'https://fapi.binance.com',
        'futures_testnet': 'https://testnet.binancefuture.com'
    }
    
    BINANCE_WS_URLS = {
        'public_mainnet': 'wss://stream.binance.com:9443/ws/',
        'public_testnet': 'wss://testnet.binance.vision/ws/',
        'futures_public': 'wss://fstream.binance.com/ws/',
    }
    
    # ==========================================================================
    # MODOS DE OPERAÇÃO
    # ==========================================================================
    
    OPERATION_MODES = {
        'demo': {
            'name': 'Modo Demonstração',
            'description': 'Dados públicos via WebSocket, sem autenticação',
            'requires_api': False,
            'features': ['charts', 'indicators', 'backtesting']
        },
        'paper_trading': {
            'name': 'Paper Trading',
            'description': 'Simulação com dados reais, sem ordens reais',
            'requires_api': True,
            'environment': 'testnet',
            'features': ['charts', 'indicators', 'simulation']
        },
        'live_trading': {
            'name': 'Trading Real',
            'description': 'Operações reais com dinheiro real',
            'requires_api': True,
            'environment': 'mainnet',
            'features': ['charts', 'indicators', 'real_orders']
        }
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES DE TIMEFRAMES E SÍMBOLOS
    # ==========================================================================
    
    AVAILABLE_TIMEFRAMES = [
        '1m', '3m', '5m', '15m', '30m', '1h', 
        '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
    ]
    
    DEFAULT_TIMEFRAME = '1h'
    
    # Símbolos disponíveis para modo público/demo
    PUBLIC_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT',
        'BCHUSDT', 'XLMUSDT', 'VETUSDT', 'FILUSDT', 'TRXUSDT'
    ]
    
    # Símbolos padrão para modos autenticados (mesmo que público por simplicidade)
    DEFAULT_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT',
        'BCHUSDT', 'XLMUSDT', 'VETUSDT', 'FILUSDT', 'TRXUSDT',
        'MATICUSDT', 'ATOMUSDT', 'NEARUSDT', 'SANDUSDT', 'MANAUSDT'
    ]
    
    # ==========================================================================
    # CONFIGURAÇÕES DE DADOS
    # ==========================================================================
    
    MAX_HISTORICAL_CANDLES = 1000
    REALTIME_UPDATE_INTERVAL = 1
    
    # ==========================================================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ==========================================================================
    
    API_TIMEOUT = 30
    MAX_RECONNECTION_ATTEMPTS = 5
    RECONNECTION_INTERVAL = 5
    CREDENTIALS_TIMEOUT = 60
    
    # ==========================================================================
    # CONFIGURAÇÕES DA INTERFACE
    # ==========================================================================
    
    STREAMLIT_CONFIG = {
        'page_title': 'Professional Trading Bot',
        'page_icon': '📈',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
    
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
    
    DEFAULT_RISK_SETTINGS = {
        'max_position_size_percent': 2.0,
        'max_daily_loss_percent': 5.0,
        'max_open_positions': 3,
        'default_stop_loss_percent': 2.0,
        'default_take_profit_percent': 4.0
    }
    
    # ==========================================================================
    # CONFIGURAÇÕES ESPECÍFICAS PARA WEBSOCKET PÚBLICO
    # ==========================================================================
    
    PUBLIC_WEBSOCKET_STREAMS = {
        'ticker': '@ticker',
        'kline': '@kline_{}',
        'depth': '@depth20@100ms',
        'trades': '@trade',
        'miniTicker': '@miniTicker'
    }
    
    # ==========================================================================
    # MÉTODOS ESTÁTICOS
    # ==========================================================================
    
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
    def get_available_symbols(cls, mode: str) -> List[str]:
        """
        Obtém símbolos disponíveis baseado no modo.
        
        Args:
            mode: Modo de operação
            
        Returns:
            Lista de símbolos disponíveis
        """
        if mode == 'demo':
            return cls.PUBLIC_SYMBOLS
        else:
            return cls.DEFAULT_SYMBOLS
    
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
        warnings = []
        
        # Validação básica de formato
        if not api_key or len(api_key.strip()) < 10:
            errors.append("API Key deve ter pelo menos 10 caracteres")
        
        if not api_secret or len(api_secret.strip()) < 10:
            errors.append("API Secret deve ter pelo menos 10 caracteres")
        
        # Validação de caracteres especiais suspeitos
        if api_key:
            api_key_clean = api_key.strip()
            if ' ' in api_key_clean or '\n' in api_key_clean or '\t' in api_key_clean:
                errors.append("API Key contém espaços ou caracteres inválidos")
            
            # Verifica se parece com uma chave real da Binance
            if len(api_key_clean) > 0 and not api_key_clean.isalnum():
                # Chaves da Binance geralmente são alfanuméricas
                warnings.append("API Key contém caracteres especiais - verifique se está correta")
        
        if api_secret:
            api_secret_clean = api_secret.strip()
            if ' ' in api_secret_clean or '\n' in api_secret_clean or '\t' in api_secret_clean:
                errors.append("API Secret contém espaços ou caracteres inválidos")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @classmethod
    def get_websocket_url(cls, symbol: str, stream_type: str = 'ticker', 
                         timeframe: str = None) -> str:
        """
        Gera URL do WebSocket baseada nos parâmetros.
        
        Args:
            symbol: Símbolo da moeda
            stream_type: Tipo de stream ('ticker', 'kline', etc.)
            timeframe: Timeframe (para kline)
            
        Returns:
            URL completa do WebSocket
        """
        base_url = cls.BINANCE_WS_URLS['public_mainnet']
        symbol_lower = symbol.lower()
        
        if stream_type == 'kline' and timeframe:
            stream = f"{symbol_lower}@kline_{timeframe}"
        elif stream_type in cls.PUBLIC_WEBSOCKET_STREAMS:
            stream_template = cls.PUBLIC_WEBSOCKET_STREAMS[stream_type]
            if '{}' in stream_template:
                stream = f"{symbol_lower}{stream_template.format(timeframe or '1m')}"
            else:
                stream = f"{symbol_lower}{stream_template}"
        else:
            # Default para ticker
            stream = f"{symbol_lower}@ticker"
        
        return f"{base_url}{stream}"
    
    @classmethod
    def validate_symbol(cls, symbol: str, mode: str = 'demo') -> bool:
        """
        Valida se o símbolo está disponível no modo especificado.
        
        Args:
            symbol: Símbolo a validar
            mode: Modo de operação
            
        Returns:
            True se símbolo válido
        """
        available_symbols = cls.get_available_symbols(mode)
        return symbol in available_symbols
    
    @classmethod
    def validate_timeframe(cls, timeframe: str) -> bool:
        """
        Valida se o timeframe é suportado.
        
        Args:
            timeframe: Timeframe a validar
            
        Returns:
            True se timeframe válido
        """
        return timeframe in cls.AVAILABLE_TIMEFRAMES
    
    @classmethod
    def get_safe_symbol(cls, symbol: str, mode: str = 'demo') -> str:
        """
        Retorna um símbolo seguro, usando padrão se inválido.
        
        Args:
            symbol: Símbolo desejado
            mode: Modo de operação
            
        Returns:
            Símbolo válido
        """
        if cls.validate_symbol(symbol, mode):
            return symbol
        
        # Retorna primeiro símbolo disponível como padrão
        available_symbols = cls.get_available_symbols(mode)
        return available_symbols[0] if available_symbols else 'BTCUSDT'
    
    @classmethod
    def get_safe_timeframe(cls, timeframe: str) -> str:
        """
        Retorna um timeframe seguro, usando padrão se inválido.
        
        Args:
            timeframe: Timeframe desejado
            
        Returns:
            Timeframe válido
        """
        if cls.validate_timeframe(timeframe):
            return timeframe
        
        return cls.DEFAULT_TIMEFRAME
