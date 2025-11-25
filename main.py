"""
=============================================================================
PROFESSIONAL TRADING BOT - ARQUIVO PRINCIPAL CORRIGIDO
=============================================================================
Sistema completo de trading com interface Streamlit
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    # Importações principais
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    from datetime import datetime, timedelta
    from typing import Optional, Dict, Any, List
    import time
    import json
    import requests
    
    # Importações dos módulos do projeto
    from config.settings import TradingConfig
    from api.binance_client import binance_client
    from utils.logger import trading_logger
    
    # Importa o dashboard
    from ui.main_dashboard import TradingDashboard
    
except ImportError as e:
    st.error(f"❌ Erro de importação: {str(e)}")
    st.stop()

def main():
    """
    Função principal da aplicação.
    Inicializa o sistema e executa o dashboard.
    """
    try:
        # Log de inicialização
        print("=== INICIANDO PROFESSIONAL TRADING BOT ===")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Python path: {sys.path[0]}")
        
        # Inicializa e executa o dashboard
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Erro crítico na inicialização: {str(e)}")
        st.exception(e)
        print(f"ERRO CRÍTICO: {str(e)}")

if __name__ == "__main__":
    main()
