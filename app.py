import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis
import io
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()

if 'tech_analysis' not in st.session_state:
    st.session_state.tech_analysis = TechnicalAnalysis()

# Main title
st.title("📈 Stock Analysis Dashboard")
st.markdown("---")

# Sidebar for navigation and controls
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose Analysis Type",
    ["Single Stock Analysis", "Stock Comparison", "Technical Analysis"]
)

st.sidebar.markdown("---")

def display_stock_info(stock_info, ticker):
    """Display basic stock information in a formatted way"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Price",
            value=f"${stock_info.get('currentPrice', 'N/A'):.2f}" if stock_info.get('currentPrice') else "N/A",
            delta=f"{stock_info.get('regularMarketChangePercent', 0):.2f}%" if stock_info.get('regularMarketChangePercent') else None
        )
        
    with col2:
        market_cap = stock_info.get('marketCap', 0)
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = "N/A"
        
        st.metric(
            label="Market Cap",
            value=market_cap_str
        )
        
    with col3:
        volume = stock_info.get('volume', 0)
        volume_str = f"{volume:,}" if volume else "N/A"
        st.metric(
            label="Volume",
            value=volume_str
        )

def create_price_chart(data, ticker, period):
    """Create an interactive price chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=f'{ticker} Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title=f'{ticker} Stock Price - {period}',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return fig

