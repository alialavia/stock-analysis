import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict, Any

class StockAnalyzer:
    """
    A class to handle stock data retrieval and basic analysis using yfinance
    """
    
    def __init__(self):
        """Initialize the StockAnalyzer"""
        pass
    
    def get_stock_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Retrieve historical stock data for a given ticker
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for data retrieval
            
        Returns:
            pd.DataFrame: Historical stock data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return None
                
            return data
            
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get basic stock information and metrics
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Stock information dictionary
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
            
        except Exception as e:
            st.error(f"Error fetching info for {ticker}: {str(e)}")
            return {}
    
    def get_financial_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        Extract key financial metrics from stock info
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Key financial metrics
        """
        info = self.get_stock_info(ticker)
        
        metrics = {
            'current_price': info.get('currentPrice', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'eps': info.get('trailingEps', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            'beta': info.get('beta', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'volume': info.get('volume', 'N/A'),
            'avg_volume': info.get('averageVolume', 'N/A')
        }
        
        return metrics
    
    def compare_stocks(self, tickers: List[str], period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Compare multiple stocks by retrieving their closing prices
        
        Args:
            tickers (List[str]): List of stock ticker symbols
            period (str): Time period for comparison
            
        Returns:
            pd.DataFrame: DataFrame with closing prices for all tickers
        """
        try:
            comparison_data = pd.DataFrame()
            
            for ticker in tickers:
                stock_data = self.get_stock_data(ticker, period)
                if stock_data is not None and not stock_data.empty:
                    comparison_data[ticker] = stock_data['Close']
                else:
                    st.warning(f"Could not fetch data for {ticker}")
            
            if comparison_data.empty:
                return None
                
            # Forward fill missing values
            comparison_data = comparison_data.fillna(method='ffill')
            
            return comparison_data
            
        except Exception as e:
            st.error(f"Error comparing stocks: {str(e)}")
            return None
    
    def get_dividend_history(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Get dividend history for a stock
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for dividend history
            
        Returns:
            pd.DataFrame: Dividend history or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            
            if dividends.empty:
                return None
            
            # Filter by period if needed
            if period != "max":
                end_date = pd.Timestamp.now()
                if period == "1y":
                    start_date = end_date - pd.DateOffset(years=1)
                elif period == "2y":
                    start_date = end_date - pd.DateOffset(years=2)
                elif period == "5y":
                    start_date = end_date - pd.DateOffset(years=5)
                else:
                    start_date = end_date - pd.DateOffset(years=1)
                
                dividends = dividends[dividends.index >= start_date]
            
            return dividends.to_frame(name='Dividend')
            
        except Exception as e:
            st.error(f"Error fetching dividend history for {ticker}: {str(e)}")
            return None
    
    def calculate_performance_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate basic performance metrics for stock data
        
        Args:
            data (pd.DataFrame): Stock price data
            
        Returns:
            Dict: Performance metrics
        """
        try:
            if data.empty:
                return {}
            
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            
            total_return = ((end_price - start_price) / start_price) * 100
            
            # Calculate daily returns
            daily_returns = data['Close'].pct_change().dropna()
            
            # Calculate volatility (annualized)
            volatility = daily_returns.std() * (252 ** 0.5) * 100
            
            # Calculate Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            avg_daily_return = daily_returns.mean()
            sharpe_ratio = (avg_daily_return * 252 - risk_free_rate) / (daily_returns.std() * (252 ** 0.5))
            
            # Calculate maximum drawdown
            cumulative_returns = (1 + daily_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
            
            metrics = {
                'total_return': total_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'start_price': start_price,
                'end_price': end_price
            }
            
            return metrics
            
        except Exception as e:
            st.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol is valid by attempting to fetch basic info
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            bool: True if ticker is valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got meaningful data
            return 'symbol' in info or 'shortName' in info or 'longName' in info
            
        except Exception:
            return False
