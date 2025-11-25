"""
=============================================================================
PROFESSIONAL TRADING BOT - PREÇOS REAIS ATUALIZADOS
=============================================================================
Sistema com preços reais do Bitcoin em $90k+
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURAÇÕES COM PREÇOS ATUAIS
# =============================================================================

class Config:
    SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT', 'LTCUSDT'
    ]
    
    TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d']
    
    COLORS = {
        'bullish': '#00ff88',
        'bearish': '#ff4444',
        'neutral': '#ffaa00'
    }
    
    # PREÇOS REAIS ATUALIZADOS (Dezembro 2024)
    REAL_PRICES = {
        'BTCUSDT': 90500,    # Bitcoin em ~$90k
        'ETHUSDT': 3200,     # Ethereum
        'BNBUSDT': 680,      # BNB
        'ADAUSDT': 0.89,     # Cardano
        'XRPUSDT': 2.45,     # XRP (alta recente)
        'SOLUSDT': 195,      # Solana
        'DOTUSDT': 8.2,      # Polkadot
        'LINKUSDT': 23.5,    # Chainlink
        'AVAXUSDT': 42,      # Avalanche
        'LTCUSDT': 105       # Litecoin
    }

# =============================================================================
# PROVEDOR DE DADOS COM PREÇOS REAIS
# =============================================================================

class RealDataProvider:
    def __init__(self):
        self.cache = {}
        self.real_time_prices = {}
        self.price_thread = None
        self.running = False
        self.start_real_time_updates()
    
    def start_real_time_updates(self):
        """Inicia atualizações de preço em tempo real"""
        if not self.running:
            self.running = True
            self.price_thread = threading.Thread(target=self._update_prices_continuously, daemon=True)
            self.price_thread.start()
            print("🔴 Iniciando atualizações de preço em tempo real...")
    
    def _update_prices_continuously(self):
        """Atualiza preços continuamente"""
        while self.running:
            try:
                for symbol in Config.SYMBOLS:
                    # Primeiro tenta API real
                    real_price = self._get_real_binance_price(symbol)
                    
                    if real_price:
                        self.real_time_prices[symbol] = real_price
                    else:
                        # Fallback com preços atualizados
                        self._simulate_realistic_price(symbol)
                
                # Atualiza a cada 3-8 segundos (mais realista)
                time.sleep(np.random.uniform(3, 8))
                
            except Exception as e:
                print(f"❌ Erro na atualização: {str(e)}")
                time.sleep(5)
    
    def _get_real_binance_price(self, symbol: str) -> Optional[Dict]:
        """Tenta obter preço real da Binance"""
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                price_info = {
                    'symbol': symbol,
                    'price': float(data['lastPrice']),
                    'change_percent': float(data['priceChangePercent']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume']),
                    'timestamp': datetime.now(),
                    'source': 'binance_api'
                }
                
                print(f"✅ Preço real obtido: {symbol} = ${price_info['price']:,.2f}")
                return price_info
                
        except Exception as e:
            print(f"⚠️ API Binance falhou para {symbol}: {str(e)}")
        
        return None
    
    def _simulate_realistic_price(self, symbol: str):
        """Simula preço realista baseado nos valores atuais"""
        base_price = Config.REAL_PRICES.get(symbol, 100)
        
        # Se já tem preço anterior, usa como base
        if symbol in self.real_time_prices:
            current_price = self.real_time_prices[symbol]['price']
        else:
            current_price = base_price
        
        # Variação pequena e realista (-0.3% a +0.3%)
        change_pct = np.random.uniform(-0.3, 0.3)
        new_price = current_price * (1 + change_pct / 100)
        
        # Garante que não fique muito longe do preço base
        if abs(new_price - base_price) / base_price > 0.05:  # Máximo 5% de diferença
            new_price = base_price * (1 + np.random.uniform(-0.02, 0.02))
        
        # Simula dados de 24h baseados no preço atual
        high_24h = new_price * np.random.uniform(1.01, 1.04)
        low_24h = new_price * np.random.uniform(0.96, 0.99)
        
        # Volume realista baseado no símbolo
        if symbol == 'BTCUSDT':
            volume_base = 25000
        elif symbol == 'ETHUSDT':
            volume_base = 180000
        else:
            volume_base = 50000
        
        volume_24h = volume_base * np.random.uniform(0.8, 1.5)
        
        price_info = {
            'symbol': symbol,
            'price': round(new_price, 4 if new_price < 10 else 2),
            'change_percent': round(change_pct, 2),
            'high': round(high_24h, 4 if high_24h < 10 else 2),
            'low': round(low_24h, 4 if low_24h < 10 else 2),
            'volume': round(volume_24h, 0),
            'timestamp': datetime.now(),
            'source': 'simulated_realistic'
        }
        
        self.real_time_prices[symbol] = price_info
        
        if symbol == 'BTCUSDT':  # Log apenas Bitcoin para não poluir
            print(f"📊 Bitcoin simulado: ${price_info['price']:,.2f} ({change_pct:+.2f}%)")
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Obtém preço atual (real ou simulado)"""
        return self.real_time_prices.get(symbol)
    
    def get_data(self, symbol: str, timeframe: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados históricos com preços atualizados"""
        
        # Verifica cache
        cache_key = f"{symbol}_{timeframe}_{limit}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < 300:  # 5 minutos
                return data
        
        # Tenta API real primeiro
        data = self._get_real_binance_data(symbol, timeframe, limit)
        
        if data is None or data.empty:
            # Fallback com dados realistas
            data = self._generate_realistic_data(symbol, timeframe, limit)
        
        if data is not None:
            self.cache[cache_key] = (datetime.now(), data)
        
        return data
    
    def _get_real_binance_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Tenta obter dados reais da Binance"""
        try:
            print(f"🌐 Tentando obter dados reais da Binance: {symbol}")
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': min(limit, 1000)
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                        'taker_buy_quote', 'ignore'
                    ])
                    
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df.dropna()
                    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                    df.set_index('timestamp', inplace=True)
                    
                    if len(df) > 0:
                        current_price = df['close'].iloc[-1]
                        print(f"✅ Dados reais da Binance: {symbol} = ${current_price:,.2f} ({len(df)} candles)")
                        return df
            
            elif response.status_code == 429:
                print("⚠️ Rate limit da Binance - aguardando...")
                time.sleep(2)
            else:
                print(f"⚠️ Status {response.status_code} da Binance")
                
        except requests.exceptions.Timeout:
            print("⚠️ Timeout na API da Binance")
        except Exception as e:
            print(f"⚠️ Erro na API da Binance: {str(e)}")
        
        return None
    
    def _generate_realistic_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Gera dados realistas com preços atuais"""
        print(f"📊 Gerando dados realistas para {symbol}")
        
        base_price = Config.REAL_PRICES.get(symbol, 100)
        
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
        
        # Gera datas indo para trás no tempo
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=min(limit, 200), freq=freq)
        
        # Seed baseado no símbolo para consistência
        np.random.seed(hash(symbol) % 2**32)
        
        data = []
        
        # Começa com preço um pouco diferente do atual e vai convergindo
        start_price = base_price * np.random.uniform(0.95, 1.05)
        current_price = start_price
        
        for i, date in enumerate(dates):
            # Tendência suave em direção ao preço atual
            progress = i / len(dates)
            target_price = base_price + (base_price - start_price) * progress
            
            # Movimento aleatório + tendência
            random_change = np.random.normal(0, 0.008)  # Volatilidade reduzida
            trend_change = (target_price - current_price) / current_price * 0.1
            
            total_change = random_change + trend_change
            current_price *= (1 + total_change)
            
            # Volatilidade intraday
            volatility = np.random.uniform(0.003, 0.015)
            
            open_price = current_price
            high_price = open_price * (1 + volatility * np.random.uniform(0.3, 1))
            low_price = open_price * (1 - volatility * np.random.uniform(0.3, 1))
            close_price = np.random.uniform(low_price, high_price)
            
            # Volume realista
            if symbol == 'BTCUSDT':
                base_volume = 800
            elif symbol == 'ETHUSDT':
                base_volume = 5000
            else:
                base_volume = 1500
            
            volume = base_volume * np.random.uniform(0.5, 2.5) * (1 + volatility * 5)
            
            data.append({
                'open': round(open_price, 4 if open_price < 10 else 2),
                'high': round(high_price, 4 if high_price < 10 else 2),
                'low': round(low_price, 4 if low_price < 10 else 2),
                'close': round(close_price, 4 if close_price < 10 else 2),
                'volume': round(volume, 2)
            })
            
            current_price = close_price
        
        df = pd.DataFrame(data, index=dates)
        
        final_price = df['close'].iloc[-1]
        print(f"📈 Dados realistas gerados: {symbol} = ${final_price:,.2f} ({len(df)} candles)")
        
        return df
    
    def get_connection_status(self) -> Dict:
        """Status da conexão"""
        active_symbols = len(self.real_time_prices)
        real_data_count = len([p for p in self.real_time_prices.values() if p.get('source') == 'binance_api'])
        
        return {
            'connected': self.running and active_symbols > 0,
            'active_symbols': active_symbols,
            'real_data_sources': real_data_count,
            'simulated_sources': active_symbols - real_data_count
        }
    
    def stop(self):
        """Para atualizações"""
        self.running = False

# =============================================================================
# DASHBOARD ATUALIZADO
# =============================================================================

class TradingDashboard:
    def __init__(self):
        self.data_provider = RealDataProvider()
        self.setup_page()
        self.init_session_state()
    
    def setup_page(self):
        st.set_page_config(
            page_title="Professional Trading Bot - Real Prices",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
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
        
        .price-update {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 0.5rem;
            border-radius: 8px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .price-positive {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        
        .price-negative {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
        }
        
        .bitcoin-price {
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            background: linear-gradient(135deg, #f7931a, #ff8c00);
            color: white;
        }
        
        .connection-status {
            background: #1a1a2e;
            border-left: 4px solid #00ff88;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def init_session_state(self):
        defaults = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'data': None,
            'last_update': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_header(self):
        st.markdown('<h1 class="main-header">🚀 Professional Trading Bot - Real Prices</h1>', 
                   unsafe_allow_html=True)
        
        # Status da conexão
        status = self.data_provider.get_connection_status()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if status['connected']:
                st.markdown(f"""
                <div class="connection-status">
                    <div class="realtime-indicator">🔴 PREÇOS REAIS</div>
                    <br>
                    <small>
                    📊 {status['active_symbols']} símbolos ativos<br>
                    🌐 {status['real_data_sources']} fontes reais • 
                    📈 {status['simulated_sources']} simuladas
                    </small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("🔄 Inicializando sistema de preços...")
        
        # Destaque especial para Bitcoin
        btc_price = self.data_provider.get_current_price('BTCUSDT')
        if btc_price:
            st.markdown(f"""
            <div class="bitcoin-price">
                ₿ BITCOIN: ${btc_price['price']:,.2f} ({btc_price['change_percent']:+.2f}%)
                <br><small>Preço em tempo real • {btc_price['timestamp'].strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        st.sidebar.markdown("## 📊 Controles")
        
        # Símbolo
        symbol = st.sidebar.selectbox(
            "Símbolo:",
            Config.SYMBOLS,
            index=Config.SYMBOLS.index(st.session_state.symbol) if st.session_state.symbol in Config.SYMBOLS else 0
        )
        
        if symbol != st.session_state.symbol:
            st.session_state.symbol = symbol
            st.session_state.data = None
        
        # Timeframe
        timeframe = st.sidebar.selectbox(
            "Timeframe:",
            Config.TIMEFRAMES,
            index=Config.TIMEFRAMES.index(st.session_state.timeframe) if st.session_state.timeframe in Config.TIMEFRAMES else 5
        )
        
        if timeframe != st.session_state.timeframe:
            st.session_state.timeframe = timeframe
            st.session_state.data = None
        
        # Status em tempo real
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔴 Preços em Tempo Real")
        
        # Mostra preços de alguns símbolos principais
        main_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        for sym in main_symbols:
            price_data = self.data_provider.get_current_price(sym)
            if price_data:
                price = price_data['price']
                change = price_data['change_percent']
                source = "🌐" if price_data.get('source') == 'binance_api' else "📊"
                
                if change >= 0:
                    st.sidebar.success(f"{source} {sym.replace('USDT', '')}: ${price:,.2f} (+{change:.2f}%)")
                else:
                    st.sidebar.error(f"{source} {sym.replace('USDT', '')}: ${price:,.2f} ({change:.2f}%)")
        
        # Botões
        st.sidebar.markdown("---")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.session_state.data = None
                st.rerun()
        
        with col2:
            if st.button("💰 Bitcoin", use_container_width=True):
                st.session_state.symbol = 'BTCUSDT'
                st.session_state.data = None
                st.rerun()
    
    def render_chart(self):
        symbol = st.session_state.symbol
        timeframe = st.session_state.timeframe
        
        # Cabeçalho com preço em tempo real
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## 📈 {symbol} - {timeframe}")
        
        with col2:
            # Preço em tempo real
            current_price = self.data_provider.get_current_price(symbol)
            if current_price:
                price = current_price['price']
                change = current_price['change_percent']
                timestamp = current_price['timestamp']
                source = current_price.get('source', 'unknown')
                
                source_icon = "🌐" if source == 'binance_api' else "📊"
                css_class = "price-positive" if change >= 0 else "price-negative"
                
                st.markdown(f"""
                <div class="price-update {css_class}">
                    {source_icon} ${price:,.4f if price < 10 else price:,.2f} 
                    <span style="font-size: 0.9em;">({change:+.2f}%)</span>
                    <br>
                    <small>{timestamp.strftime('%H:%M:%S')} • {source.replace('_', ' ').title()}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("🔄 Carregando preço...")
        
        # Carrega dados históricos
        if st.session_state.data is None:
            with st.spinner("📊 Carregando dados históricos..."):
                st.session_state.data = self.data_provider.get_data(symbol, timeframe, 500)
                st.session_state.last_update = datetime.now()
        
        df = st.session_state.data
        
        if df is not None and not df.empty:
            # Cria gráfico
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{symbol} - {timeframe} (Preços Reais)', 'Volume'),
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
                title=f"{symbol} - {timeframe} (Preços Atualizados)",
                yaxis_title="Preço (USDT)",
                yaxis2_title="Volume",
                template="plotly_dark",
                height=600,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(type='date')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas
            self.render_metrics(df, current_price)
        
        else:
            st.error("❌ Não foi possível carregar dados")
            
            if st.button("🔄 Tentar Novamente", type="primary"):
                st.session_state.data = None
                st.rerun()
    
    def render_metrics(self, df: pd.DataFrame, current_price: Optional[Dict]):
        if df is None or df.empty:
            return
        
        # Usa preço em tempo real se disponível
        if current_price:
            price = current_price['price']
            change_pct = current_price['change_percent']
            high_24h = current_price['high']
            low_24h = current_price['low']
            volume_24h = current_price['volume']
        else:
            price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2] if len(df) > 1 else price
            change_pct = ((price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            volume_24h = df['volume'].sum()
        
        # Métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Preço Atual",
                f"${price:,.4f}" if price < 10 else f"${price:,.2f}",
                delta=f"{change_pct:+.2f}%"
            )
        
        with col2:
            st.metric("📈 Máxima 24h", f"${high_24h:,.2f}")
        
        with col3:
            st.metric("📉 Mínima 24h", f"${low_24h:,.2f}")
        
        with col4:
            st.metric("📊 Volume 24h", f"{volume_24h:,.0f}")
        
        with col5:
            # Market Cap aproximado (apenas para Bitcoin)
            if st.session_state.symbol == 'BTCUSDT':
                market_cap = price * 19.7  # ~19.7M BTC em circulação
                st.metric("💎 Market Cap", f"${market_cap/1e12:.2f}T")
            else:
                # RSI para outros
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1] if len(rs) > 0 and not np.isnan(rs.iloc[-1]) else 50
                rsi_color = "🟢" if 30 <= rsi <= 70 else ("🔴" if rsi > 70 else "🟡")
                st.metric(f"📊 RSI {rsi_color}", f"{rsi:.1f}")
        
        # Status de fonte de dados
        if current_price:
            source = current_price.get('source', 'unknown')
            timestamp = current_price['timestamp']
            
            if source == 'binance_api':
                st.success(f"🌐 **DADOS REAIS DA BINANCE** - Última atualização: {timestamp.strftime('%H:%M:%S')}")
            else:
                st.info(f"📊 **DADOS SIMULADOS REALISTAS** - Última atualização: {timestamp.strftime('%H:%M:%S')}")
    
    def run(self):
        try:
            self.render_header()
            self.render_sidebar()
            self.render_chart()
            
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
            
            if st.button("🔄 Recarregar"):
                st.rerun()

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    try:
        print("🚀 Iniciando Professional Trading Bot com preços reais...")
        print(f"💰 Bitcoin configurado para ~${Config.REAL_PRICES['BTCUSDT']:,.0f}")
        
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Erro crítico: {str(e)}")
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    main()