def create_volume_chart(data, ticker):
    """Create a volume chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        name=f'{ticker} Volume',
        marker_color='rgba(31, 119, 180, 0.6)'
    ))
    
    fig.update_layout(
        title=f'{ticker} Trading Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        height=300
    )
    
    return fig

# Single Stock Analysis Page
if page == "Single Stock Analysis":
    st.header("🔍 Single Stock Analysis")
    
    # Stock input
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker Symbol", value="AAPL", help="e.g., AAPL, GOOGL, MSFT")
    
    with col2:
        period = st.selectbox(
            "Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
            index=3
        )
    
    if ticker:
        with st.spinner(f"Fetching data for {ticker.upper()}..."):
            # Get stock data
            stock_data = st.session_state.analyzer.get_stock_data(ticker, period)
            stock_info = st.session_state.analyzer.get_stock_info(ticker)
            
            if stock_data is not None and not stock_data.empty:
                # Display stock information
                st.subheader(f"{ticker.upper()} - {stock_info.get('longName', ticker.upper())}")
                display_stock_info(stock_info, ticker.upper())
                
                # Price chart
                st.subheader("📊 Price Chart")
                price_fig = create_price_chart(stock_data, ticker.upper(), period)
                st.plotly_chart(price_fig, use_container_width=True)
                
                # Volume chart
                st.subheader("📈 Volume Chart")
                volume_fig = create_volume_chart(stock_data, ticker.upper())
                st.plotly_chart(volume_fig, use_container_width=True)
                
                # Key metrics table
                st.subheader("📋 Key Financial Metrics")
                metrics_data = {
                    'Metric': ['P/E Ratio', 'EPS', '52 Week High', '52 Week Low', 'Dividend Yield', 'Beta'],
                    'Value': [
                        f"{stock_info.get('trailingPE', 'N/A'):.2f}" if stock_info.get('trailingPE') else "N/A",
                        f"{stock_info.get('trailingEps', 'N/A'):.2f}" if stock_info.get('trailingEps') else "N/A",
                        f"${stock_info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if stock_info.get('fiftyTwoWeekHigh') else "N/A",
                        f"${stock_info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if stock_info.get('fiftyTwoWeekLow') else "N/A",
                        f"{stock_info.get('dividendYield', 0)*100:.2f}%" if stock_info.get('dividendYield') else "N/A",
                        f"{stock_info.get('beta', 'N/A'):.2f}" if stock_info.get('beta') else "N/A"
                    ]
                }
                metrics_df = pd.DataFrame(metrics_data)
                st.table(metrics_df)
                
                # Data export
                st.subheader("💾 Export Data")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = stock_data.to_csv()
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{ticker.upper()}_{period}_data.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Convert to Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        stock_data.to_excel(writer, sheet_name='Stock Data')
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="Download Excel",
                        data=excel_data,
                        file_name=f"{ticker.upper()}_{period}_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
            else:
                st.error(f"❌ Could not fetch data for ticker '{ticker.upper()}'. Please check if the ticker symbol is valid.")

# Stock Comparison Page
elif page == "Stock Comparison":
    st.header("⚖️ Stock Comparison")
    
    # Multiple stock input
    col1, col2 = st.columns([3, 1])
    with col1:
        tickers_input = st.text_input(
            "Enter Stock Tickers (comma-separated)", 
            value="AAPL,GOOGL,MSFT",
            help="e.g., AAPL,GOOGL,MSFT"
        )
    
    with col2:
        period = st.selectbox(
            "Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            key="comparison_period"
        )
    
    if tickers_input:
        tickers = [ticker.strip().upper() for ticker in tickers_input.split(',')]
        
        if len(tickers) > 1:
            with st.spinner("Fetching comparison data..."):
                comparison_data = st.session_state.analyzer.compare_stocks(tickers, period)
                
                if comparison_data is not None and not comparison_data.empty:
                    # Normalize prices to show percentage change
                    normalized_data = comparison_data.div(comparison_data.iloc[0]) * 100
                    
                    # Create comparison chart
                    fig = go.Figure()
                    
                    colors = px.colors.qualitative.Set1
                    for i, ticker in enumerate(tickers):
                        if ticker in normalized_data.columns:
                            fig.add_trace(go.Scatter(
                                x=normalized_data.index,
                                y=normalized_data[ticker],
                                mode='lines',
                                name=ticker,
                                line=dict(color=colors[i % len(colors)], width=2)
                            ))
                    
                    fig.update_layout(
                        title='Stock Price Comparison (Normalized to 100)',
                        xaxis_title='Date',
                        yaxis_title='Normalized Price',
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Performance summary
                    st.subheader("📊 Performance Summary")
                    performance_data = []
                    
                    for ticker in tickers:
                        if ticker in comparison_data.columns:
                            start_price = comparison_data[ticker].iloc[0]
                            end_price = comparison_data[ticker].iloc[-1]
                            total_return = ((end_price - start_price) / start_price) * 100
                            
                            stock_info = st.session_state.analyzer.get_stock_info(ticker)
                            
                            performance_data.append({
                                'Ticker': ticker,
                                'Start Price': f"${start_price:.2f}",
                                'End Price': f"${end_price:.2f}",
                                'Total Return': f"{total_return:.2f}%",
                                'Current P/E': f"{stock_info.get('trailingPE', 'N/A'):.2f}" if stock_info.get('trailingPE') else "N/A"
                            })
                    
                    performance_df = pd.DataFrame(performance_data)
                    st.table(performance_df)
                    
                else:
                    st.error("❌ Could not fetch comparison data. Please check if all ticker symbols are valid.")
        else:
            st.warning("⚠️ Please enter at least 2 ticker symbols for comparison.")

# Technical Analysis Page
elif page == "Technical Analysis":
    st.header("🔬 Technical Analysis")
    
    # Stock input for technical analysis
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker Symbol", value="AAPL", key="tech_ticker")
    
    with col2:
        period = st.selectbox(
            "Time Period",
            ["3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            key="tech_period"
        )
    
    if ticker:
        with st.spinner(f"Performing technical analysis for {ticker.upper()}..."):
            # Get stock data
            stock_data = st.session_state.analyzer.get_stock_data(ticker, period)
            
            if stock_data is not None and not stock_data.empty:
                # Calculate technical indicators
                tech_data = st.session_state.tech_analysis.calculate_moving_averages(stock_data)
                
                # Create technical analysis chart
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=[f'{ticker.upper()} Price with Moving Averages', 'Volume'],
                    row_width=[0.7, 0.3]
                )
                
                # Price and moving averages
                fig.add_trace(
                    go.Scatter(x=tech_data.index, y=tech_data['Close'], 
                              name='Close Price', line=dict(color='blue')),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=tech_data.index, y=tech_data['MA_20'], 
                              name='20-day MA', line=dict(color='orange')),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=tech_data.index, y=tech_data['MA_50'], 
                              name='50-day MA', line=dict(color='red')),
                    row=1, col=1
                )
                
                # Volume
                fig.add_trace(
                    go.Bar(x=tech_data.index, y=tech_data['Volume'], 
                           name='Volume', marker_color='rgba(31, 119, 180, 0.6)'),
                    row=2, col=1
                )
                
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Technical indicators summary
                st.subheader("📈 Technical Indicators")
                
                current_price = tech_data['Close'].iloc[-1]
                ma_20 = tech_data['MA_20'].iloc[-1]
                ma_50 = tech_data['MA_50'].iloc[-1]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"${current_price:.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="20-day MA",
                        value=f"${ma_20:.2f}",
                        delta=f"{((current_price - ma_20) / ma_20 * 100):.2f}%"
                    )
                
                with col3:
                    st.metric(
                        label="50-day MA",
                        value=f"${ma_50:.2f}",
                        delta=f"{((current_price - ma_50) / ma_50 * 100):.2f}%"
                    )
                
                # Technical analysis signals
                st.subheader("🎯 Trading Signals")
                
                signals = []
                
                if current_price > ma_20 and current_price > ma_50:
                    signals.append("✅ Price above both 20-day and 50-day moving averages (Bullish)")
                elif current_price < ma_20 and current_price < ma_50:
                    signals.append("❌ Price below both 20-day and 50-day moving averages (Bearish)")
                else:
                    signals.append("⚠️ Mixed signals - Price between moving averages")
                
                if ma_20 > ma_50:
                    signals.append("✅ 20-day MA above 50-day MA (Short-term bullish trend)")
                else:
                    signals.append("❌ 20-day MA below 50-day MA (Short-term bearish trend)")
                
                for signal in signals:
                    st.write(signal)
                
                # RSI calculation
                rsi_data = st.session_state.tech_analysis.calculate_rsi(stock_data)
                current_rsi = rsi_data.iloc[-1]
                
                st.subheader("📊 RSI (Relative Strength Index)")
                st.metric(
                    label="Current RSI",
                    value=f"{current_rsi:.2f}"
                )
                
                if current_rsi > 70:
                    st.write("🔴 RSI indicates overbought conditions")
                elif current_rsi < 30:
                    st.write("🟢 RSI indicates oversold conditions")
                else:
                    st.write("🟡 RSI indicates neutral conditions")
                
            else:
                st.error(f"❌ Could not fetch data for ticker '{ticker.upper()}'. Please check if the ticker symbol is valid.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📊 Stock Analysis Dashboard | Data provided by Yahoo Finance via yfinance</p>
        <p><em>Disclaimer: This tool is for educational purposes only. Not financial advice.</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)
