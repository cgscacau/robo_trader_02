"""
=============================================================================
ARQUIVO PRINCIPAL - PROFESSIONAL TRADING BOT
=============================================================================
Ponto de entrada principal da aplicação.
Inicializa o sistema e executa o dashboard Streamlit.
"""

import sys
import os

# Adiciona o diretório src ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_dashboard import dashboard
from src.utils.logger import trading_logger

def main():
    """
    Função principal da aplicação.
    Inicializa o sistema e executa o dashboard.
    """
    try:
        trading_logger.log_info("=== INICIANDO PROFESSIONAL TRADING BOT ===")
        trading_logger.log_info("Sistema inicializado com sucesso")
        
        # Executa o dashboard principal
        dashboard.run()
        
    except Exception as e:
        trading_logger.log_error(f"Erro crítico na inicialização: {str(e)}", e)
        raise

if __name__ == "__main__":
    main()
