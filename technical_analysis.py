import pandas as pd
import numpy as np
from typing import Optional

class TechnicalAnalysis:
    """
    A class to perform technical analysis calculations on stock data
    """
    
    def __init__(self):
        """Initialize the TechnicalAnalysis class"""
        pass
    
    def calculate_moving_averages(self, data: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """
        Calculate moving averages for given periods
        
        Args:
            data (pd.DataFrame): Stock price data
            periods (list): List of periods for moving averages
            
        Returns:
            pd.DataFrame: Data with moving averages added
        """
        df = data.copy()
        
        for period in periods:
            df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
        
        return df
    
    def calculate_exponential_moving_averages(self, data: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """
        Calculate exponential moving averages
        
        Args:
            data (pd.DataFrame): Stock price data
            periods (list): List of periods for EMAs
            
        Returns:
            pd.DataFrame: Data with EMAs added
        """
        df = data.copy()
        
        for period in periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
        
        return df
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data (pd.DataFrame): Stock price data
            period (int): Period for RSI calculation
            
        Returns:
            pd.Series: RSI values
        """
        delta = data['Close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data (pd.DataFrame): Stock price data
            fast (int): Fast EMA period
            slow (int): Slow EMA period
            signal (int): Signal line EMA period
            
        Returns:
            pd.DataFrame: DataFrame with MACD values
        """
        df = data.copy()
        
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        result = pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }, index=df.index)
        
        return result
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands
        
        Args:
            data (pd.DataFrame): Stock price data
            period (int): Moving average period
            std_dev (int): Standard deviation multiplier
            
        Returns:
            pd.DataFrame: DataFrame with Bollinger Bands
        """
        df = data.copy()
        
        # Calculate middle band (SMA)
        middle_band = df['Close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['Close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        result = pd.DataFrame({
            'Upper_Band': upper_band,
            'Middle_Band': middle_band,
            'Lower_Band': lower_band
        }, index=df.index)
        
        return result
    
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        Calculate Stochastic Oscillator
        
        Args:
            data (pd.DataFrame): Stock price data
            k_period (int): %K period
            d_period (int): %D period
            
        Returns:
            pd.DataFrame: DataFrame with Stochastic values
        """
        df = data.copy()
        
        # Calculate %K
        lowest_low = df['Low'].rolling(window=k_period).min()
        highest_high = df['High'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (smoothed %K)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        result = pd.DataFrame({
            'K_Percent': k_percent,
            'D_Percent': d_percent
        }, index=df.index)
        
        return result
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volume-based indicators
        
        Args:
            data (pd.DataFrame): Stock price data with volume
            
        Returns:
            pd.DataFrame: DataFrame with volume indicators
        """
        df = data.copy()
        
        # Volume Moving Average
        df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
        
        # On-Balance Volume (OBV)
        obv = []
        obv_value = 0
        
        for i in range(len(df)):
            if i == 0:
                obv.append(0)
            else:
                if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                    obv_value += df['Volume'].iloc[i]
                elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                    obv_value -= df['Volume'].iloc[i]
                obv.append(obv_value)
        
        df['OBV'] = obv
        
        return df
    
    def identify_support_resistance(self, data: pd.DataFrame, window: int = 20) -> dict:
        """
        Identify potential support and resistance levels
        
        Args:
            data (pd.DataFrame): Stock price data
            window (int): Window for identifying peaks and troughs
            
        Returns:
            dict: Dictionary with support and resistance levels
        """
        df = data.copy()
        
        # Find local maxima (resistance)
        resistance_levels = []
        for i in range(window, len(df) - window):
            if df['High'].iloc[i] == max(df['High'].iloc[i-window:i+window+1]):
                resistance_levels.append(df['High'].iloc[i])
        
        # Find local minima (support)
        support_levels = []
        for i in range(window, len(df) - window):
            if df['Low'].iloc[i] == min(df['Low'].iloc[i-window:i+window+1]):
                support_levels.append(df['Low'].iloc[i])
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        support_levels = sorted(list(set(support_levels)))
        
        return {
            'resistance': resistance_levels[:5],  # Top 5 resistance levels
            'support': support_levels[-5:]  # Top 5 support levels
        }
    
    def calculate_price_channels(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calculate price channels (highest high and lowest low over a period)
        
        Args:
            data (pd.DataFrame): Stock price data
            period (int): Period for channel calculation
            
        Returns:
            pd.DataFrame: DataFrame with channel data
        """
        df = data.copy()
        
        upper_channel = df['High'].rolling(window=period).max()
        lower_channel = df['Low'].rolling(window=period).min()
        middle_channel = (upper_channel + lower_channel) / 2
        
        result = pd.DataFrame({
            'Upper_Channel': upper_channel,
            'Lower_Channel': lower_channel,
            'Middle_Channel': middle_channel
        }, index=df.index)
        
        return result
    
    def generate_trading_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate basic trading signals based on multiple indicators
        
        Args:
            data (pd.DataFrame): Stock price data
            
        Returns:
            pd.DataFrame: DataFrame with trading signals
        """
        df = data.copy()
        
        # Calculate indicators
        df = self.calculate_moving_averages(df, [20, 50])
        rsi = self.calculate_rsi(df)
        
        # Generate signals
        signals = []
        
        for i in range(len(df)):
            signal = 'HOLD'
            
            # Simple moving average crossover strategy
            if i > 0:
                # Bullish signal: price crosses above MA20 and RSI < 70
                if (df['Close'].iloc[i] > df['MA_20'].iloc[i] and 
                    df['Close'].iloc[i-1] <= df['MA_20'].iloc[i-1] and 
                    rsi.iloc[i] < 70):
                    signal = 'BUY'
                
                # Bearish signal: price crosses below MA20 and RSI > 30
                elif (df['Close'].iloc[i] < df['MA_20'].iloc[i] and 
                      df['Close'].iloc[i-1] >= df['MA_20'].iloc[i-1] and 
                      rsi.iloc[i] > 30):
                    signal = 'SELL'
            
            signals.append(signal)
        
        df['Signal'] = signals
        df['RSI'] = rsi
        
        return df
