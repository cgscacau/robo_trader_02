"""
=============================================================================
DASHBOARD PRINCIPAL - VERSÃO COMPLETA E CORRIGIDA
=============================================================================
Interface completa do sistema de trading com todas as funcionalidades.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
import json
import numpy as np

# Importações dos módulos do projeto - IMPORTS ABSOLUTOS CORRIGIDOS
from config.settings import TradingConfig
from api.binance_client import binance_client
from utils.logger import trading_logger

class TradingDashboard:
    """
    Dashboard completo e profissional para sistema de trading.
    Interface responsiva com todas as funcionalidades implementadas.
    """
    
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
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': 'https://github.com/your-repo/issues',
                'About': "Professional Trading Bot v1.0"
            }
        )
    
    def setup_custom_css(self):
        """CSS customizado para interface profissional"""
        st.markdown("""
        <style>
        /* Cabeçalho principal */
        .main-header {
            font-size: 2.8rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Indicadores de modo */
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
        
        /* Caixas de informação */
        .security-box {
            background: linear-gradient(135deg, #2d5a2d, #1a4a1a);
            border-left: 5px solid #00ff88;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,255,136,0.1);
        }
        
        .info-box {
            background: linear-gradient(135deg, #2d4a5a, #1a3a4a);
            border-left: 5px solid #00bfff;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,191,255,0.1);
        }
        
        .warning-box {
            background: linear-gradient(135deg, #5a4d2d, #4a3d1a);
            border-left: 5px solid #ffaa00;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(255,170,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Inicializa todas as variáveis de estado da sessão"""
        # Configurações principais
        session_defaults = {
            'operation_mode': 'demo',
            'selected_symbol': 'BTCUSDT',
            'selected_timeframe': '1h',
            'authenticated': False,
            'is_testnet': True,
            'account_type': 'spot',
            
            # Dados de mercado
            'historical_data': None,
            'current_price_data': None,
            
            # Dados da conta
            'account_balance': None,
            'open_orders': [],
            
            # Interface
            'chart_style': 'candlestick',
            'show_volume': True,
            'auto_refresh': False,
            'refresh_interval': 30,
            
            # Configurações de risco
            'risk_settings': TradingConfig.DEFAULT_RISK_SETTINGS.copy(),
            
            # Estado de inicialização
            'dashboard_initialized': False,
            'last_update': None,
            'connection_status': 'disconnected'
        }
        
        # Aplica valores padrão apenas se não existirem
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Marca como inicializado
        if not st.session_state.get('dashboard_initialized', False):
            st.session_state.dashboard_initialized = True
            st.session_state.last_update = datetime.now()
            trading_logger.log_info("Dashboard inicializado com sucesso")
    
    def safe_get_session_state(self, key: str, default=None):
        """Obtém valor do session_state de forma segura"""
        try:
            return getattr(st.session_state, key, default)
        except AttributeError:
            return default
    
    def render_header(self):
        """Renderiza cabeçalho principal com status"""
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot</h1>', 
                   unsafe_allow_html=True)
        
        # Status de conexão e modo
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
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
                auth_status = "CONECTADO" if binance_client.is_authenticated else "DESCONECTADO"
                st.markdown(f"""
                <div class="mode-paper">
                    🧪 PAPER TRADING - TESTNET<br>
                    <small>Status: {auth_status} • Simulação • Sem risco</small>
                </div>
                """, unsafe_allow_html=True)
            
            elif current_mode == 'live_trading':
                auth_status = "CONECTADO" if binance_client.is_authenticated else "DESCONECTADO"
                st.markdown(f"""
                <div class="mode-live">
                    ⚡ TRADING REAL - MAINNET<br>
                    <small>Status: {auth_status} • DINHEIRO REAL • CUIDADO!</small>
                </div>
                """, unsafe_allow_html=True)
    
    def render_mode_selection_sidebar(self):
        """Renderiza seleção de modo de operação"""
        st.sidebar.markdown("## 🎯 Modo de Operação")
        
        # Informações dos modos
        with st.sidebar.expander("ℹ️ Sobre os Modos", expanded=False):
            st.markdown("""
            **📊 Demo**
            - Dados públicos em tempo real
            - Sem necessidade de API
            - Ideal para aprendizado
            
            **🧪 Paper Trading**
            - Simulação com Testnet
            - Requer credenciais API
            - Ambiente de testes seguro
            
            **⚡ Live Trading**
            - Trading com dinheiro real
            - Requer credenciais Mainnet
            - ⚠️ **ATENÇÃO: RISCO REAL!**
            """)
        
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
        mode_options = {
            'demo': '📊 Modo Demo',
            'paper_trading': '🧪 Paper Trading',
            'live_trading': '⚡ Live Trading'
        }
        
        selected_mode = st.sidebar.selectbox(
            "Selecione o modo:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(current_mode)
        )
        
        if selected_mode != current_mode:
            st.session_state.operation_mode = selected_mode
            st.session_state.authenticated = False
            st.session_state.account_balance = None
            st.session_state.historical_data = None
            
            # Configura cliente
            binance_client.set_operation_mode(selected_mode)
            
            st.sidebar.success(f"Modo alterado para: {mode_options[selected_mode]}")
            time.sleep(1)
            st.rerun()
    
    def render_authentication_sidebar(self):
        """Renderiza painel de autenticação"""
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
        if current_mode == 'demo':
            st.sidebar.markdown("## 🔓 Sem Autenticação Necessária")
            st.sidebar.success("✅ Modo Demo Ativo")
            st.sidebar.markdown("""
            <div class="info-box">
            📡 <strong>WebSocket Público Ativo</strong><br>
            Dados em tempo real da Binance<br>
            Sem necessidade de credenciais
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.sidebar.markdown("## 🔐 Autenticação Binance")
        
        if not binance_client.is_authenticated:
            with st.sidebar.form("auth_form"):
                st.markdown("### 🔑 Credenciais API")
                
                # Aviso de segurança
                st.markdown("""
                <div class="security-box">
                🛡️ <strong>Segurança Garantida</strong><br>
                • Credenciais nunca são salvas<br>
                • Armazenamento apenas em memória<br>
                • Timeout automático em 60 minutos<br>
                • Limpeza automática ao sair
                </div>
                """, unsafe_allow_html=True)
                
                # Seleção de ambiente
                if current_mode == 'paper_trading':
                    st.info("🧪 **Ambiente Testnet** - Simulação segura")
                    is_testnet = True
                else:
                    st.warning("⚡ **Ambiente Mainnet** - DINHEIRO REAL!")
                    is_testnet = False
                
                # Tipo de conta
                account_type = st.selectbox(
                    "Tipo de Conta:",
                    ["spot", "futures"],
                    format_func=lambda x: {
                        "spot": "💰 Spot Trading",
                        "futures": "📈 Futures Trading"
                    }[x],
                    help="Spot para compra/venda normal, Futures para contratos"
                )
                
                # Campos de credenciais
                api_key = st.text_input(
                    "API Key:",
                    type="password",
                    help="Sua chave de API da Binance",
                    placeholder="Insira sua API Key..."
                )
                
                api_secret = st.text_input(
                    "API Secret:",
                    type="password",
                    help="Seu segredo de API da Binance",
                    placeholder="Insira seu API Secret..."
                )
                
                # Validação em tempo real
                if api_key or api_secret:
                    validation = TradingConfig.validate_credentials_format(api_key, api_secret)
                    if not validation['valid']:
                        for error in validation['errors']:
                            st.error(f"❌ {error}")
                    else:
                        st.success("✅ Formato das credenciais válido")
                
                # Botão de conexão
                connect_button = st.form_submit_button(
                    "🔑 Conectar",
                    use_container_width=True,
                    type="primary"
                )
                
                if connect_button:
                    if api_key and api_secret:
                        validation = TradingConfig.validate_credentials_format(api_key, api_secret)
                        
                        if validation['valid']:
                            with st.spinner("🔄 Conectando com a Binance..."):
                                result = binance_client.authenticate(
                                    api_key, api_secret, is_testnet, account_type
                                )
                            
                            if result['success']:
                                st.session_state.authenticated = True
                                st.session_state.is_testnet = is_testnet
                                st.session_state.account_type = account_type
                                
                                st.success(f"✅ {result['message']}")
                                st.info(f"⏱️ Tempo de resposta: {result['response_time']:.2f}s")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                        else:
                            st.error("⚠️ Corrija os erros de formato antes de conectar")
                    else:
                        st.error("📝 Preencha todos os campos obrigatórios")
        
        else:
            # Usuário autenticado
            st.sidebar.success("✅ Conectado com Sucesso!")
            
            if st.sidebar.button("🔓 Sair", use_container_width=True):
                binance_client.disconnect()
                st.session_state.authenticated = False
                st.session_state.account_balance = None
                st.sidebar.success("👋 Desconectado com segurança!")
                time.sleep(1)
                st.rerun()
    
    def render_trading_controls_sidebar(self):
        """Renderiza controles de trading"""
        st.sidebar.markdown("## 📊 Controles de Trading")
        
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        current_symbol = self.safe_get_session_state('selected_symbol', 'BTCUSDT')
        current_timeframe = self.safe_get_session_state('selected_timeframe', '1h')
        
        # Símbolos disponíveis
        available_symbols = TradingConfig.DEFAULT_SYMBOLS
        
        # Seleção de símbolo
        symbol = st.sidebar.selectbox(
            "💱 Símbolo:",
            available_symbols,
            index=available_symbols.index(current_symbol) if current_symbol in available_symbols else 0,
            help=f"Escolha o par de moedas para análise"
        )
        
        if symbol != current_symbol:
            st.session_state.selected_symbol = symbol
            st.session_state.historical_data = None
            st.session_state.current_price_data = None
        
        # Seleção de timeframe
        timeframe = st.sidebar.selectbox(
            "⏰ Timeframe:",
            TradingConfig.AVAILABLE_TIMEFRAMES,
            index=TradingConfig.AVAILABLE_TIMEFRAMES.index(current_timeframe),
            help="Intervalo de tempo para os candles"
        )
        
        if timeframe != current_timeframe:
            st.session_state.selected_timeframe = timeframe
            st.session_state.historical_data = None
        
        # Botões de ação
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🔄 Atualizar", use_container_width=True):
            st.session_state.historical_data = None
            st.session_state.current_price_data = None
            st.session_state.account_balance = None
            st.session_state.last_update = datetime.now()
            st.sidebar.success("✅ Atualizando...")
            st.rerun()
    
    def render_price_chart(self):
        """Renderiza gráfico de preços principal"""
        current_symbol = self.safe_get_session_state('selected_symbol', 'BTCUSDT')
        current_timeframe = self.safe_get_session_state('selected_timeframe', '1h')
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
        st.markdown(f"## 📈 {current_symbol} - {current_timeframe}")
        
        # Carrega dados se necessário
        if st.session_state.historical_data is None:
            with st.spinner("📊 Carregando dados históricos..."):
                if current_mode == 'demo':
                    st.session_state.historical_data = binance_client.get_public_historical_data(
                        current_symbol, current_timeframe, 500
                    )
                else:
                    st.session_state.historical_data = binance_client.get_historical_data(
                        current_symbol, current_timeframe, 500
                    )
                
                # Atualiza preço atual
                st.session_state.current_price_data = binance_client.get_current_price(current_symbol)
        
        df = st.session_state.historical_data
        
        if df is not None and not df.empty:
            try:
                # Cria gráfico
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    subplot_titles=(f'{current_symbol} - {current_timeframe}', 'Volume'),
                    row_heights=[0.75, 0.25]
                )
                
                # Candlestick
                candlestick = go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name="Preço",
                    increasing_line_color=TradingConfig.CHART_COLORS['bullish'],
                    decreasing_line_color=TradingConfig.CHART_COLORS['bearish']
                )
                
                fig.add_trace(candlestick, row=1, col=1)
                
                # Volume
                colors = [TradingConfig.CHART_COLORS['bearish'] if close < open 
                         else TradingConfig.CHART_COLORS['bullish'] 
                         for close, open in zip(df['close'], df['open'])]
                
                volume_bars = go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name="Volume",
                    marker_color=colors,
                    opacity=0.7,
                    showlegend=False
                )
                
                fig.add_trace(volume_bars, row=2, col=1)
                
                # Layout do gráfico
                fig.update_layout(
                    title=f"{current_symbol} - {current_timeframe}",
                    yaxis_title="Preço (USDT)",
                    yaxis2_title="Volume",
                    template="plotly_dark",
                    height=700,
                    showlegend=False,
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified'
                )
                
                fig.update_xaxes(type='date')
                
                # Exibe o gráfico
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas básicas
                self.render_basic_metrics(df)
                
            except Exception as e:
                st.error(f"❌ Erro ao criar gráfico: {str(e)}")
                trading_logger.log_error(f"Erro no gráfico: {str(e)}", e)
        
        else:
            st.error("❌ Não foi possível carregar os dados do gráfico")
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.historical_data = None
                st.rerun()
    
    def render_basic_metrics(self, df: pd.DataFrame):
        """Renderiza métricas básicas"""
        if df is None or df.empty:
            return
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
        
        high_24h = df['high'].iloc[-1]
        low_24h = df['low'].iloc[-1]
        volume_24h = df['volume'].iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Preço Atual",
                f"${current_price:.4f}",
                delta=f"{price_change:+.4f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            st.metric("📈 Máxima", f"${high_24h:.4f}")
        
        with col3:
            st.metric("📉 Mínima", f"${low_24h:.4f}")
        
        with col4:
            st.metric("📊 Volume", f"{volume_24h:,.0f}")
    
    def render_account_info(self):
        """Renderiza informações da conta"""
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
        if current_mode == 'demo':
            st.markdown("## 💰 Informações da Conta")
            st.markdown("""
            <div class="info-box">
            📊 <strong>Modo Demonstração</strong><br><br>
            As informações da conta não estão disponíveis no modo demo pois não há autenticação com a API.<br><br>
            <strong>Para acessar informações da conta:</strong><br>
            • Mude para o modo Paper Trading (Testnet)<br>
            • Ou Live Trading (Mainnet)<br>
            • Forneça suas credenciais da API Binance
            </div>
            """, unsafe_allow_html=True)
            return
        
        if not binance_client.is_authenticated:
            st.markdown("## 🔐 Autenticação Necessária")
            st.markdown("""
            <div class="warning-box">
            🔑 <strong>Conecte sua API</strong><br><br>
            Para visualizar informações da conta, você precisa estar autenticado.<br><br>
            Use o painel de autenticação na barra lateral para conectar sua API da Binance.
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("## 💰 Informações da Conta")
        
        # Carrega dados do saldo
        if st.session_state.account_balance is None:
            with st.spinner("💰 Carregando informações da conta..."):
                st.session_state.account_balance = binance_client.get_balance()
        
        balance_data = st.session_state.account_balance
        
        if balance_data:
            # Resumo principal
            total_balance = balance_data.get('total', {})
            free_balance = balance_data.get('free', {})
            used_balance = balance_data.get('used', {})
            
            # Métricas USDT
            usdt_total = total_balance.get('USDT', 0)
            usdt_free = free_balance.get('USDT', 0)
            usdt_used = used_balance.get('USDT', 0)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💵 USDT Total", f"${usdt_total:.2f}")
            
            with col2:
                st.metric("💸 USDT Livre", f"${usdt_free:.2f}")
            
            with col3:
                st.metric("🔒 USDT Usado", f"${usdt_used:.2f}")
            
            with col4:
                currencies_count = len(balance_data.get('currencies', {}))
                st.metric("🪙 Moedas", currencies_count)
            
            # Tabela de saldos
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
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.account_balance = None
                st.rerun()
    
    def render_welcome_screen(self):
        """Renderiza tela de boas-vindas"""
        st.markdown("""
        ## 🔐 Bem-vindo ao Professional Trading Bot
        
        ### 🚀 Escolha seu modo de operação:
        
        #### 📊 **Modo Demo** (Recomendado para começar)
        - ✅ **Dados em tempo real** via API pública
        - ✅ **Gráficos profissionais** 
        - ✅ **Sem necessidade de credenciais** - 100% seguro
        - ✅ **Ambiente de aprendizado** ideal para iniciantes
        - ❌ Sem acesso ao saldo da conta
        - ❌ Sem execução de ordens reais
        
        #### 🧪 **Paper Trading** (Para testes avançados)
        - ✅ **Simulação completa** com dados reais
        - ✅ **Testnet da Binance** - ambiente seguro
        - ✅ **Execução de ordens simuladas**
        - ⚠️ Requer credenciais da API (Testnet)
        
        #### ⚡ **Live Trading** (Para profissionais)
        - ✅ **Trading com dinheiro real**
        - ✅ **Todas as funcionalidades** disponíveis
        - 🚨 **ATENÇÃO: RISCO REAL DE PERDA**
        - ⚠️ Requer credenciais da API (Mainnet)
        
        ### 🛡️ **Segurança Garantida:**
        - 🔒 Credenciais **nunca são salvas** no código
        - 🔒 Armazenamento **apenas em memória** temporária
        - 🔒 **Timeout automático** em 60 minutos
        - 🔒 **Conexão direta** com a Binance
        
        ---
        
        <div class="info-box">
        💡 <strong>Dica:</strong> Comece sempre com o <strong>Modo Demo</strong> para se familiarizar com a plataforma!
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de ação rápida
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
            # Garante inicialização
            self.initialize_session_state()
            
            # Renderiza componentes principais
            self.render_header()
            self.render_mode_selection_sidebar()
            self.render_authentication_sidebar()
            self.render_trading_controls_sidebar()
            
            # Conteúdo principal baseado no modo
            current_mode = self.safe_get_session_state('operation_mode', 'demo')
            
            if current_mode == 'demo':
                # Modo demo - funcionalidades básicas
                tab1, tab2 = st.tabs(["📊 Gráficos", "ℹ️ Informações"])
                
                with tab1:
                    self.render_price_chart()
                
                with tab2:
                    self.render_account_info()
            
            elif binance_client.is_authenticated:
                # Modo autenticado - funcionalidades completas
                tab1, tab2 = st.tabs(["📊 Dashboard", "💰 Conta"])
                
                with tab1:
                    self.render_price_chart()
                
                with tab2:
                    self.render_account_info()
            
            else:
                # Aguardando autenticação
                self.render_welcome_screen()
                
        except Exception as e:
            st.error("❌ Erro crítico no sistema")
            st.exception(e)
            trading_logger.log_error(f"Erro crítico no dashboard: {str(e)}", e)
            
            if st.button("🔄 Recarregar Sistema", type="primary"):
                st.rerun()

# Instância global do dashboard - REMOVIDA PARA EVITAR CONFLITOS
# dashboard = TradingDashboard()
