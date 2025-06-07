import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()

if 'tech_analysis' not in st.session_state:
    st.session_state.tech_analysis = TechnicalAnalysis()

def render_technical_analysis_page():
    st.header("🔬 Technical Analysis")

    # Stock input for technical analysis
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input(
            "Enter Stock Ticker Symbol", value="AAPL", key="tech_ticker"
        )

    with col2:
        period = st.selectbox(
            "Time Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2, key="tech_period"
        )

    if ticker:
        with st.spinner(f"Performing technical analysis for {ticker.upper()}..."):
            # Get stock data
            stock_data = st.session_state.analyzer.get_stock_data(ticker, period)

            if stock_data is not None and not stock_data.empty:
                # Calculate technical indicators
                tech_data = st.session_state.tech_analysis.calculate_moving_averages(
                    stock_data
                )

                # Create technical analysis chart
                fig = make_subplots(
                    rows=2,
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=[
                        f"{ticker.upper()} Price with Moving Averages",
                        "Volume",
                    ],
                    row_width=[0.7, 0.3],
                )

                # Price and moving averages
                fig.add_trace(
                    go.Scatter(
                        x=tech_data.index,
                        y=tech_data["Close"],
                        name="Close Price",
                        line=dict(color="blue"),
                    ),
                    row=1,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=tech_data.index,
                        y=tech_data["MA_20"],
                        name="20-day MA",
                        line=dict(color="orange"),
                    ),
                    row=1,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=tech_data.index,
                        y=tech_data["MA_50"],
                        name="50-day MA",
                        line=dict(color="red"),
                    ),
                    row=1,
                    col=1,
                )

                # Volume
                fig.add_trace(
                    go.Bar(
                        x=tech_data.index,
                        y=tech_data["Volume"],
                        name="Volume",
                        marker_color="rgba(31, 119, 180, 0.6)",
                    ),
                    row=2,
                    col=1,
                )

                fig.update_layout(height=600, showlegend=True, hovermode="x unified")

                st.plotly_chart(fig, use_container_width=True)

                # Technical indicators summary
                st.subheader("📈 Technical Indicators")

                current_price = tech_data["Close"].iloc[-1]
                ma_20 = tech_data["MA_20"].iloc[-1]
                ma_50 = tech_data["MA_50"].iloc[-1]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(label="Current Price", value=f"${current_price:.2f}")

                with col2:
                    st.metric(
                        label="20-day MA",
                        value=f"${ma_20:.2f}",
                        delta=f"{((current_price - ma_20) / ma_20 * 100):.2f}%",
                    )

                with col3:
                    st.metric(
                        label="50-day MA",
                        value=f"${ma_50:.2f}",
                        delta=f"{((current_price - ma_50) / ma_50 * 100):.2f}%",
                    )

                # Technical analysis signals
                st.subheader("🎯 Trading Signals")

                signals = []

                if current_price > ma_20 and current_price > ma_50:
                    signals.append(
                        "✅ Price above both 20-day and 50-day moving averages (Bullish)"
                    )
                elif current_price < ma_20 and current_price < ma_50:
                    signals.append(
                        "❌ Price below both 20-day and 50-day moving averages (Bearish)"
                    )
                else:
                    signals.append("⚠️ Mixed signals - Price between moving averages")

                if ma_20 > ma_50:
                    signals.append(
                        "✅ 20-day MA above 50-day MA (Short-term bullish trend)"
                    )
                else:
                    signals.append(
                        "❌ 20-day MA below 50-day MA (Short-term bearish trend)"
                    )

                for signal in signals:
                    st.write(signal)

                # RSI calculation
                rsi_data = st.session_state.tech_analysis.calculate_rsi(stock_data)
                current_rsi = rsi_data.iloc[-1]

                st.subheader("📊 RSI (Relative Strength Index)")
                st.metric(label="Current RSI", value=f"{current_rsi:.2f}")

                if current_rsi > 70:
                    st.write("🔴 RSI indicates overbought conditions")
                elif current_rsi < 30:
                    st.write("🟢 RSI indicates oversold conditions")
                else:
                    st.write("🟡 RSI indicates neutral conditions")

            else:
                st.error(
                    f"❌ Could not fetch data for ticker '{ticker.upper()}'. Please check if the ticker symbol is valid."
                )

render_technical_analysis_page()
