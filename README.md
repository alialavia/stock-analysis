# Stock Analysis Dashboard 📈

A powerful web-based dashboard for analyzing stocks, comparing multiple stocks, performing technical analysis, and analyzing options data. Built with Python and Streamlit.

## Features

- **Single Stock Analysis**: View detailed stock information, price charts, volume charts, and key financial metrics
- **Stock Comparison**: Compare multiple stocks' performance over time
- **Technical Analysis**: Analyze moving averages, RSI, and trading signals
- **Options Analysis**: View open interest, options chains, and detailed options data

## Prerequisites

Before you begin, you'll need to install:

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **UV Package Manager**
   - Download from [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/StockAnalyzer.git
   cd StockAnalyzer
   ```

2. **Create and activate a virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

## Running the Application

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the dashboard**
   - Open your web browser
   - Go to http://localhost:8501

## How to Use

### Single Stock Analysis
1. Enter a stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. Select a time period
3. View price charts, volume data, and key metrics
4. Download data in CSV format

### Stock Comparison
1. Enter multiple stock tickers separated by commas
2. Select a time period
3. View normalized price comparison and performance metrics

### Technical Analysis
1. Enter a stock ticker
2. View moving averages (20-day and 50-day)
3. Check RSI (Relative Strength Index)
4. Review trading signals

### Options Analysis
1. Enter a stock ticker
2. Choose between:
   - Open Interest Value: View options interest by expiry date
   - Detailed Options Chain: View specific options contracts

## How It Works

### Price Data
- Stock price data is fetched from Yahoo Finance using the yfinance library
- Data includes Open, High, Low, Close prices and Volume
- Charts are created using Plotly for interactive visualization

### Technical Indicators
- **Moving Averages**: Calculated using 20-day and 50-day periods
  - 20-day MA = Average of last 20 closing prices
  - 50-day MA = Average of last 50 closing prices
- **RSI (Relative Strength Index)**:
  - Calculated using 14-day period
  - Values above 70 indicate overbought conditions
  - Values below 30 indicate oversold conditions

### Options Analysis
- Options data is fetched from Yahoo Finance
- Open Interest Value = Open Interest × Last Price
- Options chains are organized by expiry date and strike price

## Troubleshooting

1. **Data not loading**
   - Check your internet connection
   - Verify the stock ticker symbol is correct
   - Some stocks may have limited data availability

2. **Application not starting**
   - Ensure Python is installed correctly
   - Verify all dependencies are installed
   - Check if port 8501 is available

## Disclaimer

This tool is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.

## Contributing

Feel free to submit issues and enhancement requests! 