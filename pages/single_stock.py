import streamlit as st
import pandas as pd
from utils import display_stock_info, create_price_chart, create_volume_chart
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()

if 'tech_analysis' not in st.session_state:
    st.session_state.tech_analysis = TechnicalAnalysis()

def render_single_stock_page():
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
                    # Convert to Excel (simplified to avoid timezone issues)
                    csv_data = stock_data.to_csv()
                    
                    st.download_button(
                        label="Download Excel (CSV)",
                        data=csv_data,
                        file_name=f"{ticker.upper()}_{period}_data.csv",
                        mime="text/csv"
                    )
                
            else:
                st.error(f"❌ Could not fetch data for ticker '{ticker.upper()}'. Please check if the ticker symbol is valid.")

render_single_stock_page() 