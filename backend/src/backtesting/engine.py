
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.technical.analyzer import TechnicalAnalyzer

logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    Backtesting Engine for Methefor Financial Freedom
    Simulates trading based on TechnicalAnalyzer signals over historical data.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.analyzer = TechnicalAnalyzer()
        self.commission_rate = 0.001 # 0.1% per trade
        
    def load_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical data"""
        logger.info(f"Fetching historical data for {symbol} ({period}, {interval})...")
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                logger.error(f"No data found for {symbol}")
                return pd.DataFrame()
            return df
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return pd.DataFrame()

    def run_backtest(self, symbol: str, period: str = "6mo", interval: str = "1d", window_size: int = 100) -> Dict:
        """
        Run backtest for a single symbol.
        
        Strategy:
        - Check signal every candle.
        - BUY if Signal == 'STRONG BUY' or 'BUY'
        - SELL if Signal == 'STRONG SELL' or 'SELL'
        - HOLD otherwise
        """
        logger.info(f"Backtesting {symbol} started...")
        
        data = self.load_historical_data(symbol, period, interval)
        if data.empty or len(data) < window_size:
            return {"error": "Not enough data"}

        portfolio = {
            "cash": self.initial_capital,
            "holdings": 0,
            "total_value": self.initial_capital,
            "trades": []
        }
        
        history = []
        
        # Simulation Loop
        # We need at least 'window_size' bars to calculate technicals (e.g. SMA200)
        # We iterate from window_size to end
        
        for i in range(window_size, len(data)):
            # Slice recent data up to current point 'i'
            # To speed up, we don't need all history, just enough for indicators (e.g. last 300 bars)
            start_slice = max(0, i - 300)
            current_slice = data.iloc[start_slice : i+1]
            
            # Analyze "Current" State (simulated)
            current_price = current_slice['Close'].iloc[-1]
            current_date = current_slice.index[-1]
            
            # Perform Analysis
            # Note: This is computationally intensive for small intervals.
            # Using 'analyze_dataframe' which calculates everything on the slice.
            analysis = self.analyzer.analyze_dataframe(symbol, current_slice)
            
            if 'error' in analysis:
                continue
                
            decision = analysis['technical_signals']['decision']
            score = analysis['technical_signals']['score']
            
            # Trading Logic
            action = None
            quantity = 0
            price = current_price
            
            # Simple Logic: All-in Buy/Sell
            if decision in ['STRONG BUY', 'BUY']:
                if portfolio['cash'] > 100: # Min cash to buy
                    # Buy with available cash
                    quantity = (portfolio['cash'] * 0.99) / price # Leave room for commission
                    cost = quantity * price
                    comm = cost * self.commission_rate
                    
                    portfolio['cash'] -= (cost + comm)
                    portfolio['holdings'] += quantity
                    portfolio['trades'].append({
                        "date": current_date,
                        "type": "BUY",
                        "price": price,
                        "amount": quantity,
                        "score": score,
                        "reason": decision
                    })
                    action = "BOUGHT"

            elif decision in ['STRONG SELL', 'SELL']:
                if portfolio['holdings'] > 0:
                    # Sell all
                    revenue = portfolio['holdings'] * price
                    comm = revenue * self.commission_rate
                    
                    portfolio['cash'] += (revenue - comm)
                    portfolio['holdings'] = 0
                    portfolio['trades'].append({
                        "date": current_date,
                        "type": "SELL",
                        "price": price,
                        "amount": quantity, # Full sell
                        "score": score,
                        "reason": decision
                    })
                    action = "SOLD"
            
            # Update Portfolio Value
            current_total = portfolio['cash'] + (portfolio['holdings'] * price)
            portfolio['total_value'] = current_total
            
            history.append({
                "date": current_date,
                "price": price,
                "total_value": current_total,
                "action": action
            })
            
            # Progress log every 10%
            if i % (len(data) // 10) == 0:
                print(f"Progress: {i}/{len(data)} - Value: ${current_total:.2f}")

        # Final Report
        roi = ((portfolio['total_value'] - self.initial_capital) / self.initial_capital) * 100
        
        results = {
            "symbol": symbol,
            "period": period,
            "initial_capital": self.initial_capital,
            "final_value": portfolio['total_value'],
            "roi_percent": roi,
            "total_trades": len(portfolio['trades']),
            "trades": portfolio['trades'],
            "history": history[-5:] # Last 5 records
        }
        
        logger.info(f"Backtest Finished. ROI: {roi:.2f}%")
        return results

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    engine = BacktestEngine()
    # Using '1d' interval because '1h' takes too long for the loop without optimization
    res = engine.run_backtest("AAPL", period="1y", interval="1d") 
    
    print("\n=== BACKTEST RESULTS ===")
    print(f"Symbol: {res['symbol']}")
    print(f"ROI: {res['roi_percent']:.2f}%")
    print(f"Final Value: ${res['final_value']:.2f}")
    print(f"Total Trades: {res['total_trades']}")
    print("Trades:", res['trades'])
