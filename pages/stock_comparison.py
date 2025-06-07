import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()

if 'tech_analysis' not in st.session_state:
    st.session_state.tech_analysis = TechnicalAnalysis()

def render_stock_comparison_page():
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

render_stock_comparison_page() 