"""
=============================================================================
DASHBOARD PRINCIPAL - VERSÃO CLOUD SEGURA
=============================================================================
Interface otimizada para Streamlit Cloud com entrada segura de credenciais
e modo demo com WebSocket público.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time

from ..config.settings import TradingConfig
from ..api.binance_client import binance_client
from ..utils.logger import trading_logger

class TradingDashboard:
    """
    Dashboard principal otimizado para ambiente cloud.
    Suporta modo demo e entrada segura de credenciais.
    """
    
    def __init__(self):
        """Inicializa o dashboard."""
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configura a página do Streamlit."""
        st.set_page_config(**TradingConfig.STREAMLIT_CONFIG)
        
        # CSS customizado aprimorado
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
        .mode-paper {
            background: linear-gradient(90deg, #00bfff, #0080ff);
            color: white;
            padding: 0.7rem;
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .mode-live {
            background: linear-gradient(90deg, #ff4444, #cc0000);
            color: white;
            padding: 0.7rem;
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .security-notice {
            background-color: #2d5a2d;
            border-left: 4px solid #00ff88;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .warning-notice {
            background-color: #5a4d2d;
            border-left: 4px solid #ffaa00;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #404040;
        }
        .demo-features {
            background-color: #1a1a2e;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #ffa500;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Inicializa variáveis de estado da sessão."""
        if 'operation_mode' not in st.session_state:
            st.session_state.operation_mode = 'demo'
            binance_client.set_operation_mode('demo')
        
        if 'selected_symbol' not in st.session_state:
            st.session_state.selected_symbol = 'BTCUSDT'
        
        if 'selected_timeframe' not in st.session_state:
            st.session_state.selected_timeframe = TradingConfig.DEFAULT_TIMEFRAME
        
        if 'account_balance' not in st.session_state:
            st.session_state.account_balance = None
        
        if 'historical_data' not in st.session_state:
            st.session_state.historical_data = None
        
        if 'last_auth_attempt' not in st.session_state:
            st.session_state.last_auth_attempt = None
        
        if 'price_data' not in st.session_state:
            st.session_state.price_data = {}
    
    def render_header(self):
        """Renderiza o cabeçalho com indicador de modo."""
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot</h1>', 
                   unsafe_allow_html=True)
        
        # Indicador de modo atual
        mode_config = TradingConfig.get_operation_mode_config(st.session_state.operation_mode)
        
        if st.session_state.operation_mode == 'demo':
            st.markdown(f'<div class="mode-demo">📊 {mode_config["name"].upper()} - Dados Públicos WebSocket</div>', 
                       unsafe_allow_html=True)
        elif st.session_state.operation_mode == 'paper_trading':
            st.markdown(f'<div class="mode-paper">🧪 {mode_config["name"].upper()} - Testnet</div>', 
                       unsafe_allow_html=True)
        elif st.session_state.operation_mode == 'live_trading':
            st.markdown(f'<div class="mode-live">⚡ {mode_config["name"].upper()} - Mainnet</div>', 
                       unsafe_allow_html=True)
    
    def render_mode_selection_sidebar(self):
        """Renderiza seleção de modo na sidebar."""
        st.sidebar.markdown("## 🎯 Modo de Operação")
        
        # Informações dos modos
        st.sidebar.markdown("""
        **📊 Demo**: Dados públicos, sem API
        **🧪 Paper**: Simulação com Testnet  
        **⚡ Live**: Trading real com Mainnet
        """)
        
        current_mode = st.session_state.operation_mode
        mode_options = list(TradingConfig.OPERATION_MODES.keys())
        mode_names = [TradingConfig.OPERATION_MODES[m]['name'] for m in mode_options]
        
        selected_mode_name = st.sidebar.selectbox(
            "Selecione o modo:",
            mode_names,
            index=mode_options.index(current_mode)
        )
        
        selected_mode = mode_options[mode_names.index(selected_mode_name)]
        
        if selected_mode != current_mode:
            st.session_state.operation_mode = selected_mode
            binance_client.set_operation_mode(selected_mode)
            
            # Limpa dados ao trocar modo
            st.session_state.account_balance = None
            st.session_state.historical_data = None
            
            st.rerun()
    
    def render_authentication_sidebar(self):
        """Renderiza painel de autenticação para modos que requerem API."""
        mode_config = TradingConfig.get_operation_mode_config(st.session_state.operation_mode)
        
        if not mode_config.get('requires_api', False):
            # Modo demo - não precisa de autenticação
            st.sidebar.markdown("## 🔓 Sem Autenticação")
            st.sidebar.success("✅ Modo Demo Ativo")
            st.sidebar.markdown("Usando dados públicos via WebSocket")
            return
        
        st.sidebar.markdown("## 🔐 Autenticação API")
        
        if not binance_client.is_authenticated:
            with st.sidebar.form("auth_form"):
                st.markdown("### Credenciais Binance")
                
                # Aviso de segurança
                st.markdown("""
                <div class="security-notice">
                🔒 <strong>Segurança:</strong><br>
                • Credenciais não são salvas<br>
                • Apenas em memória temporária<br>
                • Timeout automático em 60min
                </div>
                """, unsafe_allow_html=True)
                
                # Tipo de conta baseado no modo
                if st.session_state.operation_mode == 'paper_trading':
                    st.info("🧪 **Testnet** - Ambiente de testes")
                    account_type = st.selectbox("Tipo de Conta:", ["Spot", "Futures"])
                else:
                    st.warning("⚡ **Mainnet** - Ambiente REAL")
                    account_type = st.selectbox("Tipo de Conta:", ["Spot", "Futures"])
                
                # Campos de API com validação visual
                api_key = st.text_input(
                    "API Key:",
                    type="password",
                    help="Sua chave de API da Binance (não será salva)",
                    placeholder="Digite sua API Key aqui..."
                )
                
                api_secret = st.text_input(
                    "API Secret:",
                    type="password",
                    help="Seu segredo de API da Binance (não será salvo)",
                    placeholder="Digite seu API Secret aqui..."
                )
                
                # Validação em tempo real
                if api_key or api_secret:
                    validation = TradingConfig.validate_credentials_format(api_key, api_secret)
                    if not validation['valid']:
                        for error in validation['errors']:
                            st.error(f"⚠️ {error}")
                
                # Botão de autenticação
                submit_button = st.form_submit_button("🔑 Conectar API", use_container_width=True)
                
                if submit_button:
                    if api_key and api_secret:
                        validation = TradingConfig.validate_credentials_format(api_key, api_secret)
                        
                        if validation['valid']:
                            is_testnet = st.session_state.operation_mode == 'paper_trading'
                            acc_type = account_type.lower()
                            
                            with st.spinner("🔄 Conectando com a Binance..."):
                                result = binance_client.authenticate(api_key, api_secret, is_testnet, acc_type)
                            
                            st.session_state.last_auth_attempt = result
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.success(f"⏱️ Tempo de resposta: {result['response_time']:.2f}s")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                                if result.get('suggestion'):
                                    st.info(f"💡 {result['suggestion']}")
                        else:
                            st.error("⚠️ Corrija os erros de formato antes de conectar")
                    else:
                        st.error("⚠️ Preencha todos os campos!")
        
        else:
            # Usuário autenticado
            st.sidebar.success("✅ API Conectada!")
            
            # Informações da conexão
            if binance_client.temp_credentials:
                creds = binance_client.temp_credentials
                env = "TESTNET" if creds['testnet'] else "MAINNET"
                acc_type = creds['account_type'].upper()
                st.sidebar.info(f"🌐 {env} - {acc_type}")
            
            # Tempo restante
            if binance_client.credentials_timestamp:
                elapsed = datetime.now() - binance_client.credentials_timestamp
                remaining = TradingConfig.CREDENTIALS_TIMEOUT - (elapsed.total_seconds() / 60)
                st.sidebar.info(f"⏱️ Expira em: {remaining:.0f} min")
            
            # Botão de desconexão
            if st.sidebar.button("🔓 Desconectar", use_container_width=True):
                binance_client.disconnect()
                st.session_state.account_balance = None
                st.rerun()
    
    def render_trading_controls_sidebar(self):
        """Renderiza controles de trading."""
        st.sidebar.markdown("## 📊 Controles de Trading")
        
        # Símbolos disponíveis baseados no modo
        if st.session_state.operation_mode == 'demo':
            available_symbols = TradingConfig.PUBLIC_SYMBOLS
        else:
            available_symbols = TradingConfig.DEFAULT_SYMBOLS
        
        # Seleção de símbolo
        symbol = st.sidebar.selectbox(
            "Símbolo:",
            available_symbols,
            index=available_symbols.index(st.session_state.selected_symbol) 
                  if st.session_state.selected_symbol in available_symbols 
                  else 0
        )
        
        if symbol != st.session_state.selected_symbol:
            st.session_state.selected_symbol = symbol
            st.session_state.historical_data = None
        
        # Seleção de timeframe
        timeframe = st.sidebar.selectbox(
            "Timeframe:",
            TradingConfig.AVAILABLE_TIMEFRAMES,
            index=TradingConfig.AVAILABLE_TIMEFRAMES.index(st.session_state.selected_timeframe)
        )
        
        if timeframe != st.session_state.selected_timeframe:
            st.session_state.selected_timeframe = timeframe
            st.session_state.historical_data = None
        
        # Botão para atualizar dados
        if st.sidebar.button("🔄 Atualizar Dados", use_container_width=True):
            st.session_state.historical_data = None
            st.session_state.account_balance = None
            st.session_state.price_data = {}
            st.rerun()
    
    def render_demo_mode_info(self):
        """Renderiza informações específicas do modo demo."""
        if st.session_state.operation_mode != 'demo':
            return
        
        st.markdown("""
        <div class="demo-features">
        <h3>📊 Modo Demonstração - Recursos Disponíveis</h3>
        <ul>
        <li>✅ <strong>Dados em Tempo Real</strong> - WebSocket público da Binance</li>
        <li>✅ <strong>Gráficos Interativos</strong> - Candlesticks com volume</li>
        <li>✅ <strong>Indicadores Técnicos</strong> - Todos os 20+ indicadores disponíveis</li>
        <li>✅ <strong>Backtesting</strong> - Teste suas estratégias com dados históricos</li>
        <li>✅ <strong>Otimização</strong> - Encontre os melhores parâmetros</li>
        <li>❌ <strong>Ordens Reais</strong> - Não disponível (sem API)</li>
        <li>❌ <strong>Saldo da Conta</strong> - Não disponível (sem API)</li>
        </ul>
        <p><strong>💡 Dica:</strong> Use este modo para testar estratégias antes de conectar sua API!</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_price_chart(self):
        """Renderiza gráfico de preços otimizado por modo."""
        symbol = st.session_state.selected_symbol
        timeframe = st.session_state.selected_timeframe
        
        st.markdown(f"## 📈 Gráfico - {symbol}")
        
        # Obtém dados baseado no modo
        if st.session_state.operation_mode == 'demo':
            # Modo demo - usa API pública
            if st.session_state.historical_data is None:
                with st.spinner("📊 Carregando dados públicos..."):
                    st.session_state.historical_data = binance_client.get_public_historical_data(
                        symbol, timeframe, 500
                    )
        else:
            # Modo autenticado - usa API privada
            if binance_client.is_authenticated and st.session_state.historical_data is None:
                with st.spinner("📊 Carregando dados da API..."):
                    st.session_state.historical_data = binance_client.get_historical_data(
                        symbol, timeframe, 500
                    )
        
        df = st.session_state.historical_data
        
        if df is not None and not df.empty:
            # Cria gráfico
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} - {timeframe}', 'Volume'),
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
                    increasing_line_color=TradingConfig.CHART_COLORS['bullish'],
                    decreasing_line_color=TradingConfig.CHART_COLORS['bearish']
                ),
                row=1, col=1
            )
            
            # Volume
            colors = ['#ff4444' if close < open else '#00ff88' 
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
                title=f"{symbol} - {timeframe} ({'Demo Mode' if st.session_state.operation_mode == 'demo' else 'API Mode'})",
                yaxis_title="Preço (USDT)",
                yaxis2_title="Volume",
                template="plotly_dark",
                height=600,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(type='date')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas atuais
            self.render_price_metrics(df)
        
        else:
            st.error("❌ Erro ao carregar dados do gráfico")
            if st.session_state.operation_mode != 'demo':
                st.info("💡 Tente o modo Demo para dados públicos sem API")
    
    def render_price_metrics(self, df: pd.DataFrame):
        """Renderiza métricas de preço."""
        if df is None or df.empty:
            return
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        # Dados em tempo real do WebSocket (se disponível)
        if st.session_state.operation_mode == 'demo':
            cached_price = binance_client.get_cached_price(st.session_state.selected_symbol)
            if cached_price:
                current_price = cached_price['price']
                price_change = cached_price.get('change_percent', price_change)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Preço Atual", f"${current_price:.4f}")
        
        with col2:
            st.metric("📊 Variação", f"{price_change:+.2f}%")
        
        with col3:
            st.metric("📈 Máxima", f"${df['high'].iloc[-1]:.4f}")
        
        with col4:
            st.metric("📉 Mínima", f"${df['low'].iloc[-1]:.4f}")
        
        # Informações do WebSocket em tempo real
        if st.session_state.operation_mode == 'demo':
            cached_price = binance_client.get_cached_price(st.session_state.selected_symbol)
            if cached_price:
                timestamp = cached_price['timestamp'].strftime("%H:%M:%S")
                st.success(f"🔴 Dados em tempo real via WebSocket - Última atualização: {timestamp}")
    
    def render_account_info(self):
        """Renderiza informações da conta."""
        if st.session_state.operation_mode == 'demo':
            st.info("📊 **Modo Demo**: Informações da conta não disponíveis sem API")
            return
        
        if not binance_client.is_authenticated:
            st.info("🔐 Conecte sua API para ver informações da conta")
            return
        
        st.markdown("## 💰 Informações da Conta")
        
        # Obtém saldo
        if st.session_state.account_balance is None:
            with st.spinner("💰 Carregando saldo da conta..."):
                st.session_state.account_balance = binance_client.get_account_balance()
        
        balance_data = st.session_state.account_balance
        
        if balance_data:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            total_balance = balance_data.get('total_balance', {})
            free_balance = balance_data.get('free_balance', {})
            
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
            
            # Tabela detalhada
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
    
    def run(self):
        """Executa o dashboard principal."""
        # Renderiza componentes principais
        self.render_header()
        self.render_mode_selection_sidebar()
        self.render_authentication_sidebar()
        self.render_trading_controls_sidebar()
        
        # Conteúdo principal baseado no modo
        if st.session_state.operation_mode == 'demo':
            # Modo demo - sempre disponível
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "ℹ️ Informações", "⚙️ Configurações"])
            
            with tab1:
                self.render_price_chart()
            
            with tab2:
                self.render_demo_mode_info()
            
            with tab3:
                st.markdown("## ⚙️ Configurações")
                st.info("🚧 Configurações avançadas - Próximas sessões")
        
        elif binance_client.is_authenticated:
            # Modo autenticado - funcionalidades completas
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💰 Conta", "⚙️ Configurações"])
            
            with tab1:
                self.render_price_chart()
            
            with tab2:
                self.render_account_info()
            
            with tab3:
                st.markdown("## ⚙️ Configurações")
                st.info("🚧 Configurações avançadas - Próximas sessões")
        
        else:
            # Aguardando autenticação
            st.markdown("""
            ## 🔐 Autenticação Necessária
            
            Para usar este modo, você precisa fornecer suas credenciais da API Binance.
            
            ### 🛡️ Segurança Garantida:
            - ✅ Credenciais **nunca** são salvas no código
            - ✅ Armazenamento **apenas** em memória temporária
            - ✅ Timeout automático em 60 minutos
            - ✅ Limpeza automática ao fechar o navegador
            
            ### 🚀 Para começar:
            1. Insira suas credenciais na barra lateral
            2. As credenciais são validadas em tempo real
            3. Conexão segura com a Binance
            4. Acesso completo às funcionalidades
            
            ### 💡 Alternativa:
            Use o **Modo Demo** para testar sem credenciais!
            """)

# Instância global do dashboard
dashboard = TradingDashboard()
