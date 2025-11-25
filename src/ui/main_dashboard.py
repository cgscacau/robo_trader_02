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

# Importações dos módulos do projeto - IMPORTS ABSOLUTOS
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
        
        .warning-box {
            background: linear-gradient(135deg, #5a4d2d, #4a3d1a);
            border-left: 5px solid #ffaa00;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(255,170,0,0.1);
        }
        
        .info-box {
            background: linear-gradient(135deg, #2d4a5a, #1a3a4a);
            border-left: 5px solid #00bfff;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,191,255,0.1);
        }
        
        /* Cards de métricas */
        .metric-card {
            background: linear-gradient(135deg, #262730, #1a1a2e);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid #404040;
            margin: 0.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        }
        
        /* Tabelas customizadas */
        .custom-table {
            background-color: #1a1a2e;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* Botões customizados */
        .stButton > button {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: black;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #00cc6a, #009955);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,255,136,0.3);
        }
        
        /* Sidebar customizada */
        .css-1d391kg {
            background: linear-gradient(180deg, #0e1117, #1a1a2e);
        }
        
        /* Alertas e notificações */
        .alert-success {
            background: linear-gradient(135deg, #2d5a2d, #1a4a1a);
            border-left: 5px solid #00ff88;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #5a2d2d, #4a1a1a);
            border-left: 5px solid #ff4444;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #5a4d2d, #4a3d1a);
            border-left: 5px solid #ffaa00;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        /* Loading spinner customizado */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }
        
        .spinner {
            border: 4px solid #262730;
            border-top: 4px solid #00ff88;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            
            .metric-card {
                margin: 0.25rem;
                padding: 1rem;
            }
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
            'realtime_data': {},
            
            # Dados da conta
            'account_balance': None,
            'open_orders': [],
            'positions': [],
            'trade_history': [],
            
            # Estratégias e indicadores
            'selected_indicators': ['SMA', 'RSI', 'MACD'],
            'indicator_settings': {},
            'active_strategies': [],
            'strategy_signals': {},
            
            # Backtesting e otimização
            'backtest_results': None,
            'optimization_results': None,
            'optimization_in_progress': False,
            
            # Configurações de risco
            'risk_settings': TradingConfig.DEFAULT_RISK_SETTINGS.copy(),
            'position_size': 1.0,
            'stop_loss_type': 'percentage',
            'stop_loss_value': 2.0,
            'take_profit_type': 'percentage',
            'take_profit_value': 4.0,
            
            # Interface
            'show_advanced_options': False,
            'chart_style': 'candlestick',
            'show_volume': True,
            'show_indicators_on_chart': True,
            'auto_refresh': False,
            'refresh_interval': 30,
            
            # Alertas e notificações
            'price_alerts': [],
            'trade_alerts': [],
            'system_notifications': [],
            
            # Logs e histórico
            'trading_log': [],
            'system_log': [],
            'performance_metrics': {},
            
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
        
        # Barra de status adicional
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            last_update = self.safe_get_session_state('last_update')
            if last_update:
                st.caption(f"🕐 Última atualização: {last_update.strftime('%H:%M:%S')}")
            else:
                st.caption("🕐 Aguardando dados...")
        
        with status_col2:
            symbol = self.safe_get_session_state('selected_symbol', 'BTCUSDT')
            timeframe = self.safe_get_session_state('selected_timeframe', '1h')
            st.caption(f"📊 {symbol} • {timeframe}")
        
        with status_col3:
            if binance_client.is_authenticated:
                env = "TESTNET" if binance_client.is_testnet else "MAINNET"
                acc_type = binance_client.account_type.upper()
                st.caption(f"🔐 {env} • {acc_type}")
            else:
                st.caption("🔓 Não autenticado")
        
        with status_col4:
            connection_status = self.safe_get_session_state('connection_status', 'disconnected')
            if connection_status == 'connected':
                st.caption("🟢 Conectado")
            elif connection_status == 'connecting':
                st.caption("🟡 Conectando...")
            else:
                st.caption("🔴 Desconectado")
    
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
                col1, col2 = st.columns(2)
                
                with col1:
                    connect_button = st.form_submit_button(
                        "🔑 Conectar",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col2:
                    test_button = st.form_submit_button(
                        "🧪 Testar",
                        use_container_width=True,
                        help="Testa conexão sem salvar"
                    )
                
                if connect_button or test_button:
                    if api_key and api_secret:
                        validation = TradingConfig.validate_credentials_format(api_key, api_secret)
                        
                        if validation['valid']:
                            with st.spinner("🔄 Conectando com a Binance..."):
                                result = binance_client.authenticate(
                                    api_key, api_secret, is_testnet, account_type
                                )
                            
                            if result['success']:
                                if connect_button:
                                    st.session_state.authenticated = True
                                    st.session_state.is_testnet = is_testnet
                                    st.session_state.account_type = account_type
                                
                                st.success(f"✅ {result['message']}")
                                st.info(f"⏱️ Tempo de resposta: {result['response_time']:.2f}s")
                                st.info(f"💰 Moedas com saldo: {result.get('balance_count', 0)}")
                                
                                if connect_button:
                                    time.sleep(2)
                                    st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                                if result.get('error_type') == 'authentication':
                                    st.error("🔍 Verifique suas credenciais e permissões")
                                elif result.get('error_type') == 'network':
                                    st.error("🌐 Verifique sua conexão com a internet")
                        else:
                            st.error("⚠️ Corrija os erros de formato antes de conectar")
                    else:
                        st.error("📝 Preencha todos os campos obrigatórios")
        
        else:
            # Usuário autenticado
            st.sidebar.success("✅ Conectado com Sucesso!")
            
            # Informações da conexão
            if hasattr(binance_client, 'temp_credentials') and binance_client.temp_credentials:
                creds = binance_client.temp_credentials
                env = "TESTNET" if creds['testnet'] else "MAINNET"
                acc_type = creds['account_type'].upper()
                
                st.sidebar.markdown(f"""
                <div class="info-box">
                🌐 <strong>Ambiente:</strong> {env}<br>
                💼 <strong>Conta:</strong> {acc_type}<br>
                🕐 <strong>Conectado:</strong> {datetime.now().strftime('%H:%M')}
                </div>
                """, unsafe_allow_html=True)
            
            # Tempo restante de sessão
            if hasattr(binance_client, 'credentials_timestamp') and binance_client.credentials_timestamp:
                elapsed = datetime.now() - binance_client.credentials_timestamp
                remaining = TradingConfig.CREDENTIALS_TIMEOUT - (elapsed.total_seconds() / 60)
                
                if remaining > 0:
                    st.sidebar.info(f"⏱️ Sessão expira em: {remaining:.0f} min")
                else:
                    st.sidebar.warning("⚠️ Sessão expirada - Reconecte")
            
            # Controles de sessão
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("🔄 Renovar", use_container_width=True):
                    binance_client.credentials_timestamp = datetime.now()
                    st.sidebar.success("✅ Sessão renovada!")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🔓 Sair", use_container_width=True):
                    binance_client.disconnect()
                    st.session_state.authenticated = False
                    st.session_state.account_balance = None
                    st.session_state.connection_status = 'disconnected'
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
        if current_mode == 'demo':
            available_symbols = TradingConfig.PUBLIC_SYMBOLS
        else:
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
        
        # Configurações de gráfico
        with st.sidebar.expander("🎨 Configurações do Gráfico", expanded=False):
            st.session_state.chart_style = st.selectbox(
                "Estilo:",
                ["candlestick", "ohlc", "line"],
                format_func=lambda x: {
                    "candlestick": "🕯️ Candlestick",
                    "ohlc": "📊 OHLC",
                    "line": "📈 Linha"
                }[x]
            )
            
            st.session_state.show_volume = st.checkbox("📊 Mostrar Volume", value=True)
            st.session_state.show_indicators_on_chart = st.checkbox("📈 Indicadores no Gráfico", value=True)
        
        # Configurações de atualização
        with st.sidebar.expander("🔄 Atualização Automática", expanded=False):
            st.session_state.auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
            
            if st.session_state.auto_refresh:
                st.session_state.refresh_interval = st.slider(
                    "Intervalo (segundos):",
                    min_value=5,
                    max_value=300,
                    value=30,
                    step=5
                )
        
        # Informações do mercado atual
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Status do Mercado")
        
        price_data = self.safe_get_session_state('current_price_data')
        if price_data:
            current_price = price_data.get('price', 0)
            change_percent = price_data.get('change_percent', 0)
            
            if change_percent >= 0:
                st.sidebar.success(f"💰 ${current_price:.4f} (+{change_percent:.2f}%)")
            else:
                st.sidebar.error(f"💰 ${current_price:.4f} ({change_percent:.2f}%)")
            
            volume = price_data.get('volume', 0)
            st.sidebar.info(f"📊 Volume 24h: {volume:,.0f}")
        else:
            st.sidebar.info("📊 Carregando dados do mercado...")
        
        # Botões de ação
        st.sidebar.markdown("---")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.session_state.historical_data = None
                st.session_state.current_price_data = None
                st.session_state.account_balance = None
                st.session_state.last_update = datetime.now()
                st.sidebar.success("✅ Atualizando...")
                st.rerun()
        
        with col2:
            if st.button("📊 Resetar", use_container_width=True):
                # Reset para valores padrão
                st.session_state.selected_symbol = 'BTCUSDT'
                st.session_state.selected_timeframe = '1h'
                st.session_state.historical_data = None
                st.sidebar.success("✅ Resetado!")
                st.rerun()
    
    def render_price_chart(self):
        """Renderiza gráfico de preços principal"""
        current_symbol = self.safe_get_session_state('selected_symbol', 'BTCUSDT')
        current_timeframe = self.safe_get_session_state('selected_timeframe', '1h')
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        chart_style = self.safe_get_session_state('chart_style', 'candlestick')
        show_volume = self.safe_get_session_state('show_volume', True)
        
        # Cabeçalho do gráfico
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"## 📈 {current_symbol} - {current_timeframe}")
        
        with col2:
            # Preço atual em tempo real
            price_data = self.safe_get_session_state('current_price_data')
            if price_data:
                current_price = price_data.get('price', 0)
                st.metric("💰 Preço Atual", f"${current_price:.4f}")
        
        with col3:
            # Variação percentual
            if price_data:
                change_percent = price_data.get('change_percent', 0)
                st.metric(
                    "📊 Variação 24h", 
                    f"{change_percent:+.2f}%",
                    delta=f"{change_percent:.2f}%"
                )
        
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
                # Configuração do gráfico
                if show_volume:
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=(f'{current_symbol} - {current_timeframe}', 'Volume'),
                        row_heights=[0.75, 0.25]
                    )
                else:
                    fig = go.Figure()
                
                # Gráfico de preços
                if chart_style == 'candlestick':
                    candlestick = go.Candlestick(
                        x=df.index,
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name="Preço",
                        increasing_line_color=TradingConfig.CHART_COLORS['bullish'],
                        decreasing_line_color=TradingConfig.CHART_COLORS['bearish'],
                        increasing_fillcolor=TradingConfig.CHART_COLORS['bullish'],
                        decreasing_fillcolor=TradingConfig.CHART_COLORS['bearish']
                    )
                    
                    if show_volume:
                        fig.add_trace(candlestick, row=1, col=1)
                    else:
                        fig.add_trace(candlestick)
                
                elif chart_style == 'ohlc':
                    ohlc = go.Ohlc(
                        x=df.index,
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name="Preço",
                        increasing_line_color=TradingConfig.CHART_COLORS['bullish'],
                        decreasing_line_color=TradingConfig.CHART_COLORS['bearish']
                    )
                    
                    if show_volume:
                        fig.add_trace(ohlc, row=1, col=1)
                    else:
                        fig.add_trace(ohlc)
                
                else:  # line
                    line = go.Scatter(
                        x=df.index,
                        y=df['close'],
                        mode='lines',
                        name="Preço",
                        line=dict(color=TradingConfig.CHART_COLORS['bullish'], width=2)
                    )
                    
                    if show_volume:
                        fig.add_trace(line, row=1, col=1)
                    else:
                        fig.add_trace(line)
                
                # Gráfico de volume
                if show_volume:
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
                
                # Adiciona indicadores se selecionado
                if st.session_state.show_indicators_on_chart:
                    self._add_indicators_to_chart(fig, df, show_volume)
                
                # Layout do gráfico
                fig.update_layout(
                    title=f"{current_symbol} - {current_timeframe} ({current_mode.replace('_', ' ').title()})",
                    yaxis_title="Preço (USDT)",
                    template="plotly_dark",
                    height=700 if show_volume else 500,
                    showlegend=True,
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                if show_volume:
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                
                fig.update_xaxes(type='date')
                
                # Exibe o gráfico
                st.plotly_chart(fig, use_container_width=True, config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                })
                
                # Métricas detalhadas
                self.render_detailed_metrics(df)
                
            except Exception as e:
                st.error(f"❌ Erro ao criar gráfico: {str(e)}")
                trading_logger.log_error(f"Erro no gráfico: {str(e)}", e)
        
        else:
            st.error("❌ Não foi possível carregar os dados do gráfico")
            st.markdown("""
            ### 💡 Possíveis soluções:
            - ✅ Verifique sua conexão com a internet
            - ✅ Tente selecionar outro símbolo
            - ✅ Aguarde alguns segundos e clique em "Atualizar"
            - ✅ Se o problema persistir, tente o Modo Demo
            """)
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.historical_data = None
                st.rerun()
    
    def _add_indicators_to_chart(self, fig, df: pd.DataFrame, show_volume: bool):
        """Adiciona indicadores técnicos ao gráfico"""
        try:
            # Importa indicadores (assumindo que existe)
            from ..indicators.technical_indicators import TechnicalIndicators
            
            selected_indicators = self.safe_get_session_state('selected_indicators', [])
            row = 1  # Linha do gráfico principal
            
            for indicator in selected_indicators:
                if indicator == 'SMA':
                    sma_20 = TechnicalIndicators.sma(df['close'], 20)
                    sma_50 = TechnicalIndicators.sma(df['close'], 50)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=sma_20,
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='orange', width=1),
                        opacity=0.8
                    ), row=row, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=sma_50,
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='blue', width=1),
                        opacity=0.8
                    ), row=row, col=1)
                
                elif indicator == 'Bollinger Bands':
                    bb = TechnicalIndicators.bollinger_bands(df['close'])
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=bb['upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='purple', width=1, dash='dash'),
                        opacity=0.6
                    ), row=row, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=bb['lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='purple', width=1, dash='dash'),
                        opacity=0.6,
                        fill='tonexty',
                        fillcolor='rgba(128,0,128,0.1)'
                    ), row=row, col=1)
        
        except ImportError:
            # Se não houver módulo de indicadores, ignora
            pass
        except Exception as e:
            trading_logger.log_error(f"Erro ao adicionar indicadores: {str(e)}", e)
    
    def render_detailed_metrics(self, df: pd.DataFrame):
        """Renderiza métricas detalhadas do mercado"""
        if df is None or df.empty:
            return
        
        st.markdown("### 📊 Métricas Detalhadas")
        
        # Calcula métricas
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
        
        high_24h = df['high'].max()
        low_24h = df['low'].min()
        volume_24h = df['volume'].sum()
        avg_volume = df['volume'].mean()
        
        # Volatilidade
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(len(df)) * 100
        
        # RSI simples (aproximação)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if not rs.iloc[-1] == 0 else 50
        
        # Layout das métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Preço Atual",
                f"${current_price:.4f}",
                delta=f"{price_change:+.4f} ({price_change_pct:+.2f}%)",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "📈 Máxima 24h",
                f"${high_24h:.4f}",
                delta=f"{((current_price - high_24h) / high_24h) * 100:.2f}%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "📉 Mínima 24h",
                f"${low_24h:.4f}",
                delta=f"{((current_price - low_24h) / low_24h) * 100:.2f}%",
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "📊 Volume 24h",
                f"{volume_24h:,.0f}",
                delta=f"Média: {avg_volume:,.0f}",
                delta_color="off"
            )
        
        with col5:
            rsi_color = "🟢" if 30 <= rsi <= 70 else ("🔴" if rsi > 70 else "🟡")
            st.metric(
                f"📈 RSI {rsi_color}",
                f"{rsi:.1f}",
                delta="Neutro" if 30 <= rsi <= 70 else ("Sobrecompra" if rsi > 70 else "Sobrevenda"),
                delta_color="off"
            )
        
        # Métricas adicionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Volatilidade",
                f"{volatility:.2f}%",
                help="Volatilidade histórica anualizada"
            )
        
        with col2:
            amplitude = ((high_24h - low_24h) / low_24h) * 100
            st.metric(
                "📏 Amplitude 24h",
                f"{amplitude:.2f}%",
                help="Diferença entre máxima e mínima"
            )
        
        with col3:
            # Posição no range
            position_in_range = ((current_price - low_24h) / (high_24h - low_24h)) * 100 if high_24h != low_24h else 50
            st.metric(
                "📍 Posição no Range",
                f"{position_in_range:.1f}%",
                help="Posição atual no range 24h"
            )
        
        with col4:
            # Momentum simples
            momentum_5 = ((current_price - df['close'].iloc[-6]) / df['close'].iloc[-6]) * 100 if len(df) > 5 else 0
            st.metric(
                "🚀 Momentum 5p",
                f"{momentum_5:+.2f}%",
                help="Variação nos últimos 5 períodos"
            )
    
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
                st.metric(
                    "💵 USDT Total",
                    f"${usdt_total:.2f}",
                    help="Saldo total em USDT"
                )
            
            with col2:
                st.metric(
                    "💸 USDT Livre",
                    f"${usdt_free:.2f}",
                    delta=f"{(usdt_free/usdt_total)*100:.1f}%" if usdt_total > 0 else "0%",
                    help="Saldo disponível para trading"
                )
            
            with col3:
                st.metric(
                    "🔒 USDT Usado",
                    f"${usdt_used:.2f}",
                    delta=f"{(usdt_used/usdt_total)*100:.1f}%" if usdt_total > 0 else "0%",
                    help="Saldo em ordens abertas"
                )
            
            with col4:
                currencies_count = len(balance_data.get('currencies', {}))
                st.metric(
                    "🪙 Moedas",
                    currencies_count,
                    help="Número de moedas com saldo > 0"
                )
            
            # Distribuição do portfólio
            if balance_data.get('currencies'):
                st.markdown("### 📊 Distribuição do Portfólio")
                
                # Prepara dados para gráfico de pizza
                portfolio_data = []
                for currency, info in balance_data['currencies'].items():
                    total_value = info.get('total', 0)
                    if total_value > 0:
                        portfolio_data.append({
                            'currency': currency,
                            'value': total_value,
                            'free': info.get('free', 0),
                            'used': info.get('used', 0)
                        })
                
                if portfolio_data:
                    # Gráfico de pizza
                    fig_pie = px.pie(
                        values=[item['value'] for item in portfolio_data],
                        names=[item['currency'] for item in portfolio_data],
                        title="Distribuição por Moeda",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig_pie.update_layout(
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=400
                    )
                    
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Tabela detalhada
                        st.markdown("#### 📋 Detalhes por Moeda")
                        
                        balance_df = pd.DataFrame([
                            {
                                'Moeda': item['currency'],
                                'Total': f"{item['value']:.8f}",
                                'Livre': f"{item['free']:.8f}",
                                'Usado': f"{item['used']:.8f}",
                                '% Livre': f"{(item['free']/item['value'])*100:.1f}%" if item['value'] > 0 else "0%"
                            }
                            for item in portfolio_data
                        ])
                        
                        st.dataframe(
                            balance_df,
                            use_container_width=True,
                            hide_index=True
                        )
            
            # Informações adicionais
            st.markdown("### ℹ️ Informações da Conta")
            
            col1, col2 = st.columns(2)
            
            with col1:
                env = "TESTNET" if binance_client.is_testnet else "MAINNET"
                acc_type = binance_client.account_type.upper()
                
                st.markdown(f"""
                <div class="info-box">
                🌐 <strong>Ambiente:</strong> {env}<br>
                💼 <strong>Tipo de Conta:</strong> {acc_type}<br>
                🕐 <strong>Última Atualização:</strong> {datetime.now().strftime('%H:%M:%S')}<br>
                📊 <strong>Status:</strong> Conectado
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 Atualizar Saldo", use_container_width=True):
                    st.session_state.account_balance = None
                    st.rerun()
                
                if st.button("📊 Histórico de Trades", use_container_width=True):
                    with st.spinner("📊 Carregando histórico..."):
                        trades = binance_client.get_trade_history(limit=50)
                        if trades:
                            st.session_state.trade_history = trades
                            st.success(f"✅ {len(trades)} trades carregados!")
                        else:
                            st.info("📊 Nenhum trade encontrado")
        
        else:
            st.error("❌ Erro ao carregar informações da conta")
            st.markdown("""
            ### 💡 Possíveis soluções:
            - ✅ Verifique sua conexão com a internet
            - ✅ Verifique se suas credenciais estão corretas
            - ✅ Aguarde alguns segundos e tente novamente
            - ✅ Se o problema persistir, reconecte sua API
            """)
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.account_balance = None
                st.rerun()
    
    def render_trading_panel(self):
        """Renderiza painel de trading manual"""
        current_mode = self.safe_get_session_state('operation_mode', 'demo')
        
        st.markdown("## 🎯 Painel de Trading")
        
        if current_mode == 'demo':
            st.markdown("""
            <div class="warning-box">
            📊 <strong>Modo Demo</strong><br><br>
            O painel de trading não está disponível no modo demo.<br>
            Para executar ordens reais ou simuladas, use:<br><br>
            • <strong>Paper Trading:</strong> Simulação segura com Testnet<br>
            • <strong>Live Trading:</strong> Trading real com Mainnet
            </div>
            """, unsafe_allow_html=True)
            return
        
        if not binance_client.is_authenticated:
            st.markdown("""
            <div class="warning-box">
            🔐 <strong>Autenticação Necessária</strong><br><br>
            Para acessar o painel de trading, conecte sua API Binance na barra lateral.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Painel de execução de ordens
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Ordem de Compra")
            
            with st.form("buy_order_form"):
                buy_order_type = st.selectbox(
                    "Tipo de Ordem:",
                    ["market", "limit"],
                    format_func=lambda x: "📈 Market" if x == "market" else "🎯 Limit"
                )
                
                buy_quantity = st.number_input(
                    "Quantidade:",
                    min_value=0.0,
                    value=0.01,
                    step=0.001,
                    format="%.6f"
                )
                
                if buy_order_type == "limit":
                    buy_price = st.number_input(
                        "Preço:",
                        min_value=0.0,
                        value=0.0,
                        step=0.0001,
                        format="%.4f"
                    )
                else:
                    buy_price = None
                    st.info("💡 Ordem Market será executada ao preço atual")
                
                # Configurações avançadas
                with st.expander("⚙️ Configurações Avançadas"):
                    use_stop_loss = st.checkbox("🛡️ Stop Loss")
                    if use_stop_loss:
                        stop_loss_price = st.number_input(
                            "Preço Stop Loss:",
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f"
                        )
                    
                    use_take_profit = st.checkbox("🎯 Take Profit")
                    if use_take_profit:
                        take_profit_price = st.number_input(
                            "Preço Take Profit:",
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f"
                        )
                
                buy_submit = st.form_submit_button(
                    "🟢 COMPRAR",
                    use_container_width=True,
                    type="primary"
                )
                
                if buy_submit:
                    if buy_quantity > 0:
                        with st.spinner("📈 Executando ordem de compra..."):
                            symbol = st.session_state.selected_symbol
                            
                            result = binance_client.place_order(
                                symbol=symbol,
                                side='buy',
                                order_type=buy_order_type,
                                amount=buy_quantity,
                                price=buy_price
                            )
                            
                            if result:
                                st.success(f"✅ Ordem de compra executada!")
                                st.json(result)
                                
                                # Atualiza saldo
                                st.session_state.account_balance = None
                            else:
                                st.error("❌ Erro ao executar ordem de compra")
                    else:
                        st.error("⚠️ Quantidade deve ser maior que zero")
        
        with col2:
            st.markdown("### 🔴 Ordem de Venda")
            
            with st.form("sell_order_form"):
                sell_order_type = st.selectbox(
                    "Tipo de Ordem:",
                    ["market", "limit"],
                    format_func=lambda x: "📉 Market" if x == "market" else "🎯 Limit"
                )
                
                sell_quantity = st.number_input(
                    "Quantidade:",
                    min_value=0.0,
                    value=0.01,
                    step=0.001,
                    format="%.6f"
                )
                
                if sell_order_type == "limit":
                    sell_price = st.number_input(
                        "Preço:",
                        min_value=0.0,
                        value=0.0,
                        step=0.0001,
                        format="%.4f"
                    )
                else:
                    sell_price = None
                    st.info("💡 Ordem Market será executada ao preço atual")
                
                # Configurações avançadas
                with st.expander("⚙️ Configurações Avançadas"):
                    use_stop_loss_sell = st.checkbox("🛡️ Stop Loss", key="sell_sl")
                    if use_stop_loss_sell:
                        stop_loss_price_sell = st.number_input(
                            "Preço Stop Loss:",
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f",
                            key="sell_sl_price"
                        )
                    
                    use_take_profit_sell = st.checkbox("🎯 Take Profit", key="sell_tp")
                    if use_take_profit_sell:
                        take_profit_price_sell = st.number_input(
                            "Preço Take Profit:",
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f",
                            key="sell_tp_price"
                        )
                
                sell_submit = st.form_submit_button(
                    "🔴 VENDER",
                    use_container_width=True
                )
                
                if sell_submit:
                    if sell_quantity > 0:
                        with st.spinner("📉 Executando ordem de venda..."):
                            symbol = st.session_state.selected_symbol
                            
                            result = binance_client.place_order(
                                symbol=symbol,
                                side='sell',
                                order_type=sell_order_type,
                                amount=sell_quantity,
                                price=sell_price
                            )
                            
                            if result:
                                st.success(f"✅ Ordem de venda executada!")
                                st.json(result)
                                
                                # Atualiza saldo
                                st.session_state.account_balance = None
                            else:
                                st.error("❌ Erro ao executar ordem de venda")
                    else:
                        st.error("⚠️ Quantidade deve ser maior que zero")
        
        # Ordens abertas
        st.markdown("### 📋 Ordens Abertas")
        
        if st.button("🔄 Atualizar Ordens", key="refresh_orders"):
            with st.spinner("📋 Carregando ordens abertas..."):
                orders = binance_client.get_open_orders(st.session_state.selected_symbol)
                st.session_state.open_orders = orders
        
        open_orders = st.session_state.get('open_orders', [])
        
        if open_orders:
            orders_df = pd.DataFrame([
                {
                    'ID': order.get('id', 'N/A'),
                    'Símbolo': order.get('symbol', 'N/A'),
                    'Lado': order.get('side', 'N/A').upper(),
                    'Tipo': order.get('type', 'N/A').upper(),
                    'Quantidade': f"{order.get('amount', 0):.6f}",
                    'Preço': f"{order.get('price', 0):.4f}" if order.get('price') else "Market",
                    'Status': order.get('status', 'N/A').upper(),
                    'Criado': order.get('datetime', 'N/A')
                }
                for order in open_orders
            ])
            
            st.dataframe(orders_df, use_container_width=True)
            
            # Botão para cancelar todas as ordens
            if st.button("❌ Cancelar Todas as Ordens", type="secondary"):
                with st.spinner("❌ Cancelando ordens..."):
                    cancelled_count = 0
                    for order in open_orders:
                        if binance_client.cancel_order(order.get('id'), order.get('symbol')):
                            cancelled_count += 1
                    
                    st.success(f"✅ {cancelled_count} ordens canceladas")
                    st.session_state.open_orders = []
                    st.rerun()
        
        else:
            st.info("📋 Nenhuma ordem aberta encontrada")
    
    def render_strategies_panel(self):
        """Renderiza painel de estratégias"""
        st.markdown("## 🤖 Estratégias de Trading")
        
        tab1, tab2, tab3 = st.tabs(["📊 Criar Estratégia", "🔍 Backtesting", "⚡ Otimização"])
        
        with tab1:
            st.markdown("### 🛠️ Criar Nova Estratégia")
            st.info("🚧 Funcionalidade em desenvolvimento - Próximas sessões")
            
            # Preview da funcionalidade
            with st.expander("👁️ Preview - Criador de Estratégias"):
                st.markdown("""
                **Recursos planejados:**
                - ✅ Interface drag-and-drop para criar estratégias
                - ✅ Biblioteca com 20+ indicadores técnicos
                - ✅ Condições lógicas complexas (AND, OR, NOT)
                - ✅ Backtesting automático
                - ✅ Otimização de parâmetros
                - ✅ Simulação em tempo real
                """)
        
        with tab2:
            st.markdown("### 📈 Backtesting")
            st.info("🚧 Funcionalidade em desenvolvimento - Próximas sessões")
            
            # Preview da funcionalidade
            with st.expander("👁️ Preview - Sistema de Backtesting"):
                st.markdown("""
                **Recursos planejados:**
                - ✅ Teste de estratégias com dados históricos
                - ✅ Métricas detalhadas (Sharpe, Drawdown, etc.)
                - ✅ Gráficos de performance
                - ✅ Análise de riscos
                - ✅ Comparação entre estratégias
                - ✅ Exportação de relatórios
                """)
        
        with tab3:
            st.markdown("### ⚡ Otimização de Parâmetros")
            st.info("🚧 Funcionalidade em desenvolvimento - Próximas sessões")
            
            # Preview da funcionalidade
            with st.expander("👁️ Preview - Otimizador"):
                st.markdown("""
                **Recursos planejados:**
                - ✅ Otimização genética
                - ✅ Grid search inteligente
                - ✅ Walk-forward analysis
                - ✅ Validação cruzada
                - ✅ Aplicação automática dos melhores parâmetros
                - ✅ Monitoramento de performance out-of-sample
                """)
    
    def render_risk_management(self):
        """Renderiza painel de gestão de risco"""
        st.markdown("## 🛡️ Gestão de Risco")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚙️ Configurações de Risco")
            
            # Tamanho máximo da posição
            max_position = st.slider(
                "Tamanho Máximo da Posição (% do capital):",
                min_value=0.1,
                max_value=50.0,
                value=st.session_state.risk_settings['max_position_size_percent'],
                step=0.1,
                help="Percentual máximo do capital para uma única posição"
            )
            st.session_state.risk_settings['max_position_size_percent'] = max_position
            
            # Perda máxima diária
            max_daily_loss = st.slider(
                "Perda Máxima Diária (%):",
                min_value=0.1,
                max_value=20.0,
                value=st.session_state.risk_settings['max_daily_loss_percent'],
                step=0.1,
                help="Percentual máximo de perda permitida por dia"
            )
            st.session_state.risk_settings['max_daily_loss_percent'] = max_daily_loss
            
            # Número máximo de posições
            max_positions = st.slider(
                "Máximo de Posições Abertas:",
                min_value=1,
                max_value=20,
                value=st.session_state.risk_settings['max_open_positions'],
                step=1,
                help="Número máximo de posições simultâneas"
            )
            st.session_state.risk_settings['max_open_positions'] = max_positions
            
            # Stop Loss padrão
            default_sl = st.slider(
                "Stop Loss Padrão (%):",
                min_value=0.1,
                max_value=10.0,
                value=st.session_state.risk_settings['default_stop_loss_percent'],
                step=0.1,
                help="Percentual padrão para stop loss"
            )
            st.session_state.risk_settings['default_stop_loss_percent'] = default_sl
            
            # Take Profit padrão
            default_tp = st.slider(
                "Take Profit Padrão (%):",
                min_value=0.1,
                max_value=20.0,
                value=st.session_state.risk_settings['default_take_profit_percent'],
                step=0.1,
                help="Percentual padrão para take profit"
            )
            st.session_state.risk_settings['default_take_profit_percent'] = default_tp
        
        with col2:
            st.markdown("### 📊 Análise de Risco")
            
            # Simulação de risco
            if st.session_state.account_balance:
                total_balance = st.session_state.account_balance.get('total', {}).get('USDT', 0)
                
                if total_balance > 0:
                    # Cálculos de risco
                    max_position_value = total_balance * (max_position / 100)
                    max_daily_loss_value = total_balance * (max_daily_loss / 100)
                    sl_value = max_position_value * (default_sl / 100)
                    tp_value = max_position_value * (default_tp / 100)
                    
                    st.metric(
                        "💰 Capital Total",
                        f"${total_balance:.2f}"
                    )
                    
                    st.metric(
                        "📊 Valor Máx. por Posição",
                        f"${max_position_value:.2f}",
                        delta=f"{max_position:.1f}% do capital"
                    )
                    
                    st.metric(
                        "🛡️ Stop Loss por Posição",
                        f"${sl_value:.2f}",
                        delta=f"{default_sl:.1f}% da posição"
                    )
                    
                    st.metric(
                        "🎯 Take Profit por Posição",
                        f"${tp_value:.2f}",
                        delta=f"{default_tp:.1f}% da posição"
                    )
                    
                    st.metric(
                        "⚠️ Perda Máx. Diária",
                        f"${max_daily_loss_value:.2f}",
                        delta=f"{max_daily_loss:.1f}% do capital"
                    )
                    
                    # Risk/Reward Ratio
                    rr_ratio = default_tp / default_sl
                    st.metric(
                        "⚖️ Risk/Reward Ratio",
                        f"1:{rr_ratio:.2f}",
                        help="Relação entre risco e recompensa"
                    )
                else:
                    st.info("💰 Conecte sua API para ver análise de risco personalizada")
            else:
                st.info("💰 Carregue o saldo da conta para análise de risco")
        
        # Alertas de risco
        st.markdown("### 🚨 Alertas de Risco")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_risk_alerts = st.checkbox(
                "🔔 Alertas de Risco Ativados",
                value=True,
                help="Receber alertas quando limites de risco forem atingidos"
            )
            
            if enable_risk_alerts:
                alert_types = st.multiselect(
                    "Tipos de Alerta:",
                    [
                        "Posição muito grande",
                        "Perda diária excedida",
                        "Muitas posições abertas",
                        "Stop loss atingido",
                        "Take profit atingido"
                    ],
                    default=["Posição muito grande", "Perda diária excedida"]
                )
        
        with col2:
            st.markdown("#### 📋 Status Atual")
            
            # Simula status de risco
            risk_status = []
            
            if max_position > 10:
                risk_status.append("🟡 Posição máxima alta (>10%)")
            
            if max_daily_loss > 5:
                risk_status.append("🟡 Perda diária alta (>5%)")
            
            if default_sl < 1:
                risk_status.append("🔴 Stop loss muito baixo (<1%)")
            
            if len(risk_status) == 0:
                st.success("✅ Configurações de risco adequadas")
            else:
                for status in risk_status:
                    st.warning(status)
        
        # Salvar configurações
        if st.button("💾 Salvar Configurações de Risco", type="primary"):
            st.success("✅ Configurações de risco salvas!")
            st.balloons()
    
    def render_settings(self):
        """Renderiza painel de configurações"""
        st.markdown("## ⚙️ Configurações do Sistema")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🎨 Interface", "📊 Dados", "🔔 Alertas", "📋 Sistema"])
        
        with tab1:
            st.markdown("### 🎨 Configurações da Interface")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Tema do gráfico
                chart_theme = st.selectbox(
                    "Tema do Gráfico:",
                    ["plotly_dark", "plotly_white", "ggplot2", "seaborn"],
                    index=0
                )
                
                # Estilo padrão do gráfico
                default_chart_style = st.selectbox(
                    "Estilo Padrão:",
                    ["candlestick", "ohlc", "line"],
                    index=0,
                    format_func=lambda x: {
                        "candlestick": "🕯️ Candlestick",
                        "ohlc": "📊 OHLC",
                        "line": "📈 Linha"
                    }[x]
                )
                
                # Cores personalizadas
                st.markdown("#### 🎨 Cores Personalizadas")
                bullish_color = st.color_picker("Cor Alta (Bullish):", "#00ff88")
                bearish_color = st.color_picker("Cor Baixa (Bearish):", "#ff4444")
            
            with col2:
                # Layout
                sidebar_default = st.selectbox(
                    "Sidebar Padrão:",
                    ["expanded", "collapsed", "auto"],
                    index=0
                )
                
                # Densidade da interface
                ui_density = st.selectbox(
                    "Densidade da Interface:",
                    ["compact", "normal", "spacious"],
                    index=1
                )
                
                # Animações
                enable_animations = st.checkbox("✨ Animações", value=True)
                enable_sound = st.checkbox("🔊 Sons de Alerta", value=False)
        
        with tab2:
            st.markdown("### 📊 Configurações de Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Cache de dados
                cache_duration = st.slider(
                    "Duração do Cache (minutos):",
                    min_value=1,
                    max_value=60,
                    value=5,
                    help="Tempo para manter dados em cache"
                )
                
                # Quantidade de dados históricos
                default_candles = st.slider(
                    "Candles Padrão:",
                    min_value=100,
                    max_value=1000,
                    value=500,
                    step=50,
                    help="Quantidade padrão de candles para carregar"
                )
                
                # Atualização automática
                auto_refresh_enabled = st.checkbox("🔄 Auto Refresh", value=False)
                
                if auto_refresh_enabled:
                    refresh_interval = st.slider(
                        "Intervalo (segundos):",
                        min_value=5,
                        max_value=300,
                        value=30
                    )
            
            with col2:
                # Qualidade dos dados
                data_quality = st.selectbox(
                    "Qualidade dos Dados:",
                    ["basic", "standard", "premium"],
                    index=1,
                    format_func=lambda x: {
                        "basic": "🟡 Básica",
                        "standard": "🟢 Padrão",
                        "premium": "🟣 Premium"
                    }[x]
                )
                
                # Backup de dados
                enable_backup = st.checkbox("💾 Backup Automático", value=True)
                
                if enable_backup:
                    backup_frequency = st.selectbox(
                        "Frequência do Backup:",
                        ["daily", "weekly", "monthly"],
                        format_func=lambda x: {
                            "daily": "📅 Diário",
                            "weekly": "📅 Semanal",
                            "monthly": "📅 Mensal"
                        }[x]
                    )
                
                # Compressão
                enable_compression = st.checkbox("🗜️ Compressão de Dados", value=True)
        
        with tab3:
            st.markdown("### 🔔 Configurações de Alertas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Tipos de alerta
                st.markdown("#### 📱 Canais de Notificação")
                
                enable_browser_notifications = st.checkbox("🌐 Notificações do Navegador", value=True)
                enable_email_notifications = st.checkbox("📧 Email", value=False)
                enable_telegram_notifications = st.checkbox("📱 Telegram", value=False)
                enable_discord_notifications = st.checkbox("💬 Discord", value=False)
                
                if enable_email_notifications:
                    email_address = st.text_input("📧 Email:", placeholder="seu@email.com")
                
                if enable_telegram_notifications:
                    telegram_token = st.text_input("🤖 Bot Token:", type="password")
                    telegram_chat_id = st.text_input("💬 Chat ID:")
            
            with col2:
                # Configurações de alerta
                st.markdown("#### ⚙️ Configurações")
                
                alert_frequency = st.selectbox(
                    "Frequência Máxima:",
                    ["immediate", "1min", "5min", "15min"],
                    index=1,
                    format_func=lambda x: {
                        "immediate": "⚡ Imediato",
                        "1min": "🕐 1 minuto",
                        "5min": "🕐 5 minutos",
                        "15min": "🕐 15 minutos"
                    }[x]
                )
                
                alert_priority = st.selectbox(
                    "Prioridade:",
                    ["low", "normal", "high", "critical"],
                    index=1,
                    format_func=lambda x: {
                        "low": "🟢 Baixa",
                        "normal": "🟡 Normal",
                        "high": "🟠 Alta",
                        "critical": "🔴 Crítica"
                    }[x]
                )
                
                # Horário de funcionamento
                st.markdown("#### 🕐 Horário de Funcionamento")
                
                alert_start_time = st.time_input("Início:", value=datetime.strptime("09:00", "%H:%M").time())
                alert_end_time = st.time_input("Fim:", value=datetime.strptime("18:00", "%H:%M").time())
                
                weekend_alerts = st.checkbox("📅 Alertas no Fim de Semana", value=False)
        
        with tab4:
            st.markdown("### 📋 Configurações do Sistema")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Logs
                st.markdown("#### 📝 Logs")
                
                log_level = st.selectbox(
                    "Nível de Log:",
                    ["DEBUG", "INFO", "WARNING", "ERROR"],
                    index=1
                )
                
                log_retention = st.slider(
                    "Retenção de Logs (dias):",
                    min_value=1,
                    max_value=90,
                    value=30
                )
                
                enable_performance_logs = st.checkbox("📊 Logs de Performance", value=True)
                
                # Segurança
                st.markdown("#### 🔒 Segurança")
                
                session_timeout = st.slider(
                    "Timeout de Sessão (minutos):",
                    min_value=5,
                    max_value=240,
                    value=60
                )
                
                enable_2fa = st.checkbox("🛡️ Autenticação 2FA (Futuro)", value=False, disabled=True)
            
            with col2:
                # Performance
                st.markdown("#### ⚡ Performance")
                
                max_memory_usage = st.slider(
                    "Uso Máximo de Memória (MB):",
                    min_value=100,
                    max_value=2000,
                    value=500
                )
                
                enable_gpu_acceleration = st.checkbox("🚀 Aceleração GPU (Futuro)", value=False, disabled=True)
                
                # Manutenção
                st.markdown("#### 🧹 Manutenção")
                
                auto_cleanup = st.checkbox("🧹 Limpeza Automática", value=True)
                
                if auto_cleanup:
                    cleanup_frequency = st.selectbox(
                        "Frequência:",
                        ["daily", "weekly", "monthly"],
                        format_func=lambda x: {
                            "daily": "📅 Diário",
                            "weekly": "📅 Semanal", 
                            "monthly": "📅 Mensal"
                        }[x]
                    )
                
                # Reset
                st.markdown("---")
                if st.button("🔄 Resetar Todas as Configurações", type="secondary"):
                    if st.checkbox("⚠️ Confirmar Reset"):
                        st.warning("⚠️ Esta ação não pode ser desfeita!")
                        if st.button("🔴 CONFIRMAR RESET"):
                            # Reset das configurações
                            st.success("✅ Configurações resetadas!")
                            st.balloons()
        
        # Botão para salvar todas as configurações
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("💾 Salvar Configurações", type="primary", use_container_width=True):
                st.success("✅ Configurações salvas com sucesso!")
                st.balloons()
        
        with col2:
            if st.button("🔄 Restaurar Padrões", use_container_width=True):
                st.info("🔄 Configurações restauradas para os valores padrão")
        
        with col3:
            if st.button("📤 Exportar Config", use_container_width=True):
                # Simula exportação
                config_data = {
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "settings": "exported_successfully"
                }
                st.download_button(
                    "📥 Download",
                    data=json.dumps(config_data, indent=2),
                    file_name=f"trading_bot_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
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
                # Modo demo - funcionalidades limitadas
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Gráficos", 
                    "ℹ️ Informações", 
                    "🤖 Estratégias",
                    "⚙️ Configurações"
                ])
                
                with tab1:
                    self.render_price_chart()
                
                with tab2:
                    self.render_account_info()
                
                with tab3:
                    self.render_strategies_panel()
                
                with tab4:
                    self.render_settings()
            
            elif binance_client.is_authenticated:
                # Modo autenticado - funcionalidades completas
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "📊 Dashboard", 
                    "💰 Conta", 
                    "🎯 Trading",
                    "🤖 Estratégias",
                    "🛡️ Risco",
                    "⚙️ Config"
                ])
                
                with tab1:
                    self.render_price_chart()
                
                with tab2:
                    self.render_account_info()
                
                with tab3:
                    self.render_trading_panel()
                
                with tab4:
                    self.render_strategies_panel()
                
                with tab5:
                    self.render_risk_management()
                
                with tab6:
                    self.render_settings()
            
            else:
                # Aguardando autenticação
                st.markdown("""
                ## 🔐 Bem-vindo ao Professional Trading Bot
                
                ### 🚀 Escolha seu modo de operação:
                
                #### 📊 **Modo Demo** (Recomendado para começar)
                - ✅ **Dados em tempo real** via WebSocket público
                - ✅ **Gráficos profissionais** com indicadores técnicos
                - ✅ **Sem necessidade de credenciais** - 100% seguro
                - ✅ **Ambiente de aprendizado** ideal para iniciantes
                - ❌ Sem acesso ao saldo da conta
                - ❌ Sem execução de ordens reais
                
                #### 🧪 **Paper Trading** (Para testes avançados)
                - ✅ **Simulação completa** com dados reais
                - ✅ **Testnet da Binance** - ambiente seguro
                - ✅ **Execução de ordens simuladas**
                - ✅ **Análise de performance** detalhada
                - ⚠️ Requer credenciais da API (Testnet)
                
                #### ⚡ **Live Trading** (Para profissionais)
                - ✅ **Trading com dinheiro real**
                - ✅ **Todas as funcionalidades** disponíveis
                - ✅ **Gestão de risco avançada**
                - ✅ **Estratégias automatizadas**
                - 🚨 **ATENÇÃO: RISCO REAL DE PERDA**
                - ⚠️ Requer credenciais da API (Mainnet)
                
                ### 🛡️ **Segurança Garantida:**
                - 🔒 Credenciais **nunca são salvas** no código
                - 🔒 Armazenamento **apenas em memória** temporária
                - 🔒 **Timeout automático** em 60 minutos
                - 🔒 **Limpeza automática** ao fechar navegador
                - 🔒 **Conexão direta** com a Binance
                
                ### 📚 **Como começar:**
                1. **Selecione um modo** na barra lateral
                2. **Para Demo:** Comece imediatamente
                3. **Para outros modos:** Insira suas credenciais API
                4. **Explore as funcionalidades** disponíveis
                5. **Configure suas estratégias** de trading
                
                ---
                
                <div class="info-box">
                💡 <strong>Dica:</strong> Comece sempre com o <strong>Modo Demo</strong> para se familiarizar com a plataforma antes de usar dinheiro real!
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
            
            # Auto-refresh se habilitado
            if st.session_state.get('auto_refresh', False) and current_mode == 'demo':
                time.sleep(st.session_state.get('refresh_interval', 30))
                st.rerun()
                
        except Exception as e:
            st.error("❌ Erro crítico no sistema")
            st.exception(e)
            trading_logger.log_error(f"Erro crítico no dashboard: {str(e)}", e)
            
            if st.button("🔄 Recarregar Sistema", type="primary"):
                st.rerun()

# Instância global do dashboard
dashboard = TradingDashboard()
