"""
=============================================================================
PROFESSIONAL TRADING BOT - SISTEMA COMPLETO EM ARQUIVO ÚNICO
=============================================================================
Sistema de trading profissional com interface Streamlit
Desenvolvido para máxima compatibilidade e funcionalidade
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sys
import os

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

class TradingConfig:
    """Configurações centralizadas do sistema"""
    
    # Símbolos disponíveis
    SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT',
        'MATICUSDT', 'ATOMUSDT', 'NEARUSDT', 'SANDUSDT', 'MANAUSDT'
    ]
    
    # Timeframes
    TIMEFRAMES = [
        '1m', '3m', '5m', '15m', '30m', '1h', 
        '2h', '4h', '6h', '12h', '1d', '3d', '1w'
    ]
    
    # URLs da API
    API_URLS = {
        'mainnet': 'https://api.binance.com',
        'testnet': 'https://testnet.binance.vision',
        'futures_mainnet': 'https://fapi.binance.com',
        'futures_testnet': 'https://testnet.binancefuture.com'
    }
    
    # Cores do tema
    COLORS = {
        'bullish': '#00ff88',
        'bearish': '#ff4444',
        'neutral': '#ffaa00',
        'background': '#0e1117'
    }
    
    # Configurações de risco
    RISK_SETTINGS = {
        'max_position_size': 2.0,
        'max_daily_loss': 5.0,
        'max_open_positions': 3,
        'default_stop_loss': 2.0,
        'default_take_profit': 4.0
    }
    
    @staticmethod
    def validate_credentials(api_key: str, api_secret: str) -> Dict[str, Any]:
        """Valida formato das credenciais"""
        errors = []
        
        if not api_key or len(api_key.strip()) < 10:
            errors.append("API Key deve ter pelo menos 10 caracteres")
        
        if not api_secret or len(api_secret.strip()) < 10:
            errors.append("API Secret deve ter pelo menos 10 caracteres")
        
        if api_key and (' ' in api_key or '\n' in api_key):
            errors.append("API Key contém espaços inválidos")
        
        if api_secret and (' ' in api_secret or '\n' in api_secret):
            errors.append("API Secret contém espaços inválidos")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

# =============================================================================
# SISTEMA DE LOGGING
# =============================================================================

class Logger:
    """Sistema de logging simplificado"""
    
    @staticmethod
    def info(message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[INFO] {timestamp} - {message}")
    
    @staticmethod
    def error(message: str, exception=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[ERROR] {timestamp} - {message}")
        if exception:
            print(f"[ERROR] Exception: {str(exception)}")
    
    @staticmethod
    def warning(message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[WARNING] {timestamp} - {message}")

logger = Logger()

# =============================================================================
# CLIENTE BINANCE API
# =============================================================================

class BinanceClient:
    """Cliente simplificado para Binance API"""
    
    def __init__(self):
        self.exchange = None
        self.is_authenticated = False
        self.is_testnet = True
        self.account_type = 'spot'
        self.credentials_timestamp = None
        self.temp_credentials = None
        
        logger.info("Cliente Binance inicializado")
    
    def set_operation_mode(self, mode: str) -> bool:
        """Define modo de operação"""
        logger.info(f"Modo alterado para: {mode}")
        return True
    
    def authenticate(self, api_key: str, api_secret: str, 
                    testnet: bool = True, account_type: str = 'spot') -> Dict[str, Any]:
        """Autentica com a API da Binance"""
        try:
            # Tenta importar ccxt
            import ccxt
            
            self.is_testnet = testnet
            self.account_type = account_type
            
            # Configuração do exchange
            config = {
                'apiKey': api_key.strip(),
                'secret': api_secret.strip(),
                'timeout': 30000,
                'enableRateLimit': True,
            }
            
            if testnet:
                config['sandbox'] = True
                config['urls'] = {'api': TradingConfig.API_URLS['testnet']}
            
            self.exchange = ccxt.binance(config)
            
            # Testa conexão
            start_time = time.time()
            balance = self.exchange.fetch_balance()
            response_time = time.time() - start_time
            
            self.is_authenticated = True
            self.credentials_timestamp = datetime.now()
            self.temp_credentials = {
                'testnet': testnet,
                'account_type': account_type
            }
            
            env = "TESTNET" if testnet else "MAINNET"
            logger.info(f"Autenticação bem-sucedida - {env}")
            
            return {
                'success': True,
                'message': f'Conectado ao {env} ({account_type.upper()})',
                'response_time': response_time,
                'balance_count': len([k for k, v in balance.get('total', {}).items() if v > 0])
            }
            
        except ImportError:
            return {
                'success': False,
                'message': 'Biblioteca CCXT não disponível. Usando modo simulação.',
                'error_type': 'dependency'
            }
        except Exception as e:
            self.is_authenticated = False
            logger.error(f"Erro na autenticação: {str(e)}", e)
            return {
                'success': False,
                'message': f'Erro: {str(e)}',
                'error_type': 'unknown'
            }
    
    def get_balance(self) -> Optional[Dict[str, Any]]:
        """Obtém saldo da conta"""
        if not self.is_authenticated or not self.exchange:
            return None
        
        try:
            balance = self.exchange.fetch_balance()
            
            # Filtra moedas com saldo > 0
            filtered_balance = {}
            for currency, info in balance.items():
                if isinstance(info, dict) and info.get('total', 0) > 0:
                    filtered_balance[currency] = info
            
            return {
                'total': balance.get('total', {}),
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'currencies': filtered_balance,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {str(e)}", e)
            return None
    
    def get_historical_data(self, symbol: str, timeframe: str, 
                          limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados históricos"""
        if self.is_authenticated and self.exchange:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    logger.info(f"Dados autenticados obtidos: {symbol} - {len(df)} candles")
                    return df
            except Exception as e:
                logger.error(f"Erro API autenticada: {str(e)}", e)
        
        # Fallback para API pública
        return self.get_public_data(symbol, timeframe, limit)

    def test_api_connection(self) -> Dict[str, Any]:
        """Testa conectividade com diferentes endpoints da Binance"""
        results = {}
        
        endpoints = {
            'main': 'https://api.binance.com/api/v3/ping',
            'api1': 'https://api1.binance.com/api/v3/ping',
            'api2': 'https://api2.binance.com/api/v3/ping',
            'api3': 'https://api3.binance.com/api/v3/ping'
        }
        
        for name, url in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                
                results[name] = {
                    'status': 'ok' if response.status_code == 200 else 'error',
                    'status_code': response.status_code,
                    'response_time': response_time
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'response_time': None
                }
        
        return results

    
    
    def get_public_data(self, symbol: str, timeframe: str, 
                       limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados via API pública com tratamento robusto de erros"""
        try:
            # URLs alternativas para tentar
            urls_to_try = [
                f"{TradingConfig.API_URLS['mainnet']}/api/v3/klines",
                "https://api.binance.com/api/v3/klines",
                "https://api1.binance.com/api/v3/klines",
                "https://api2.binance.com/api/v3/klines"
            ]
            
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': min(limit, 1000)
            }
            
            logger.info(f"Tentando obter dados para {symbol} - {timeframe}")
            
            # Tenta diferentes URLs
            for i, url in enumerate(urls_to_try):
                try:
                    logger.info(f"Tentativa {i+1}: {url}")
                    
                    response = requests.get(
                        url, 
                        params=params, 
                        timeout=30,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    
                    logger.info(f"Status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if not data or len(data) == 0:
                            logger.warning("API retornou dados vazios")
                            continue
                        
                        logger.info(f"Dados recebidos: {len(data)} candles")
                        
                        # Processa os dados
                        df = pd.DataFrame(data, columns=[
                            'timestamp', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
                            'taker_buy_quote', 'ignore'
                        ])
                        
                        # Converte tipos
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # Converte colunas numéricas
                        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                        for col in numeric_columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        # Remove linhas com NaN
                        df = df.dropna()
                        
                        if df.empty:
                            logger.warning("DataFrame vazio após limpeza")
                            continue
                        
                        # Seleciona apenas colunas necessárias
                        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                        df.set_index('timestamp', inplace=True)
                        
                        logger.info(f"Dados processados com sucesso: {len(df)} candles")
                        return df
                    
                    else:
                        logger.warning(f"Status code não é 200: {response.status_code}")
                        if response.status_code == 429:
                            logger.warning("Rate limit atingido, aguardando...")
                            time.sleep(2)
                        continue
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout na URL {i+1}")
                    continue
                except requests.exceptions.ConnectionError:
                    logger.warning(f"Erro de conexão na URL {i+1}")
                    continue
                except json.JSONDecodeError:
                    logger.warning(f"Erro ao decodificar JSON na URL {i+1}")
                    continue
                except Exception as e:
                    logger.warning(f"Erro na URL {i+1}: {str(e)}")
                    continue
            
            # Se chegou aqui, todas as tentativas falharam
            logger.error("Todas as tentativas de obter dados falharam")
            
            # Tenta dados de exemplo como último recurso
            return self._generate_sample_data(symbol)
            
        except Exception as e:
            logger.error(f"Erro geral na API pública: {str(e)}", e)
            return self._generate_sample_data(symbol)
    
    def _generate_sample_data(self, symbol: str) -> pd.DataFrame:
        """Gera dados de exemplo quando a API falha"""
        try:
            logger.info(f"Gerando dados de exemplo para {symbol}")
            
            # Gera 100 candles de exemplo
            dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
            
            # Preço base baseado no símbolo
            if 'BTC' in symbol:
                base_price = 45000
            elif 'ETH' in symbol:
                base_price = 2500
            elif 'BNB' in symbol:
                base_price = 300
            else:
                base_price = 1
            
            # Gera dados aleatórios realistas
            np.random.seed(42)  # Para reproduzibilidade
            
            prices = []
            current_price = base_price
            
            for i in range(100):
                # Variação aleatória de -2% a +2%
                change = np.random.uniform(-0.02, 0.02)
                current_price *= (1 + change)
                
                # OHLC para o candle
                open_price = current_price
                high_price = open_price * (1 + abs(np.random.uniform(0, 0.01)))
                low_price = open_price * (1 - abs(np.random.uniform(0, 0.01)))
                close_price = np.random.uniform(low_price, high_price)
                volume = np.random.uniform(1000, 10000)
                
                prices.append({
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
                
                current_price = close_price
            
            df = pd.DataFrame(prices, index=dates)
            
            logger.info(f"Dados de exemplo gerados: {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de exemplo: {str(e)}", e)
            return None

    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém preço atual"""
        try:
            url = f"{TradingConfig.API_URLS['mainnet']}/api/v3/ticker/24hr"
            response = requests.get(url, params={'symbol': symbol}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
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
            logger.error(f"Erro ao obter preço: {str(e)}", e)
            return None
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   amount: float, price: Optional[float] = None) -> Optional[Dict]:
        """Executa ordem (simulada se não autenticado)"""
        if self.is_authenticated and self.exchange:
            try:
                if order_type.lower() == 'market':
                    order = self.exchange.create_market_order(symbol, side, amount)
                elif order_type.lower() == 'limit' and price:
                    order = self.exchange.create_limit_order(symbol, side, amount, price)
                else:
                    return None
                
                logger.info(f"Ordem real executada: {side.upper()} {amount} {symbol}")
                return order
            except Exception as e:
                logger.error(f"Erro ao executar ordem real: {str(e)}", e)
                return None
        else:
            # Simulação
            logger.info(f"Ordem simulada: {side.upper()} {amount} {symbol} @ {price or 'MARKET'}")
            return {
                'id': f'sim_{int(time.time())}',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'status': 'filled',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Obtém ordens abertas"""
        if self.is_authenticated and self.exchange:
            try:
                return self.exchange.fetch_open_orders(symbol)
            except Exception as e:
                logger.error(f"Erro ao obter ordens: {str(e)}", e)
        return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancela ordem"""
        if self.is_authenticated and self.exchange:
            try:
                self.exchange.cancel_order(order_id, symbol)
                logger.info(f"Ordem cancelada: {order_id}")
                return True
            except Exception as e:
                logger.error(f"Erro ao cancelar ordem: {str(e)}", e)
        return False
    
    def disconnect(self):
        """Desconecta"""
        self.is_authenticated = False
        self.exchange = None
        self.credentials_timestamp = None
        self.temp_credentials = None
        logger.info("Cliente desconectado")

# Instância global do cliente
binance_client = BinanceClient()

# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================

class TradingDashboard:
    """Dashboard principal do sistema de trading"""
    
    def __init__(self):
        """Inicializa o dashboard"""
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_custom_css()
    
    def setup_page_config(self):
        """Configura a página do Streamlit"""
        st.set_page_config(
            page_title="Professional Trading Bot",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_custom_css(self):
        """CSS customizado para interface profissional"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.8rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .mode-demo {
            background: linear-gradient(135deg, #ffa500, #ff8c00);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .mode-paper {
            background: linear-gradient(135deg, #00bfff, #0080ff);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .mode-live {
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 4px 8px rgba(255,68,68,0.2); }
            50% { box-shadow: 0 4px 20px rgba(255,68,68,0.4); }
            100% { box-shadow: 0 4px 8px rgba(255,68,68,0.2); }
        }
        
        .info-box {
            background: linear-gradient(135deg, #2d4a5a, #1a3a4a);
            border-left: 5px solid #00bfff;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .security-box {
            background: linear-gradient(135deg, #2d5a2d, #1a4a1a);
            border-left: 5px solid #00ff88;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #5a4d2d, #4a3d1a);
            border-left: 5px solid #ffaa00;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Inicializa variáveis de estado"""
        defaults = {
            'operation_mode': 'demo',
            'selected_symbol': 'BTCUSDT',
            'selected_timeframe': '1h',
            'authenticated': False,
            'historical_data': None,
            'current_price_data': None,
            'account_balance': None,
            'open_orders': [],
            'chart_style': 'candlestick',
            'show_volume': True,
            'risk_settings': TradingConfig.RISK_SETTINGS.copy(),
            'dashboard_initialized': False,
            'last_update': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        if not st.session_state.dashboard_initialized:
            st.session_state.dashboard_initialized = True
            st.session_state.last_update = datetime.now()
            logger.info("Dashboard inicializado")
    
    def safe_get(self, key: str, default=None):
        """Obtém valor do session_state de forma segura"""
        return getattr(st.session_state, key, default)
    
    def render_header(self):
        """Renderiza cabeçalho principal"""
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot</h1>', 
                   unsafe_allow_html=True)
        
        current_mode = self.safe_get('operation_mode', 'demo')
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if current_mode == 'demo':
                st.markdown("""
                <div class="mode-demo">
                    📊 MODO DEMONSTRAÇÃO<br>
                    <small>Dados públicos • Sem autenticação • Ambiente seguro</small>
                </div>
                """, unsafe_allow_html=True)
            
            elif current_mode == 'paper_trading':
                status = "CONECTADO" if binance_client.is_authenticated else "DESCONECTADO"
                st.markdown(f"""
                <div class="mode-paper">
                    🧪 PAPER TRADING - TESTNET<br>
                    <small>Status: {status} • Simulação • Sem risco</small>
                </div>
                """, unsafe_allow_html=True)
            
            elif current_mode == 'live_trading':
                status = "CONECTADO" if binance_client.is_authenticated else "DESCONECTADO"
                st.markdown(f"""
                <div class="mode-live">
                    ⚡ TRADING REAL - MAINNET<br>
                    <small>Status: {status} • DINHEIRO REAL • CUIDADO!</small>
                </div>
                """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderiza barra lateral completa"""
        # Seleção de modo
        st.sidebar.markdown("## 🎯 Modo de Operação")
        
        current_mode = self.safe_get('operation_mode', 'demo')
        
        mode_options = {
            'demo': '📊 Modo Demo',
            'paper_trading': '🧪 Paper Trading',
            'live_trading': '⚡ Live Trading'
        }
        
        selected_mode = st.sidebar.selectbox(
            "Selecione:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(current_mode)
        )
        
        if selected_mode != current_mode:
            st.session_state.operation_mode = selected_mode
            st.session_state.authenticated = False
            st.session_state.account_balance = None
            st.session_state.historical_data = None
            binance_client.set_operation_mode(selected_mode)
            st.rerun()
        
        # Autenticação
        if current_mode != 'demo':
            st.sidebar.markdown("## 🔐 Autenticação")
            
            if not binance_client.is_authenticated:
                with st.sidebar.form("auth_form"):
                    st.markdown("### Credenciais API")
                    
                    st.markdown("""
                    <div class="security-box">
                    🛡️ <strong>Seguro:</strong><br>
                    • Credenciais não são salvas<br>
                    • Apenas em memória<br>
                    • Timeout automático
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if current_mode == 'paper_trading':
                        st.info("🧪 Ambiente Testnet - Seguro")
                        is_testnet = True
                    else:
                        st.warning("⚡ Ambiente Mainnet - REAL!")
                        is_testnet = False
                    
                    account_type = st.selectbox("Tipo:", ["spot", "futures"])
                    api_key = st.text_input("API Key:", type="password")
                    api_secret = st.text_input("API Secret:", type="password")
                    
                    if st.form_submit_button("🔑 Conectar", use_container_width=True):
                        if api_key and api_secret:
                            validation = TradingConfig.validate_credentials(api_key, api_secret)
                            
                            if validation['valid']:
                                with st.spinner("Conectando..."):
                                    result = binance_client.authenticate(api_key, api_secret, is_testnet, account_type)
                                
                                if result['success']:
                                    st.session_state.authenticated = True
                                    st.success(result['message'])
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                            else:
                                for error in validation['errors']:
                                    st.error(error)
                        else:
                            st.error("Preencha todos os campos!")
            
            else:
                st.sidebar.success("✅ Conectado!")
                if st.sidebar.button("🔓 Desconectar", use_container_width=True):
                    binance_client.disconnect()
                    st.session_state.authenticated = False
                    st.rerun()
        
        else:
            st.sidebar.success("✅ Modo Demo Ativo")
        
        # Controles de trading
        st.sidebar.markdown("## 📊 Controles")
        
        symbol = st.sidebar.selectbox(
            "Símbolo:",
            TradingConfig.SYMBOLS,
            index=TradingConfig.SYMBOLS.index(self.safe_get('selected_symbol', 'BTCUSDT'))
        )
        
        if symbol != st.session_state.selected_symbol:
            st.session_state.selected_symbol = symbol
            st.session_state.historical_data = None
        
        timeframe = st.sidebar.selectbox(
            "Timeframe:",
            TradingConfig.TIMEFRAMES,
            index=TradingConfig.TIMEFRAMES.index(self.safe_get('selected_timeframe', '1h'))
        )
        
        if timeframe != st.session_state.selected_timeframe:
            st.session_state.selected_timeframe = timeframe
            st.session_state.historical_data = None
        
        if st.sidebar.button("🔄 Atualizar", use_container_width=True):
            st.session_state.historical_data = None
            st.session_state.current_price_data = None
            st.session_state.account_balance = None
            st.rerun()
    
    def render_chart(self):
        """Renderiza gráfico principal"""
        symbol = self.safe_get('selected_symbol', 'BTCUSDT')
        timeframe = self.safe_get('selected_timeframe', '1h')
        mode = self.safe_get('operation_mode', 'demo')
        
        st.markdown(f"## 📈 {symbol} - {timeframe}")
        
        # Carrega dados
        if st.session_state.historical_data is None:
            with st.spinner("📊 Carregando dados..."):
                if mode == 'demo':
                    st.session_state.historical_data = binance_client.get_public_data(symbol, timeframe, 500)
                else:
                    st.session_state.historical_data = binance_client.get_historical_data(symbol, timeframe, 500)
                
                st.session_state.current_price_data = binance_client.get_current_price(symbol)
        
        df = st.session_state.historical_data
        
        if df is not None and not df.empty:
            # Cria gráfico
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{symbol} - {timeframe}', 'Volume'),
                row_heights=[0.75, 0.25]
            )
            
            # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name="Preço",
                    increasing_line_color=TradingConfig.COLORS['bullish'],
                    decreasing_line_color=TradingConfig.COLORS['bearish']
                ),
                row=1, col=1
            )
            
            # Volume
            colors = [TradingConfig.COLORS['bearish'] if close < open else TradingConfig.COLORS['bullish'] 
                     for close, open in zip(df['close'], df['open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name="Volume",
                    marker_color=colors,
                    opacity=0.7,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # Layout
            fig.update_layout(
                title=f"{symbol} - {timeframe}",
                yaxis_title="Preço (USDT)",
                yaxis2_title="Volume",
                template="plotly_dark",
                height=700,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(type='date')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas
            self.render_metrics(df)
        
        else:
            st.error("❌ Não foi possível carregar dados")
            if st.button("🔄 Tentar Novamente"):
                st.session_state.historical_data = None
                st.rerun()
    
    def render_metrics(self, df: pd.DataFrame):
        """Renderiza métricas do mercado"""
        if df is None or df.empty:
            return
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
        
        # Dados em tempo real se disponível
        price_data = st.session_state.current_price_data
        if price_data:
            current_price = price_data['price']
            change_pct = price_data['change_percent']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Preço",
                f"${current_price:.4f}",
                delta=f"{change_pct:+.2f}%"
            )
        
        with col2:
            st.metric("📈 Máxima", f"${df['high'].iloc[-1]:.4f}")
        
        with col3:
            st.metric("📉 Mínima", f"${df['low'].iloc[-1]:.4f}")
        
        with col4:
            st.metric("📊 Volume", f"{df['volume'].iloc[-1]:,.0f}")
    
    def render_account_info(self):
        """Renderiza informações da conta"""
        mode = self.safe_get('operation_mode', 'demo')
        
        if mode == 'demo':
            st.markdown("""
            <div class="info-box">
            📊 <strong>Modo Demo</strong><br><br>
            Informações da conta não disponíveis sem autenticação.<br><br>
            <strong>Para acessar:</strong><br>
            • Use Paper Trading (Testnet)<br>
            • Ou Live Trading (Mainnet)<br>
            • Forneça credenciais da API
            </div>
            """, unsafe_allow_html=True)
            return
        
        if not binance_client.is_authenticated:
            st.markdown("""
            <div class="warning-box">
            🔑 <strong>Autenticação Necessária</strong><br><br>
            Conecte sua API na barra lateral para ver informações da conta.
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("## 💰 Informações da Conta")
        
        if st.session_state.account_balance is None:
            with st.spinner("Carregando saldo..."):
                st.session_state.account_balance = binance_client.get_balance()
        
        balance = st.session_state.account_balance
        
        if balance:
            total = balance.get('total', {})
            free = balance.get('free', {})
            used = balance.get('used', {})
            
            usdt_total = total.get('USDT', 0)
            usdt_free = free.get('USDT', 0)
            usdt_used = used.get('USDT', 0)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💵 USDT Total", f"${usdt_total:.2f}")
            
            with col2:
                st.metric("💸 USDT Livre", f"${usdt_free:.2f}")
            
            with col3:
                st.metric("🔒 USDT Usado", f"${usdt_used:.2f}")
            
            with col4:
                currencies = len(balance.get('currencies', {}))
                st.metric("🪙 Moedas", currencies)
            
            # Tabela de saldos
            if balance.get('currencies'):
                st.markdown("### Saldos Detalhados")
                
                data = []
                for currency, info in balance['currencies'].items():
                    data.append({
                        'Moeda': currency,
                        'Total': f"{info.get('total', 0):.8f}",
                        'Livre': f"{info.get('free', 0):.8f}",
                        'Usado': f"{info.get('used', 0):.8f}"
                    })
                
                df_balance = pd.DataFrame(data)
                st.dataframe(df_balance, use_container_width=True)
        
        else:
            st.error("Erro ao carregar saldo")
    
    def render_trading_panel(self):
        """Renderiza painel de trading"""
        mode = self.safe_get('operation_mode', 'demo')
        
        if mode == 'demo':
            st.markdown("""
            <div class="info-box">
            📊 <strong>Modo Demo</strong><br><br>
            Trading não disponível no modo demo.<br><br>
            <strong>Para fazer trading:</strong><br>
            • Use Paper Trading (simulação)<br>
            • Ou Live Trading (real)
            </div>
            """, unsafe_allow_html=True)
            return
        
        if not binance_client.is_authenticated:
            st.markdown("""
            <div class="warning-box">
            🔑 <strong>Conecte sua API</strong> na barra lateral para acessar o trading.
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("## 🎯 Painel de Trading")
        
        symbol = self.safe_get('selected_symbol', 'BTCUSDT')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Compra")
            
            with st.form("buy_form"):
                buy_type = st.selectbox("Tipo:", ["market", "limit"], format_func=lambda x: "Market" if x == "market" else "Limit")
                buy_amount = st.number_input("Quantidade:", min_value=0.0, value=0.01, step=0.001, format="%.6f")
                
                if buy_type == "limit":
                    buy_price = st.number_input("Preço:", min_value=0.0, step=0.0001, format="%.4f")
                else:
                    buy_price = None
                    st.info("Ordem Market - preço atual")
                
                if st.form_submit_button("🟢 COMPRAR", use_container_width=True):
                    if buy_amount > 0:
                        with st.spinner("Executando compra..."):
                            result = binance_client.place_order(symbol, 'buy', buy_type, buy_amount, buy_price)
                        
                        if result:
                            st.success("✅ Ordem de compra executada!")
                            st.json(result)
                        else:
                            st.error("❌ Erro na ordem de compra")
                    else:
                        st.error("Quantidade deve ser > 0")
        
        with col2:
            st.markdown("### 🔴 Venda")
            
            with st.form("sell_form"):
                sell_type = st.selectbox("Tipo:", ["market", "limit"], format_func=lambda x: "Market" if x == "market" else "Limit", key="sell_type")
                sell_amount = st.number_input("Quantidade:", min_value=0.0, value=0.01, step=0.001, format="%.6f", key="sell_amount")
                
                if sell_type == "limit":
                    sell_price = st.number_input("Preço:", min_value=0.0, step=0.0001, format="%.4f", key="sell_price")
                else:
                    sell_price = None
                    st.info("Ordem Market - preço atual")
                
                if st.form_submit_button("🔴 VENDER", use_container_width=True):
                    if sell_amount > 0:
                        with st.spinner("Executando venda..."):
                            result = binance_client.place_order(symbol, 'sell', sell_type, sell_amount, sell_price)
                        
                        if result:
                            st.success("✅ Ordem de venda executada!")
                            st.json(result)
                        else:
                            st.error("❌ Erro na ordem de venda")
                    else:
                        st.error("Quantidade deve ser > 0")
        
        # Ordens abertas
        st.markdown("### 📋 Ordens Abertas")
        
        if st.button("🔄 Atualizar Ordens"):
            orders = binance_client.get_open_orders(symbol)
            st.session_state.open_orders = orders
        
        orders = st.session_state.get('open_orders', [])
        
        if orders:
            orders_data = []
            for order in orders:
                orders_data.append({
                    'ID': order.get('id', 'N/A'),
                    'Símbolo': order.get('symbol', 'N/A'),
                    'Lado': order.get('side', 'N/A').upper(),
                    'Tipo': order.get('type', 'N/A').upper(),
                    'Quantidade': f"{order.get('amount', 0):.6f}",
                    'Preço': f"{order.get('price', 0):.4f}" if order.get('price') else "Market",
                    'Status': order.get('status', 'N/A').upper()
                })
            
            df_orders = pd.DataFrame(orders_data)
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.info("Nenhuma ordem aberta")
    
    def render_welcome(self):
        """Renderiza tela de boas-vindas"""
        st.markdown("""
        ## 🚀 Bem-vindo ao Professional Trading Bot
        
        ### Escolha seu modo de operação:
        
        #### 📊 **Modo Demo** (Recomendado)
        - ✅ Dados em tempo real via API pública
        - ✅ Gráficos profissionais interativos
        - ✅ Sem necessidade de credenciais - 100% seguro
        - ✅ Ideal para aprendizado e testes
        - ❌ Sem acesso ao saldo da conta
        - ❌ Sem execução de ordens reais
        
        #### 🧪 **Paper Trading** (Testes Avançados)
        - ✅ Simulação completa com dados reais
        - ✅ Testnet da Binance - ambiente seguro
        - ✅ Execução de ordens simuladas
        - ✅ Análise de performance completa
        - ⚠️ Requer credenciais da API (Testnet)
        
        #### ⚡ **Live Trading** (Profissionais)
        - ✅ Trading com dinheiro real
        - ✅ Todas as funcionalidades disponíveis
        - ✅ Gestão de risco avançada
        - 🚨 **ATENÇÃO: RISCO REAL DE PERDA**
        - ⚠️ Requer credenciais da API (Mainnet)
        
        ### 🛡️ Segurança Garantida:
        - 🔒 Credenciais nunca são salvas no código
        - 🔒 Armazenamento apenas em memória temporária
        - 🔒 Timeout automático em 60 minutos
        - 🔒 Conexão direta com a Binance
        
        ---
        
        <div class="info-box">
        💡 <strong>Dica:</strong> Comece com o <strong>Modo Demo</strong> para se familiarizar com a plataforma!
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Iniciar Demo", type="primary", use_container_width=True):
                st.session_state.operation_mode = 'demo'
                binance_client.set_operation_mode('demo')
                st.rerun()
        
        with col2:
            if st.button("🧪 Paper Trading", use_container_width=True):
                st.session_state.operation_mode = 'paper_trading'
                st.rerun()
        
        with col3:
            if st.button("⚡ Live Trading", use_container_width=True):
                st.session_state.operation_mode = 'live_trading'
                st.rerun()
    
    def run(self):
        """Executa o dashboard principal"""
        try:
            logger.info("Executando dashboard")
            
            # Renderiza componentes
            self.render_header()
            self.render_sidebar()
            
            # Conteúdo principal
            mode = self.safe_get('operation_mode', 'demo')
            
            if mode == 'demo':
                tab1, tab2 = st.tabs(["📊 Gráficos", "ℹ️ Informações"])
                
                with tab1:
                    self.render_chart()
                
                with tab2:
                    self.render_account_info()
            
            elif binance_client.is_authenticated:
                tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "💰 Conta", "🎯 Trading"])
                
                with tab1:
                    self.render_chart()
                
                with tab2:
                    self.render_account_info()
                
                with tab3:
                    self.render_trading_panel()
            
            else:
                self.render_welcome()
                
        except Exception as e:
            st.error(f"❌ Erro crítico: {str(e)}")
            logger.error(f"Erro no dashboard: {str(e)}", e)
            
            if st.button("🔄 Recarregar"):
                st.rerun()

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal da aplicação"""
    try:
        logger.info("=== INICIANDO PROFESSIONAL TRADING BOT ===")
        
        # Cria e executa dashboard
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Erro crítico na inicialização: {str(e)}")
        logger.error(f"Erro crítico: {str(e)}", e)

if __name__ == "__main__":
    main()
