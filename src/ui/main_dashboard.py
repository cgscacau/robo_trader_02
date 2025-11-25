"""
=============================================================================
DASHBOARD PRINCIPAL - INTERFACE STREAMLIT
=============================================================================
Interface principal do sistema de trading com layout profissional
e controles interativos para todas as funcionalidades.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from ..config.settings import TradingConfig
from ..api.binance_client import binance_client
from ..utils.logger import trading_logger

class TradingDashboard:
    """
    Classe principal do dashboard de trading.
    Gerencia toda a interface do usuário e interações.
    """
    
    def __init__(self):
        """Inicializa o dashboard."""
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configura a página do Streamlit."""
        st.set_page_config(**TradingConfig.STREAMLIT_CONFIG)
        
        # CSS customizado para melhor aparência
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #00ff88;
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-connected {
            background-color: #00ff88;
            color: black;
            padding: 0.5rem;
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
        }
        .status-disconnected {
            background-color: #ff4444;
            color: white;
            padding: 0.5rem;
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
        }
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #404040;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Inicializa variáveis de estado da sessão."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if 'selected_symbol' not in st.session_state:
            st.session_state.selected_symbol = 'BTCUSDT'
        
        if 'selected_timeframe' not in st.session_state:
            st.session_state.selected_timeframe = TradingConfig.DEFAULT_TIMEFRAME
        
        if 'account_balance' not in st.session_state:
            st.session_state.account_balance = None
        
        if 'historical_data' not in st.session_state:
            st.session_state.historical_data = None
    
    def render_header(self):
        """Renderiza o cabeçalho principal."""
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot</h1>', 
                   unsafe_allow_html=True)
        
        # Status de conexão
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if binance_client.is_connected:
                env_type = "TESTNET" if binance_client.is_testnet else "MAINNET"
                account_type = binance_client.account_type.upper()
                st.markdown(
                    f'<div class="status-connected">✅ CONECTADO - {env_type} - {account_type}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="status-disconnected">❌ DESCONECTADO</div>',
                    unsafe_allow_html=True
                )
    
    def render_authentication_sidebar(self):
        """Renderiza painel de autenticação na sidebar."""
        st.sidebar.markdown("## 🔐 Autenticação API")
        
        if not st.session_state.authenticated:
            with st.sidebar.form("auth_form"):
                st.markdown("### Credenciais Binance")
                
                # Seleção do ambiente
                environment = st.selectbox(
                    "Ambiente:",
                    ["Testnet (Recomendado)", "Mainnet (Produção)"],
                    help="Testnet para testes, Mainnet para operações reais"
                )
                
                # Seleção do tipo de conta
                account_type = st.selectbox(
                    "Tipo de Conta:",
                    ["Spot", "Futures"],
                    help="Spot para compra/venda normal, Futures para contratos futuros"
                )
                
                # Campos de API
                api_key = st.text_input(
                    "API Key:",
                    type="password",
                    help="Sua chave de API da Binance"
                )
                
                api_secret = st.text_input(
                    "API Secret:",
                    type="password",
                    help="Seu segredo de API da Binance"
                )
                
                # Botão de autenticação
                submit_button = st.form_submit_button("🔑 Conectar", use_container_width=True)
                
                if submit_button:
                    if api_key and api_secret:
                        is_testnet = environment == "Testnet (Recomendado)"
                        acc_type = account_type.lower()
                        
                        with st.spinner("Conectando com a Binance..."):
                            success = binance_client.authenticate(
                                api_key, api_secret, is_testnet, acc_type
                            )
                        
                        if success:
                            st.session_state.authenticated = True
                            st.success("✅ Conectado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Falha na autenticação. Verifique suas credenciais.")
                    else:
                        st.error("⚠️ Preencha todos os campos!")
        
        else:
            st.sidebar.success("✅ Autenticado com sucesso!")
            if st.sidebar.button("🔓 Desconectar", use_container_width=True):
                binance_client.disconnect()
                st.session_state.authenticated = False
                st.session_state.account_balance = None
                st.rerun()
    
    def render_trading_controls_sidebar(self):
        """Renderiza controles de trading na sidebar."""
        if not st.session_state.authenticated:
            return
        
        st.sidebar.markdown("## 📊 Controles de Trading")
        
        # Seleção de símbolo
        symbol = st.sidebar.selectbox(
            "Símbolo:",
            TradingConfig.DEFAULT_SYMBOLS,
            index=TradingConfig.DEFAULT_SYMBOLS.index(st.session_state.selected_symbol)
        )
        
        if symbol != st.session_state.selected_symbol:
            st.session_state.selected_symbol = symbol
            st.session_state.historical_data = None  # Reset data cache
        
        # Seleção de timeframe
        timeframe = st.sidebar.selectbox(
            "Timeframe:",
            TradingConfig.AVAILABLE_TIMEFRAMES,
            index=TradingConfig.AVAILABLE_TIMEFRAMES.index(st.session_state.selected_timeframe)
        )
        
        if timeframe != st.session_state.selected_timeframe:
            st.session_state.selected_timeframe = timeframe
            st.session_state.historical_data = None  # Reset data cache
        
        # Botão para atualizar dados
        if st.sidebar.button("🔄 Atualizar Dados", use_container_width=True):
            st.session_state.historical_data = None
            st.session_state.account_balance = None
            st.rerun()
    
    def render_account_info(self):
        """Renderiza informações da conta."""
        if not st.session_state.authenticated:
            st.info("🔐 Faça login para ver as informações da conta")
            return
        
        st.markdown("## 💰 Informações da Conta")
        
        # Obtém saldo se não estiver em cache
        if st.session_state.account_balance is None:
            with st.spinner("Carregando saldo da conta..."):
                st.session_state.account_balance = binance_client.get_account_balance()
        
        balance_data = st.session_state.account_balance
        
        if balance_data:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            total_balance = balance_data.get('total_balance', {})
            free_balance = balance_data.get('free_balance', {})
            
            # USDT como referência principal
            usdt_total = total_balance.get('USDT', 0)
            usdt_free = free_balance.get('USDT', 0)
            
            with col1:
                st.metric("💵 USDT Total", f"{usdt_total:.2f}")
            
            with col2:
                st.metric("💸 USDT Livre", f"{usdt_free:.2f}")
            
            with col3:
                st.metric("🔒 USDT Usado", f"{usdt_total - usdt_free:.2f}")
            
            with col4:
                currencies_count = len(balance_data.get('currencies', {}))
                st.metric("🪙 Moedas", currencies_count)
            
            # Tabela detalhada de saldos
            if balance_data.get('currencies'):
                st.markdown("### 📋 Saldos Detalhados")
                
                balance_list = []
                for currency, info in balance_data['currencies'].items():
                    balance_list.append({
                        'Moeda': currency,
                        'Total': f"{info.get('total', 0):.8f}",
                        'Livre': f"{info.get('free', 0):.8f}",
                        'Usado': f"{info.get('used', 0):.8f}"
                    })
                
                df_balance = pd.DataFrame(balance_list)
                st.dataframe(df_balance, use_container_width=True)
        
        else:
            st.error("❌ Erro ao carregar informações da conta")
    
    def render_price_chart(self):
        """Renderiza gráfico de preços."""
        if not st.session_state.authenticated:
            st.info("🔐 Faça login para ver os gráficos")
            return
        
        st.markdown(f"## 📈 Gráfico - {st.session_state.selected_symbol}")
        
        # Obtém dados históricos se não estiver em cache
        if st.session_state.historical_data is None:
            with st.spinner("Carregando dados históricos..."):
                st.session_state.historical_data = binance_client.get_historical_data(
                    st.session_state.selected_symbol,
                    st.session_state.selected_timeframe,
                    500
                )
        
        df = st.session_state.historical_data
        
        if df is not None and not df.empty:
            # Cria gráfico de candlestick
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('Preço', 'Volume'),
                row_width=[0.7, 0.3]
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
                    increasing_line_color=TradingConfig.CHART_COLORS['bullish'],
                    decreasing_line_color=TradingConfig.CHART_COLORS['bearish']
                ),
                row=1, col=1
            )
            
            # Volume
            colors = ['red' if close < open else 'green' 
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
                title=f"{st.session_state.selected_symbol} - {st.session_state.selected_timeframe}",
                yaxis_title="Preço (USDT)",
                yaxis2_title="Volume",
                template="plotly_dark",
                height=600,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(type='date')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Informações atuais
            current_price = df['close'].iloc[-1]
            price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Preço Atual", f"${current_price:.4f}")
            
            with col2:
                st.metric("📊 Variação", f"{price_change:+.2f}%")
            
            with col3:
                st.metric("📈 Máxima 24h", f"${df['high'].iloc[-1]:.4f}")
            
            with col4:
                st.metric("📉 Mínima 24h", f"${df['low'].iloc[-1]:.4f}")
        
        else:
            st.error("❌ Erro ao carregar dados do gráfico")
    
    def run(self):
        """Executa o dashboard principal."""
        # Renderiza componentes principais
        self.render_header()
        self.render_authentication_sidebar()
        self.render_trading_controls_sidebar()
        
        # Conteúdo principal
        if st.session_state.authenticated:
            # Abas principais
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💰 Conta", "⚙️ Configurações"])
            
            with tab1:
                self.render_price_chart()
            
            with tab2:
                self.render_account_info()
            
            with tab3:
                st.markdown("## ⚙️ Configurações")
                st.info("🚧 Configurações avançadas serão implementadas nas próximas sessões")
        
        else:
            # Tela de boas-vindas
            st.markdown("""
            ## 👋 Bem-vindo ao Professional Trading Bot
            
            Este é um sistema completo de trading automatizado com recursos profissionais:
            
            - 🔐 **Conexão Segura**: Integração direta com a API da Binance
            - 📊 **Gráficos Avançados**: Visualização em tempo real com indicadores técnicos
            - 🤖 **Trading Automatizado**: Estratégias personalizáveis e otimização
            - 📈 **Gestão de Risco**: Controles avançados de stop loss e take profit
            - 📱 **Interface Responsiva**: Dashboard profissional e intuitivo
            
            ### 🚀 Para começar:
            1. Insira suas credenciais da API Binance na barra lateral
            2. Escolha entre Testnet (recomendado) ou Mainnet
            3. Selecione o tipo de conta (Spot ou Futures)
            4. Clique em "Conectar"
            
            ### ⚠️ Importante:
            - Use sempre o **Testnet** primeiro para testar suas estratégias
            - Nunca compartilhe suas chaves de API
            - Mantenha suas credenciais seguras
            """)

# Instância global do dashboard
dashboard = TradingDashboard()
