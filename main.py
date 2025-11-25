"""
=============================================================================
PROFESSIONAL TRADING BOT - ARQUIVO PRINCIPAL CORRIGIDO
=============================================================================
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    import streamlit as st
    from ui.main_dashboard import TradingDashboard  # Import corrigido
    
except ImportError as e:
    st.error(f"❌ Erro de importação: {str(e)}")
    st.stop()

def main():
    """Função principal da aplicação"""
    try:
        print("=== INICIANDO PROFESSIONAL TRADING BOT ===")
        
        # Cria e executa o dashboard
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Erro crítico: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()


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
