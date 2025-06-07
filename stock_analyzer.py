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

    def get_stock_data(self,
                       ticker: str,
                       period: str = "1y") -> Optional[pd.DataFrame]:
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

    def compare_stocks(self,
                       tickers: List[str],
                       period: str = "1y") -> Optional[pd.DataFrame]:
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
            comparison_data = comparison_data.ffill()

            return comparison_data

        except Exception as e:
            st.error(f"Error comparing stocks: {str(e)}")
            return None

    def get_dividend_history(self,
                             ticker: str,
                             period: str = "1y") -> Optional[pd.DataFrame]:
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

            return pd.DataFrame({'Dividend': dividends})

        except Exception as e:
            st.error(f"Error fetching dividend history for {ticker}: {str(e)}")
            return None

    def calculate_performance_metrics(self,
                                      data: pd.DataFrame) -> Dict[str, float]:
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
            volatility = daily_returns.std() * (252**0.5) * 100

            # Calculate Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            avg_daily_return = daily_returns.mean()
            sharpe_ratio = (avg_daily_return * 252 -
                            risk_free_rate) / (daily_returns.std() *
                                               (252**0.5))

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

    def get_options_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get options data for a given ticker including all expiry dates
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Options data with expiry dates, calls, and puts
        """
        try:
            stock = yf.Ticker(ticker)
            options_data = {}

            # Get all expiry dates
            expiry_dates = stock.options

            if not expiry_dates:
                return {}

            options_data['expiry_dates'] = expiry_dates
            options_data['calls'] = {}
            options_data['puts'] = {}

            for expiry in expiry_dates:
                try:
                    opt_chain = stock.option_chain(expiry)
                    options_data['calls'][expiry] = opt_chain.calls
                    options_data['puts'][expiry] = opt_chain.puts
                except Exception as e:
                    st.warning(
                        f"Could not fetch options data for expiry {expiry}: {str(e)}"
                    )
                    continue

            return options_data

        except Exception as e:
            st.error(f"Error fetching options data for {ticker}: {str(e)}")
            return {}

    def calculate_options_interest_value(
            self, options_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Calculate open interest multiplied by last price for each expiry date
        
        Args:
            options_data (Dict): Options data from get_options_data
            
        Returns:
            Dict: DataFrames with calculated interest values for calls and puts
        """
        try:
            if not options_data or 'expiry_dates' not in options_data:
                return {}

            result = {
                'calls_summary': [],
                'puts_summary': [],
                'calls_detail': {},
                'puts_detail': {}
            }

            for expiry in options_data['expiry_dates']:
                if expiry in options_data['calls']:
                    calls_df = options_data['calls'][expiry].copy()

                    if not calls_df.empty and 'openInterest' in calls_df.columns and 'lastPrice' in calls_df.columns:
                        # Calculate total interest value for this expiry
                        calls_df['interestValue'] = calls_df[
                            'openInterest'] * calls_df['lastPrice'] * 100.0
                        total_calls_value = calls_df['interestValue'].sum()
                        total_calls_interest = calls_df['openInterest'].sum()

                        # Calculate volume statistics
                        total_volume = calls_df['volume'].sum() if 'volume' in calls_df.columns else 0
                        avg_volume = calls_df['volume'].mean() if 'volume' in calls_df.columns else 0
                        
                        result['calls_summary'].append({
                            'expiry': expiry,
                            'total_open_interest': total_calls_interest,
                            'total_interest_value': total_calls_value,
                            'avg_last_price': calls_df['lastPrice'].mean(),
                            'total_volume': total_volume,
                            'avg_volume': avg_volume
                        })

                        result['calls_detail'][expiry] = calls_df

                if expiry in options_data['puts']:
                    puts_df = options_data['puts'][expiry].copy()

                    if not puts_df.empty and 'openInterest' in puts_df.columns and 'lastPrice' in puts_df.columns:
                        # Calculate total interest value for this expiry
                        puts_df['interestValue'] = puts_df[
                            'openInterest'] * puts_df['lastPrice'] * 100.0
                        total_puts_value = puts_df['interestValue'].sum()
                        total_puts_interest = puts_df['openInterest'].sum()

                        # Calculate volume statistics
                        total_volume = puts_df['volume'].sum() if 'volume' in puts_df.columns else 0
                        avg_volume = puts_df['volume'].mean() if 'volume' in puts_df.columns else 0
                        
                        result['puts_summary'].append({
                            'expiry': expiry,
                            'total_open_interest': total_puts_interest,
                            'total_interest_value': total_puts_value,
                            'avg_last_price': puts_df['lastPrice'].mean(),
                            'total_volume': total_volume,
                            'avg_volume': avg_volume
                        })

                        result['puts_detail'][expiry] = puts_df

            # Convert summaries to DataFrames
            if result['calls_summary']:
                result['calls_summary'] = pd.DataFrame(result['calls_summary'])
            if result['puts_summary']:
                result['puts_summary'] = pd.DataFrame(result['puts_summary'])

            return result

        except Exception as e:
            st.error(f"Error calculating options interest values: {str(e)}")
            return {}
