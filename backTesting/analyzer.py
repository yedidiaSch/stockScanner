# Import the consolidated analyzer functionality  
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer import analyze_stock_backtest as analyze_stock

# For backward compatibility, re-export the function
__all__ = ['analyze_stock']
