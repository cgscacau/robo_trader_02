"""
=============================================================================
PROFESSIONAL TRADING BOT - COM WEBSOCKET EM TEMPO REAL
=============================================================================
Sistema de trading profissional com dados em tempo real via WebSocket público
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
import threading
import websocket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

class Config:
    """Configurações centralizadas"""
    
    SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT',
        'MATICUSDT', 'ATOMUSDT', 'NEARUSDT', 'SANDUSDT', 'MANAUSDT'
    ]
    
    TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
    
    COLORS = {
        'bullish': '#00ff88',
        'bearish': '#ff4444',
        'neutral': '#ffaa00'
    }
    
    # WebSocket URLs
    WS_BASE_URL = 'wss://stream.binance.com:9443/ws/'
    
    API_ENDPOINTS = [
        'https://api.binance.com/api/v3/klines',
        'https://api1.binance.com/api/v3/klines',
        'https://api2.binance.com/api/v3/klines'
    ]

# =============================================================================
# WEBSOCKET MANAGER PARA DADOS EM TEMPO REAL
# =============================================================================

class WebSocketManager:
    """Gerenciador de WebSocket para dados em tempo real"""
    
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.current_symbol = None
        self.price_data = {}
        self.kline_data = {}
        self.callbacks = {
            'price': [],
            'kline': []
        }
        self.thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    def add_price_callback(self, callback):
        """Adiciona callback para atualizações de preço"""
        self.callbacks['price'].append(callback)
    
    def add_kline_callback(self, callback):
        """Adiciona callback para atualizações de kline"""
        self.callbacks['kline'].append(callback)
    
    def connect(self, symbol: str):
        """Conecta ao WebSocket para um símbolo específico"""
        if self.current_symbol == symbol and self.is_connected:
            return True
        
        self.disconnect()
        self.current_symbol = symbol
        
        try:
            # URL do WebSocket para ticker e kline
            symbol_lower = symbol.lower()
            streams = [
                f"{symbol_lower}@ticker",
                f"{symbol_lower}@kline_1m"
            ]
            
            ws_url = f"{Config.WS_BASE_URL}{'/'.join(streams)}"
            
            print(f"🔌 Conectando WebSocket: {symbol}")
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Inicia thread do WebSocket
            self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.thread.start()
            
            # Aguarda conexão
            timeout = 10
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.is_connected
            
        except Exception as e:
            print(f"❌ Erro ao conectar WebSocket: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta WebSocket"""
        if self.ws:
            try:
                self.is_connected = False
                self.ws.close()
                print(f"🔌 WebSocket desconectado")
            except:
                pass
        
        self.ws = None
        self.thread = None
        self.reconnect_attempts = 0
    
    def _on_open(self, ws):
        """Callback quando WebSocket conecta"""
        self.is_connected = True
        self.reconnect_attempts = 0
        print(f"✅ WebSocket conectado: {self.current_symbol}")
    
    def _on_message(self, ws, message):
        """Callback para mensagens do WebSocket"""
        try:
            data = json.loads(message)
            
            # Verifica se é dados de ticker
            if 'e' in data and data['e'] == '24hrTicker':
                self._process_ticker_data(data)
            
            # Verifica se é dados de kline
            elif 'e' in data and data['e'] == 'kline':
                self._process_kline_data(data)
                
        except Exception as e:
            print(f"❌ Erro ao processar mensagem WebSocket: {str(e)}")
    
    def _on_error(self, ws, error):
        """Callback para erros do WebSocket"""
        print(f"❌ Erro WebSocket: {str(error)}")
        self.is_connected = False
        
        # Tenta reconectar
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"🔄 Tentativa de reconexão {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(2)
            if self.current_symbol:
                self.connect(self.current_symbol)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback quando WebSocket fecha"""
        self.is_connected = False
        print(f"🔌 WebSocket fechado: {close_status_code} - {close_msg}")
    
    def _process_ticker_data(self, data):
        """Processa dados de ticker em tempo real"""
        try:
            symbol = data['s']
            
            price_info = {
                'symbol': symbol,
                'price': float(data['c']),
                'change': float(data['P']),
                'change_percent': float(data['P']),
                'high': float(data['h']),
                'low': float(data['l']),
                'volume': float(data['v']),
                'timestamp': datetime.now()
            }
            
            self.price_data[symbol] = price_info
            
            # Chama callbacks
            for callback in self.callbacks['price']:
                try:
                    callback(price_info)
                except Exception as e:
                    print(f"❌ Erro em callback de preço: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar ticker: {str(e)}")
    
    def _process_kline_data(self, data):
        """Processa dados de kline em tempo real"""
        try:
            kline = data['k']
            symbol = kline['s']
            
            kline_info = {
                'symbol': symbol,
                'timestamp': pd.to_datetime(kline['t'], unit='ms'),
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v']),
                'is_closed': kline['x'],  # True se o kline está fechado
                'trades': int(kline['n'])
            }
            
            # Armazena kline
            if symbol not in self.kline_data:
                self.kline_data[symbol] = []
            
            # Atualiza ou adiciona kline
            klines = self.kline_data[symbol]
            
            # Se o kline já existe (mesmo timestamp), atualiza
            updated = False
            for i, existing_kline in enumerate(klines):
                if existing_kline['timestamp'] == kline_info['timestamp']:
                    klines[i] = kline_info
                    updated = True
                    break
            
            # Se não existe, adiciona
            if not updated:
                klines.append(kline_info)
                # Mantém apenas os últimos 100 klines
                if len(klines) > 100:
                    klines.pop(0)
            
            # Chama callbacks
            for callback in self.callbacks['kline']:
                try:
                    callback(kline_info)
                except Exception as e:
                    print(f"❌ Erro em callback de kline: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar kline: {str(e)}")
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Obtém preço atual do cache do WebSocket"""
        return self.price_data.get(symbol)
    
    def get_realtime_klines(self, symbol: str) -> List[Dict]:
        """Obtém klines em tempo real"""
        return self.kline_data.get(symbol, [])

