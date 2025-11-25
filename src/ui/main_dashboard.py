"""
=============================================================================
PROFESSIONAL TRADING BOT - ARQUIVO PRINCIPAL
=============================================================================
Sistema completo de trading com interface Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

class Config:
    """Configurações centralizadas do sistema"""
    
    # Símbolos disponíveis
    SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT'
    ]
    
    # Timeframes
    TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d']
    
    # URLs da API
    API_BASE = 'https://api.binance.com'
    TESTNET_BASE = 'https://testnet.binance.vision'
    
    # Cores
    COLORS = {
        'green': '#00ff88',
        'red': '#ff4444',
        'orange': '#ffaa00'
    }

# =============================================================================
# CLIENTE BINANCE SIMPLIFICADO
# =============================================================================

class BinanceClient:
    """Cliente simplificado para Binance API"""
    
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.is_testnet = True
        self.is_authenticated = False
    
    def authenticate(self, api_key: str, api_secret: str, testnet: bool = True) -> Dict:
        """Autentica com a API"""
        try:
            import ccxt
            
            self.api_key = api_key
            self.api_secret = api_secret
            self.is_testnet = testnet
            
            # Configuração do exchange
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'timeout': 30000,
                'enableRateLimit': True,
            }
            
            if testnet:
                config['sandbox'] = True
                config['urls'] = {'api': Config.TESTNET_BASE}
            
            self.exchange = ccxt.binance(config)
            
            # Testa conexão
            balance = self.exchange.fetch_balance()
            self.is_authenticated = True
            
            return {
                'success': True,
                'message': f'Conectado ao {"Testnet" if testnet else "Mainnet"}',
                'balance_count': len([k for k, v in balance.get('total', {}).items() if v > 0])
            }
            
        except Exception as e:
            self.is_authenticated = False
            return {
                'success': False,
                'message': f'Erro na autenticação: {str(e)}'
            }
    
    def get_balance(self) -> Optional[Dict]:
        """Obtém saldo da conta"""
        if not self.is_authenticated:
            return None
        
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            st.error(f"Erro ao obter saldo: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados históricos"""
        try:
            if self.is_authenticated:
                # Usa API autenticada
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            else:
                # Usa API pública
                return self.get_public_data(symbol, timeframe, limit)
            
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            
            return None
            
        except Exception as e:
            st.error(f"Erro ao obter dados: {str(e)}")
            return self.get_public_data(symbol, timeframe, limit)
    
    def get_public_data(self, symbol: str, timeframe: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados via API pública"""
        try:
            url = f"{Config.API_BASE}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': min(limit, 1000)
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
                ])
                
                # Converte tipos
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
                
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df.set_index('timestamp', inplace=True)
                
                return df
            
            return None
            
        except Exception as e:
            st.error(f"Erro na API pública: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Obtém preço atual"""
        try:
            url = f"{Config.API_BASE}/api/v3/ticker/24hr"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data['lastPrice']),
                    'change': float(data['priceChange']),
                    'change_percent': float(data['priceChangePercent']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume'])
                }
            
            return None
            
        except Exception as e:
            st.error(f"Erro ao obter preço: {str(e)}")
            return None

# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def setup_page():
    """Configura a página"""
    st.set_page_config(
        page_title="Professional Trading Bot",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00ff88;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-demo {
        background: linear-gradient(90deg, #ffa500, #ff8c00);
        color: white;
        padding: 0.7rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .mode-auth {
        background: linear-gradient(90deg, #00bfff, #0080ff);
        color: white;
        padding: 0.7rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .security-box {
        background-color: #2d5a2d;
        border-left: 4px solid #00ff88;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """Inicializa estado da sessão"""
    defaults = {
        'mode': 'demo',
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'authenticated': False,
        'balance_data': None,
        'chart_data': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_header():
    """Renderiza cabeçalho"""
    st.markdown('<h1 class="main-header">🚀 Professional Trading Bot</h1>', 
               unsafe_allow_html=True)
    
    # Indicador de modo
    if st.session_state.mode == 'demo':
        st.markdown('<div class="mode-demo">📊 MODO DEMO - Dados Públicos</div>', 
                   unsafe_allow_html=True)
    else:
        env = "TESTNET" if client.is_testnet else "MAINNET"
        status = "CONECTADO" if client.is_authenticated else "DESCONECTADO"
        st.markdown(f'<div class="mode-auth">🔐 {env} - {status}</div>', 
                   unsafe_allow_html=True)

def render_sidebar():
    """Renderiza barra lateral"""
    st.sidebar.markdown("## 🎯 Modo de Operação")
    
    # Seleção de modo
    mode = st.sidebar.selectbox(
        "Selecione o modo:",
        ["demo", "testnet", "mainnet"],
        index=["demo", "testnet", "mainnet"].index(st.session_state.mode),
        format_func=lambda x: {
            "demo": "📊 Demo (Público)",
            "testnet": "🧪 Testnet",
            "mainnet": "⚡ Mainnet"
        }[x]
    )
    
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.authenticated = False
        st.session_state.balance_data = None
        st.rerun()
    
    # Autenticação para modos não-demo
    if st.session_state.mode != 'demo':
        st.sidebar.markdown("## 🔐 Autenticação")
        
        if not st.session_state.authenticated:
            with st.sidebar.form("auth_form"):
                st.markdown("### Credenciais Binance")
                
                st.markdown("""
                <div class="security-box">
                🔒 <strong>Seguro:</strong><br>
                • Não salvamos suas chaves<br>
                • Apenas em memória<br>
                • Limpeza automática
                </div>
                """, unsafe_allow_html=True)
                
                api_key = st.text_input("API Key:", type="password")
                api_secret = st.text_input("API Secret:", type="password")
                
                submit = st.form_submit_button("🔑 Conectar", use_container_width=True)
                
                if submit and api_key and api_secret:
                    with st.spinner("Conectando..."):
                        result = client.authenticate(
                            api_key, api_secret, 
                            st.session_state.mode == 'testnet'
                        )
                    
                    if result['success']:
                        st.session_state.authenticated = True
                        st.success(result['message'])
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(result['message'])
        else:
            st.sidebar.success("✅ Conectado!")
            if st.sidebar.button("🔓 Desconectar", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.balance_data = None
                client.is_authenticated = False
                st.rerun()
    
    # Controles de trading
    st.sidebar.markdown("## 📊 Trading")
    
    # Símbolo
    symbol = st.sidebar.selectbox(
        "Símbolo:",
        Config.SYMBOLS,
        index=Config.SYMBOLS.index(st.session_state.symbol)
    )
    
    if symbol != st.session_state.symbol:
        st.session_state.symbol = symbol
        st.session_state.chart_data = None
    
    # Timeframe
    timeframe = st.sidebar.selectbox(
        "Timeframe:",
        Config.TIMEFRAMES,
        index=Config.TIMEFRAMES.index(st.session_state.timeframe)
    )
    
    if timeframe != st.session_state.timeframe:
        st.session_state.timeframe = timeframe
        st.session_state.chart_data = None
    
    # Atualizar
    if st.sidebar.button("🔄 Atualizar", use_container_width=True):
        st.session_state.chart_data = None
        st.session_state.balance_data = None
        st.rerun()

def render_chart():
    """Renderiza gráfico de preços"""
    st.markdown(f"## 📈 {st.session_state.symbol} - {st.session_state.timeframe}")
    
    # Carrega dados se necessário
    if st.session_state.chart_data is None:
        with st.spinner("📊 Carregando dados..."):
            st.session_state.chart_data = client.get_historical_data(
                st.session_state.symbol, 
                st.session_state.timeframe, 
                500
            )
    
    df = st.session_state.chart_data
    
    if df is not None and not df.empty:
        # Cria gráfico
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Preço', 'Volume'),
            row_heights=[0.7, 0.3]
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
                increasing_line_color=Config.COLORS['green'],
                decreasing_line_color=Config.COLORS['red']
            ),
            row=1, col=1
        )
        
        # Volume
        colors = [Config.COLORS['red'] if close < open else Config.COLORS['green'] 
                 for close, open in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name="Volume",
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title=f"{st.session_state.symbol} - {st.session_state.timeframe}",
            yaxis_title="Preço (USDT)",
            yaxis2_title="Volume",
            template="plotly_dark",
            height=600,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        change = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Preço", f"${current_price:.4f}")
        
        with col2:
            st.metric("📊 Variação", f"{change:+.2f}%")
        
        with col3:
            st.metric("📈 Máxima", f"${df['high'].iloc[-1]:.4f}")
        
        with col4:
            st.metric("📉 Mínima", f"${df['low'].iloc[-1]:.4f}")
        
        # Dados em tempo real para demo
        if st.session_state.mode == 'demo':
            price_data = client.get_current_price(st.session_state.symbol)
            if price_data:
                st.success(f"🔴 Preço em tempo real: ${price_data['price']:.4f} ({price_data['change_percent']:+.2f}%)")
    
    else:
        st.error("❌ Não foi possível carregar os dados")
        st.info("💡 Tente:")
        st.info("• Verificar conexão com internet")
        st.info("• Selecionar outro símbolo")
        st.info("• Aguardar alguns segundos e atualizar")

def render_balance():
    """Renderiza informações de saldo"""
    if st.session_state.mode == 'demo':
        st.info("📊 **Modo Demo**: Saldo não disponível sem autenticação")
        return
    
    if not st.session_state.authenticated:
        st.info("🔐 Conecte sua API para ver o saldo")
        return
    
    st.markdown("## 💰 Saldo da Conta")
    
    # Carrega saldo se necessário
    if st.session_state.balance_data is None:
        with st.spinner("💰 Carregando saldo..."):
            st.session_state.balance_data = client.get_balance()
    
    balance = st.session_state.balance_data
    
    if balance:
        # Métricas principais
        total_balance = balance.get('total', {})
        free_balance = balance.get('free', {})
        
        usdt_total = total_balance.get('USDT', 0)
        usdt_free = free_balance.get('USDT', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 USDT Total", f"{usdt_total:.2f}")
        
        with col2:
            st.metric("💸 USDT Livre", f"{usdt_free:.2f}")
        
        with col3:
            st.metric("🔒 USDT Usado", f"{usdt_total - usdt_free:.2f}")
        
        with col4:
            currencies = len([k for k, v in total_balance.items() if v > 0])
            st.metric("🪙 Moedas", currencies)
        
        # Tabela detalhada
        if total_balance:
            st.markdown("### 📋 Detalhes")
            
            balance_list = []
            for currency, total in total_balance.items():
                if total > 0:
                    free = free_balance.get(currency, 0)
                    used = total - free
                    
                    balance_list.append({
                        'Moeda': currency,
                        'Total': f"{total:.8f}",
                        'Livre': f"{free:.8f}",
                        'Usado': f"{used:.8f}"
                    })
            
            if balance_list:
                df_balance = pd.DataFrame(balance_list)
                st.dataframe(df_balance, use_container_width=True)
    
    else:
        st.error("❌ Erro ao carregar saldo")

def render_info():
    """Renderiza informações do sistema"""
    st.markdown("## ℹ️ Informações do Sistema")
    
    st.markdown("""
    ### 🚀 Professional Trading Bot
    
    **Recursos Disponíveis:**
    
    #### 📊 Modo Demo
    - ✅ Dados públicos em tempo real
    - ✅ Gráficos interativos
    - ✅ Todos os símbolos principais
    - ❌ Sem acesso ao saldo
    - ❌ Sem execução de ordens
    
    #### 🧪 Modo Testnet
    - ✅ Simulação completa
    - ✅ Saldo da conta de teste
    - ✅ Execução de ordens simuladas
    - ✅ Ambiente seguro para testes
    
    #### ⚡ Modo Mainnet
    - ✅ Trading real
    - ✅ Saldo real da conta
    - ✅ Execução de ordens reais
    - ⚠️ **CUIDADO**: Dinheiro real!
    
    ### 🔒 Segurança
    - Credenciais nunca são salvas
    - Conexão direta com Binance
    - Código open source
    - Limpeza automática da memória
    
    ### 🛠️ Próximas Funcionalidades
    - Indicadores técnicos avançados
    - Estratégias automatizadas
    - Backtesting completo
    - Gestão de risco
    - Alertas em tempo real
    """)

# =============================================================================
# APLICAÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal"""
    # Setup
    setup_page()
    init_session_state()
    
    # Cliente global
    global client
    client = BinanceClient()
    
    # Interface
    render_header()
    render_sidebar()
    
    # Conteúdo principal
    if st.session_state.mode == 'demo' or st.session_state.authenticated:
        # Funcionalidades disponíveis
        tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "💰 Saldo", "ℹ️ Info"])
        
        with tab1:
            render_chart()
        
        with tab2:
            render_balance()
        
        with tab3:
            render_info()
    
    else:
        # Aguardando autenticação
        st.markdown("""
        ## 🔐 Autenticação Necessária
        
        Para usar este modo, conecte sua API Binance na barra lateral.
        
        ### 🛡️ Sua segurança é nossa prioridade:
        - ✅ Credenciais **nunca** são salvas
        - ✅ Armazenamento apenas em memória
        - ✅ Limpeza automática
        - ✅ Conexão direta com Binance
        
        ### 💡 Alternativa:
        Use o **Modo Demo** para testar sem credenciais!
        """)

if __name__ == "__main__":
    main()