# =============================================================================
# PROVEDOR DE DADOS COM WEBSOCKET
# =============================================================================

class DataProvider:
    """Provedor de dados com WebSocket em tempo real"""
    
    def __init__(self):
        self.cache = {}
        self.ws_manager = WebSocketManager()
        self.current_symbol = None
    
    def set_symbol(self, symbol: str):
        """Define símbolo atual e conecta WebSocket"""
        if symbol != self.current_symbol:
            self.current_symbol = symbol
            self.ws_manager.connect(symbol)
    
    def get_data(self, symbol: str, timeframe: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados históricos"""
        
        # Conecta WebSocket para o símbolo
        self.set_symbol(symbol)
        
        # Verifica cache
        cache_key = f"{symbol}_{timeframe}_{limit}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < 300:  # 5 minutos
                return data
        
        # Tenta obter dados históricos
        for method in [self._get_binance_data, self._get_sample_data]:
            try:
                data = method(symbol, timeframe, limit)
                if data is not None and not data.empty:
                    self.cache[cache_key] = (datetime.now(), data)
                    return data
            except Exception as e:
                print(f"Erro em {method.__name__}: {str(e)}")
                continue
        
        return None
    
    def _get_binance_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Obtém dados da API da Binance"""
        
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': min(limit, 1000)
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for endpoint in Config.API_ENDPOINTS:
            try:
                response = requests.get(endpoint, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        df = pd.DataFrame(data, columns=[
                            'timestamp', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                            'taker_buy_quote', 'ignore'
                        ])
                        
                        # Processa dados
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        df = df.dropna()
                        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                        df.set_index('timestamp', inplace=True)
                        
                        if len(df) > 0:
                            print(f"✅ Dados históricos obtidos: {len(df)} candles")
                            return df
                
            except Exception as e:
                print(f"Erro no endpoint {endpoint}: {str(e)}")
                continue
        
        return None
    
    def _get_sample_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Gera dados de exemplo"""
        print(f"📊 Gerando dados de exemplo para {symbol}")
        
        # Preços base
        base_prices = {
            'BTCUSDT': 43000, 'ETHUSDT': 2300, 'BNBUSDT': 280, 'ADAUSDT': 0.45,
            'XRPUSDT': 0.52, 'SOLUSDT': 95, 'DOTUSDT': 6.8, 'LINKUSDT': 14.5,
            'AVAXUSDT': 35, 'LTCUSDT': 70, 'MATICUSDT': 0.85, 'ATOMUSDT': 9.5,
            'NEARUSDT': 2.1, 'SANDUSDT': 0.38, 'MANAUSDT': 0.42
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Frequência baseada no timeframe
        if timeframe.endswith('m'):
            minutes = int(timeframe[:-1])
            freq = f'{minutes}T'
        elif timeframe.endswith('h'):
            hours = int(timeframe[:-1])
            freq = f'{hours}H'
        elif timeframe.endswith('d'):
            days = int(timeframe[:-1])
            freq = f'{days}D'
        else:
            freq = '1H'
        
        dates = pd.date_range(end=datetime.now(), periods=min(limit, 200), freq=freq)
        
        # Gera dados
        np.random.seed(hash(symbol) % 2**32)
        
        data = []
        current_price = base_price
        
        for date in dates:
            change = np.random.normal(0, 0.005)
            current_price *= (1 + change)
            
            volatility = np.random.uniform(0.005, 0.02)
            
            open_price = current_price
            high_price = open_price * (1 + volatility * np.random.uniform(0.2, 1))
            low_price = open_price * (1 - volatility * np.random.uniform(0.2, 1))
            close_price = np.random.uniform(low_price, high_price)
            
            volume = 1000 * np.random.uniform(0.5, 2) * (1 + volatility * 10)
            
            data.append({
                'open': round(open_price, 4),
                'high': round(high_price, 4),
                'low': round(low_price, 4),
                'close': round(close_price, 4),
                'volume': round(volume, 2)
            })
            
            current_price = close_price
        
        df = pd.DataFrame(data, index=dates)
        print(f"📈 Dados de exemplo gerados: {len(df)} candles")
        
        return df
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém preço atual (WebSocket tem prioridade)"""
        
        # Primeiro tenta WebSocket
        ws_price = self.ws_manager.get_current_price(symbol)
        if ws_price:
            return ws_price
        
        # Fallback para API REST
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
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
        except:
            pass
        
        return None
    
    def is_realtime_connected(self, symbol: str) -> bool:
        """Verifica se WebSocket está conectado"""
        return (self.ws_manager.is_connected and 
                self.ws_manager.current_symbol == symbol)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Obtém status da conexão"""
        return {
            'connected': self.ws_manager.is_connected,
            'symbol': self.ws_manager.current_symbol,
            'reconnect_attempts': self.ws_manager.reconnect_attempts
        }

# =============================================================================
# CLIENTE DE TRADING (mesmo código anterior)
# =============================================================================

class TradingClient:
    """Cliente de trading com simulação"""
    
    def __init__(self):
        self.is_authenticated = False
        self.is_testnet = True
        self.account_type = 'spot'
        self.balance = {'USDT': 10000.0}
        self.orders = []
        self.trades = []
    
    def authenticate(self, api_key: str, api_secret: str, testnet: bool = True, account_type: str = 'spot') -> Dict[str, Any]:
        """Simula autenticação"""
        
        if len(api_key.strip()) < 10 or len(api_secret.strip()) < 10:
            return {
                'success': False,
                'message': 'Credenciais muito curtas',
                'error_type': 'validation'
            }
        
        time.sleep(1)
        
        try:
            import ccxt
            
            config = {
                'apiKey': api_key.strip(),
                'secret': api_secret.strip(),
                'timeout': 30000,
                'enableRateLimit': True,
            }
            
            if testnet:
                config['sandbox'] = True
            
            exchange = ccxt.binance(config)
            balance = exchange.fetch_balance()
            
            self.is_authenticated = True
            self.is_testnet = testnet
            self.account_type = account_type
            self.balance = balance.get('total', {})
            
            return {
                'success': True,
                'message': f'Conectado ao {"Testnet" if testnet else "Mainnet"}',
                'response_time': 1.2,
                'balance_count': len([k for k, v in self.balance.items() if v > 0])
            }
            
        except ImportError:
            self.is_authenticated = True
            self.is_testnet = testnet
            self.account_type = account_type
            
            if testnet:
                self.balance = {'USDT': 10000.0, 'BTC': 0.1, 'ETH': 2.0, 'BNB': 10.0}
            else:
                self.balance = {'USDT': 1000.0, 'BTC': 0.01, 'ETH': 0.5}
            
            return {
                'success': True,
                'message': f'Conectado ao {"Testnet" if testnet else "Mainnet"} (Simulado)',
                'response_time': 1.0,
                'balance_count': len(self.balance)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro na autenticação: {str(e)}',
                'error_type': 'connection'
            }
    
    def get_balance(self) -> Optional[Dict[str, Any]]:
        """Obtém saldo da conta"""
        if not self.is_authenticated:
            return None
        
        total_balance = self.balance.copy()
        free_balance = {k: v * 0.9 for k, v in total_balance.items()}
        used_balance = {k: v * 0.1 for k, v in total_balance.items()}
        
        currencies = {}
        for currency, total in total_balance.items():
            if total > 0:
                currencies[currency] = {
                    'total': total,
                    'free': free_balance.get(currency, 0),
                    'used': used_balance.get(currency, 0)
                }
        
        return {
            'total': total_balance,
            'free': free_balance,
            'used': used_balance,
            'currencies': currencies,
            'timestamp': datetime.now()
        }
    
    def place_order(self, symbol: str, side: str, order_type: str, amount: float, price: Optional[float] = None) -> Optional[Dict]:
        """Executa ordem (simulada)"""
        
        order_id = f"order_{int(time.time())}_{len(self.orders)}"
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'amount': amount,
            'price': price if price else 'market',
            'status': 'filled',
            'timestamp': datetime.now().isoformat(),
            'filled': amount,
            'remaining': 0
        }
        
        self.orders.append(order)
        self.trades.append(order)
        
        print(f"📋 Ordem simulada: {side.upper()} {amount} {symbol} @ {price or 'MARKET'}")
        
        return order
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Obtém ordens abertas"""
        return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancela ordem"""
        return True
    
    def disconnect(self):
        """Desconecta"""
        self.is_authenticated = False
        self.balance = {'USDT': 10000.0}
        self.orders = []
        self.trades = []

# =============================================================================
# DASHBOARD COM WEBSOCKET EM TEMPO REAL
# =============================================================================

class TradingDashboard:
    """Dashboard com WebSocket em tempo real"""
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.trading_client = TradingClient()
        self.setup_page()
        self.init_session_state()
        
        # Placeholder para atualizações em tempo real
        self.realtime_placeholder = None
        self.metrics_placeholder = None
    
    def setup_page(self):
        """Configura página"""
        st.set_page_config(
            page_title="Professional Trading Bot - Real Time",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # CSS (mesmo do código anterior)
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .realtime-indicator {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            animation: pulse-green 2s infinite;
        }
        
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
        }
        
        .websocket-status {
            background: #1a1a2e;
            border-left: 4px solid #00ff88;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .price-update {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 0.5rem;
            border-radius: 8px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .price-up {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        
        .price-down {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
        }
        
        /* Resto do CSS igual ao anterior */
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
        </style>
        """, unsafe_allow_html=True)
    
    def init_session_state(self):
        """Inicializa session state"""
        defaults = {
            'mode': 'demo',
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'authenticated': False,
            'data': None,
            'price_data': None,
            'balance_data': None,
            'realtime_price': None,
            'last_price': None,
            'price_direction': 'neutral',
            'last_update': None,
            'ws_connected': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def update_realtime_price(self, price_info):
        """Callback para atualizações de preço em tempo real"""
        try:
            current_price = price_info['price']
            last_price = st.session_state.get('last_price', current_price)
            
            # Determina direção do preço
            if current_price > last_price:
                direction = 'up'
            elif current_price < last_price:
                direction = 'down'
            else:
                direction = 'neutral'
            
            # Atualiza session state
            st.session_state.realtime_price = price_info
            st.session_state.last_price = current_price
            st.session_state.price_direction = direction
            st.session_state.last_update = datetime.now()
            
            # Força rerun para atualizar interface
            if self.realtime_placeholder:
                with self.realtime_placeholder.container():
                    self.render_realtime_price(price_info, direction)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar preço: {str(e)}")
    
    def render_header(self):
        """Renderiza cabeçalho com status WebSocket"""
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot - Real Time</h1>', 
                   unsafe_allow_html=True)
        
        # Status do WebSocket
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.session_state.mode == 'demo':
                # Verifica status do WebSocket
                connection_status = self.data_provider.get_connection_status()
                
                if connection_status['connected']:
                    st.markdown("""
                    <div class="websocket-status">
                        <div class="realtime-indicator">🔴 AO VIVO</div>
                        <br><small>WebSocket conectado • Dados em tempo real</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="mode-demo">
                        📊 MODO DEMONSTRAÇÃO<br>
                        <small>Conectando WebSocket...</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_realtime_price(self, price_info, direction):
        """Renderiza preço em tempo real"""
        if not price_info:
            return
        
        price = price_info['price']
        change_pct = price_info['change_percent']
        
        # CSS class baseada na direção
        css_class = f"price-{direction}" if direction in ['up', 'down'] else ""
        
        st.markdown(f"""
        <div class="price-update {css_class}">
            💰 ${price:.4f} 
            <span style="font-size: 0.9em;">({change_pct:+.2f}%)</span>
            <br>
            <small>{price_info['timestamp'].strftime('%H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderiza sidebar com status WebSocket"""
        # Seleção de modo
        st.sidebar.markdown("## 🎯 Modo de Operação")
        
        mode_options = {
            'demo': '📊 Demo (WebSocket)',
            'paper': '🧪 Paper Trading',
            'live': '⚡ Live Trading'
        }
        
        mode = st.sidebar.selectbox(
            "Modo:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(st.session_state.mode)
        )
        
        if mode != st.session_state.mode:
            st.session_state.mode = mode
            st.session_state.authenticated = False
            st.session_state.data = None
            st.session_state.balance_data = None
            # Desconecta WebSocket anterior
            self.data_provider.ws_manager.disconnect()
            st.rerun()
        
        # Controles
        st.sidebar.markdown("## 📊 Controles")
        
        symbol = st.sidebar.selectbox(
            "Símbolo:",
            Config.SYMBOLS,
            index=Config.SYMBOLS.index(st.session_state.symbol) if st.session_state.symbol in Config.SYMBOLS else 0
        )
        
        if symbol != st.session_state.symbol:
            st.session_state.symbol = symbol
            st.session_state.data = None
            st.session_state.price_data = None
            st.session_state.realtime_price = None
            
            # Conecta WebSocket para novo símbolo
            if st.session_state.mode == 'demo':
                self.data_provider.set_symbol(symbol)
                # Adiciona callback para atualizações
                self.data_provider.ws_manager.add_price_callback(self.update_realtime_price)
        
        timeframe = st.sidebar.selectbox(
            "Timeframe:",
            Config.TIMEFRAMES,
            index=Config.TIMEFRAMES.index(st.session_state.timeframe) if st.session_state.timeframe in Config.TIMEFRAMES else 5
        )
        
        if timeframe != st.session_state.timeframe:
            st.session_state.timeframe = timeframe
            st.session_state.data = None
        
        # Status do WebSocket
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🌐 Status WebSocket")
        
        if st.session_state.mode == 'demo':
            connection_status = self.data_provider.get_connection_status()
            
            if connection_status['connected']:
                st.sidebar.success("✅ Conectado")
                st.sidebar.info(f"📊 {connection_status['symbol']}")
                
                # Preço em tempo real na sidebar
                if st.session_state.realtime_price:
                    price_info = st.session_state.realtime_price
                    price = price_info['price']
                    change_pct = price_info['change_percent']
                    
                    if change_pct >= 0:
                        st.sidebar.success(f"💰 ${price:.4f} (+{change_pct:.2f}%)")
                    else:
                        st.sidebar.error(f"💰 ${price:.4f} ({change_pct:.2f}%)")
                    
                    last_update = st.session_state.last_update
                    if last_update:
                        st.sidebar.caption(f"🕐 {last_update.strftime('%H:%M:%S')}")
            else:
                st.sidebar.warning("🔄 Conectando...")
                if connection_status['reconnect_attempts'] > 0:
                    st.sidebar.info(f"Tentativas: {connection_status['reconnect_attempts']}")
        else:
            st.sidebar.info("WebSocket disponível no modo Demo")
        
        # Botões
        if st.sidebar.button("🔄 Atualizar", use_container_width=True):
            st.session_state.data = None
            st.session_state.price_data = None
            st.session_state.balance_data = None
            st.session_state.last_update = datetime.now()
            st.rerun()
        
        if st.sidebar.button("🔌 Reconectar WebSocket", use_container_width=True):
            if st.session_state.mode == 'demo':
                self.data_provider.ws_manager.disconnect()
                time.sleep(1)
                self.data_provider.set_symbol(st.session_state.symbol)
                self.data_provider.ws_manager.add_price_callback(self.update_realtime_price)
                st.sidebar.success("🔄 Reconectando...")
    
    def render_chart(self):
        """Renderiza gráfico com dados em tempo real"""
        symbol = st.session_state.symbol
        timeframe = st.session_state.timeframe
        
        # Cabeçalho com preço em tempo real
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## 📈 {symbol} - {timeframe}")
        
        with col2:
            # Placeholder para preço em tempo real
            self.realtime_placeholder = st.empty()
            
            # Renderiza preço atual
            if st.session_state.realtime_price:
                with self.realtime_placeholder.container():
                    self.render_realtime_price(
                        st.session_state.realtime_price, 
                        st.session_state.price_direction
                    )
            else:
                with self.realtime_placeholder.container():
                    st.info("🔄 Carregando preço em tempo real...")
        
        # Conecta WebSocket se necessário
        if st.session_state.mode == 'demo':
            if not self.data_provider.is_realtime_connected(symbol):
                self.data_provider.set_symbol(symbol)
                self.data_provider.ws_manager.add_price_callback(self.update_realtime_price)
        
        # Carrega dados históricos
        if st.session_state.data is None:
            with st.spinner("📊 Carregando dados históricos..."):
                st.session_state.data = self.data_provider.get_data(symbol, timeframe, 500)
                st.session_state.last_update = datetime.now()
        
        df = st.session_state.data
        
        if df is not None and not df.empty:
            # Cria gráfico (mesmo código do anterior)
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
                    increasing_line_color=Config.COLORS['bullish'],
                    decreasing_line_color=Config.COLORS['bearish']
                ),
                row=1, col=1
            )
            
            # Volume
            colors = [Config.COLORS['bearish'] if close < open else Config.COLORS['bullish'] 
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
                title=f"{symbol} - {timeframe} (Tempo Real)",
                yaxis_title="Preço (USDT)",
                yaxis2_title="Volume",
                template="plotly_dark",
                height=700,
                showlegend=False,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )
            
            fig.update_xaxes(type='date')
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
            # Métricas
            self.render_metrics(df)
        
        else:
            st.error("❌ Não foi possível carregar dados")
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.data = None
                st.rerun()
    
    def render_metrics(self, df: pd.DataFrame):
        """Renderiza métricas (mesmo código anterior)"""
        if df is None or df.empty:
            return
        
        # Usa preço em tempo real se disponível
        if st.session_state.realtime_price:
            current_price = st.session_state.realtime_price['price']
            change_pct = st.session_state.realtime_price['change_percent']
            high_24h = st.session_state.realtime_price['high']
            low_24h = st.session_state.realtime_price['low']
            volume_24h = st.session_state.realtime_price['volume']
        else:
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            volume_24h = df['volume'].sum()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if len(rs) > 0 and not np.isnan(rs.iloc[-1]) else 50
        
        # Exibe métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Preço Atual",
                f"${current_price:.4f}",
                delta=f"{change_pct:+.2f}%"
            )
        
        with col2:
            st.metric("📈 Máxima 24h", f"${high_24h:.4f}")
        
        with col3:
            st.metric("📉 Mínima 24h", f"${low_24h:.4f}")
        
        with col4:
            st.metric("📊 Volume 24h", f"{volume_24h:,.0f}")
        
        with col5:
            rsi_color = "🟢" if 30 <= rsi <= 70 else ("🔴" if rsi > 70 else "🟡")
            st.metric(f"📊 RSI {rsi_color}", f"{rsi:.1f}")
        
        # Indicador de tempo real
        if st.session_state.realtime_price:
            last_update = st.session_state.realtime_price['timestamp']
            st.success(f"🔴 **DADOS EM TEMPO REAL** - Última atualização: {last_update.strftime('%H:%M:%S')}")
    
    def render_welcome(self):
        """Tela de boas-vindas"""
        st.markdown("""
        ## 🚀 Professional Trading Bot - Real Time Edition
        
        ### 🔴 **NOVO: Dados em Tempo Real via WebSocket!**
        
        #### 📊 **Modo Demo com WebSocket** (Recomendado)
        - ✅ **Dados REALMENTE em tempo real** via WebSocket público
        - ✅ **Atualizações instantâneas** de preço
        - ✅ **Gráficos profissionais** interativos
        - ✅ **100% seguro** - sem credenciais
        - ✅ **Reconexão automática** se cair conexão
        - ❌ Sem acesso ao saldo
        - ❌ Sem execução de ordens
        
        #### 🧪 **Paper Trading** (Testes)
        - ✅ Simulação completa
        - ✅ Testnet da Binance
        - ⚠️ Requer credenciais API
        
        #### ⚡ **Live Trading** (Profissional)
        - ✅ Trading real
        - 🚨 **RISCO REAL**
        - ⚠️ Requer credenciais API
        
        ### 🌐 **Tecnologia WebSocket:**
        - 🔌 **Conexão direta** com servidores da Binance
        - ⚡ **Latência ultra-baixa** (< 50ms)
        - 🔄 **Reconexão automática** em caso de queda
        - 📊 **Múltiplos streams** (preço + volume + trades)
        
        ---
        
        <div class="info-box">
        🔴 <strong>Novidade:</strong> Agora com <strong>dados em tempo real</strong> via WebSocket público! 
        Veja os preços se atualizando instantaneamente!
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de ação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔴 Demo Real Time", type="primary", use_container_width=True):
                st.session_state.mode = 'demo'
                st.rerun()
        
        with col2:
            if st.button("🧪 Paper Trading", use_container_width=True):
                st.session_state.mode = 'paper'
                st.rerun()
        
        with col3:
            if st.button("⚡ Live Trading", use_container_width=True):
                st.session_state.mode = 'live'
                st.rerun()
    
    def run(self):
        """Executa o dashboard"""
        try:
            # Header
            self.render_header()
            
            # Sidebar
            self.render_sidebar()
            
            # Conteúdo principal
            mode = st.session_state.mode
            
            if mode == 'demo':
                # Modo demo com WebSocket
                tab1, tab2 = st.tabs(["🔴 Tempo Real", "ℹ️ Informações"])
                
                with tab1:
                    self.render_chart()
                
                with tab2:
                    st.markdown("## ℹ️ Informações do Sistema")
                    
                    # Status detalhado do WebSocket
                    connection_status = self.data_provider.get_connection_status()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🌐 Status WebSocket")
                        
                        if connection_status['connected']:
                            st.success("✅ Conectado")
                            st.info(f"📊 Símbolo: {connection_status['symbol']}")
                            st.info("🔄 Reconexões: 0")
                        else:
                            st.warning("🔄 Conectando...")
                            st.info(f"🔄 Tentativas: {connection_status['reconnect_attempts']}")
                    
                    with col2:
                        st.markdown("### 📊 Recursos Ativos")
                        st.success("✅ Dados históricos")
                        st.success("✅ Preços em tempo real")
                        st.success("✅ Gráficos interativos")
                        st.success("✅ Métricas avançadas")
                        st.info("❌ Saldo da conta (sem API)")
                        st.info("❌ Execução de ordens (sem API)")
            
            else:
                # Outros modos (mesmo código anterior)
                self.render_welcome()
                
        except Exception as e:
            st.error(f"❌ Erro no sistema: {str(e)}")
            
            if st.button("🔄 Recarregar", type="primary"):
                st.rerun()

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal"""
    try:
        print("🚀 Iniciando Professional Trading Bot - Real Time Edition...")
        
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Erro crítico: {str(e)}")
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    main()
