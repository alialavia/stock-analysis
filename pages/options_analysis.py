import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()

if 'tech_analysis' not in st.session_state:
    st.session_state.tech_analysis = TechnicalAnalysis()

def render_options_analysis_page():
    st.header("📊 Options Analysis")
    
    # Multi-ticker input for options analysis
    col1, col2 = st.columns([2, 1])
    with col1:
        tickers_input = st.text_input(
            "Enter Stock Ticker Symbol(s)", value="AAPL", key="options_ticker",
            help="You can enter multiple tickers separated by commas (e.g., AAPL, MSFT, GOOGL)"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Open Interest Value", "Detailed Options Chain"],
            key="options_analysis_type"
        )
    
    if tickers_input:
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if not tickers:
            st.warning("Please enter at least one ticker symbol.")
            return
        
        with st.spinner(f"Fetching options data for {', '.join(tickers)}..."):
            all_interest_values = {}
            all_options_data = {}
            errors = []
            for ticker in tickers:
                options_data = st.session_state.analyzer.get_options_data(ticker)
                if options_data and 'expiry_dates' in options_data:
                    interest_values = st.session_state.analyzer.calculate_options_interest_value(options_data)
                    if interest_values:
                        all_interest_values[ticker] = interest_values
                        all_options_data[ticker] = options_data
                    else:
                        errors.append(f"Could not calculate options interest values for {ticker}.")
                else:
                    errors.append(f"No options data available for ticker '{ticker}'.")
            
            if analysis_type == "Open Interest Value":
                st.subheader("📈 Open Interest × Last Price by Expiry Date (Multiple Tickers)")
                tab1, tab2 = st.tabs(["📞 Calls", "📉 Puts"])
                color_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                # Calls tab
                with tab1:
                    fig_calls = go.Figure()
                    for i, (ticker, interest_values) in enumerate(all_interest_values.items()):
                        calls_summary = interest_values['calls_summary']
                        if isinstance(calls_summary, pd.DataFrame) and not calls_summary.empty:
                            fig_calls.add_trace(go.Scatter(
                                x=calls_summary['expiry'],
                                y=calls_summary['total_interest_value'],
                                mode='lines+markers',
                                name=f'{ticker} Calls',
                                line=dict(color=color_palette[i % len(color_palette)], width=3),
                                marker=dict(size=8, color=color_palette[i % len(color_palette)]),
                                customdata=list(zip(
                                    calls_summary['expiry'],
                                    calls_summary['total_interest_value'],
                                    calls_summary['total_open_interest'],
                                    calls_summary['avg_last_price'],
                                    calls_summary['total_volume'],
                                    calls_summary['avg_volume'],
                                )),
                                hovertemplate='<b>Expiry Date:</b> %{customdata[0]}<br>' +
                                              '<b>Total Interest Value:</b> $%{customdata[1]:,.0f}<br>' +
                                              '<b>Total Open Interest:</b> %{customdata[2]:,}<br>' +
                                              '<b>Avg Last Price:</b> $%{customdata[3]:.2f}<br>' +
                                              '<b>Total Volume:</b> %{customdata[4]:,}<br>' +
                                              '<b>Avg Volume:</b> %{customdata[5]:,.0f}<extra></extra>'
                            ))
                    fig_calls.update_layout(
                        title='Calls: Open Interest × Last Price by Expiry (Multiple Tickers)',
                        xaxis_title='Expiry Date',
                        yaxis_title='Total Interest Value ($)',
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig_calls, use_container_width=True)
                    # Show summary tables for each ticker
                    for ticker, interest_values in all_interest_values.items():
                        calls_summary = interest_values['calls_summary']
                        if isinstance(calls_summary, pd.DataFrame) and not calls_summary.empty:
                            st.subheader(f"Calls Summary for {ticker}")
                            calls_display = calls_summary.copy()
                            calls_display['total_interest_value'] = calls_display['total_interest_value'].apply(lambda x: f"${x:,.0f}")
                            calls_display['total_open_interest'] = calls_display['total_open_interest'].apply(lambda x: f"{x:,}")
                            calls_display['avg_last_price'] = calls_display['avg_last_price'].apply(lambda x: f"${x:.2f}")
                            calls_display['total_volume'] = calls_display['total_volume'].apply(lambda x: f"{x:,}")
                            calls_display['avg_volume'] = calls_display['avg_volume'].apply(lambda x: f"{x:,.0f}")
                            column_mapping = {
                                'expiry': 'Expiry Date',
                                'total_open_interest': 'Total Open Interest',
                                'total_interest_value': 'Total Interest Value',
                                'avg_last_price': 'Avg Last Price',
                                'total_volume': 'Total Volume',
                                'avg_volume': 'Avg Volume'
                            }
                            calls_display = calls_display.rename(columns=column_mapping)
                            st.table(calls_display)
                # Puts tab
                with tab2:
                    fig_puts = go.Figure()
                    for i, (ticker, interest_values) in enumerate(all_interest_values.items()):
                        puts_summary = interest_values['puts_summary']
                        if isinstance(puts_summary, pd.DataFrame) and not puts_summary.empty:
                            fig_puts.add_trace(go.Scatter(
                                x=puts_summary['expiry'],
                                y=puts_summary['total_interest_value'],
                                mode='lines+markers',
                                name=f'{ticker} Puts',
                                line=dict(color=color_palette[i % len(color_palette)], width=3, dash='dot'),
                                marker=dict(size=8, color=color_palette[i % len(color_palette)]),
                                customdata=list(zip(
                                    puts_summary['expiry'],
                                    puts_summary['total_interest_value'],
                                    puts_summary['total_open_interest'],
                                    puts_summary['avg_last_price'],
                                    puts_summary['total_volume'],
                                    puts_summary['avg_volume'],
                                )),
                                hovertemplate='<b>Expiry Date:</b> %{customdata[0]}<br>' +
                                              '<b>Total Interest Value:</b> $%{customdata[1]:,.0f}<br>' +
                                              '<b>Total Open Interest:</b> %{customdata[2]:,}<br>' +
                                              '<b>Avg Last Price:</b> $%{customdata[3]:.2f}<br>' +
                                              '<b>Total Volume:</b> %{customdata[4]:,}<br>' +
                                              '<b>Avg Volume:</b> %{customdata[5]:,.0f}<extra></extra>'
                            ))
                    fig_puts.update_layout(
                        title='Puts: Open Interest × Last Price by Expiry (Multiple Tickers)',
                        xaxis_title='Expiry Date',
                        yaxis_title='Total Interest Value ($)',
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig_puts, use_container_width=True)
                    # Show summary tables for each ticker
                    for ticker, interest_values in all_interest_values.items():
                        puts_summary = interest_values['puts_summary']
                        if isinstance(puts_summary, pd.DataFrame) and not puts_summary.empty:
                            st.subheader(f"Puts Summary for {ticker}")
                            puts_display = puts_summary.copy()
                            puts_display['total_interest_value'] = puts_display['total_interest_value'].apply(lambda x: f"${x:,.0f}")
                            puts_display['total_open_interest'] = puts_display['total_open_interest'].apply(lambda x: f"{x:,}")
                            puts_display['avg_last_price'] = puts_display['avg_last_price'].apply(lambda x: f"${x:.2f}")
                            puts_display['total_volume'] = puts_display['total_volume'].apply(lambda x: f"{x:,}")
                            puts_display['avg_volume'] = puts_display['avg_volume'].apply(lambda x: f"{x:,.0f}")
                            column_mapping = {
                                'expiry': 'Expiry Date',
                                'total_open_interest': 'Total Open Interest',
                                'total_interest_value': 'Total Interest Value',
                                'avg_last_price': 'Avg Last Price',
                                'total_volume': 'Total Volume',
                                'avg_volume': 'Avg Volume'
                            }
                            puts_display = puts_display.rename(columns=column_mapping)
                            st.table(puts_display)
                if errors:
                    for err in errors:
                        st.info(err)
            elif analysis_type == "Detailed Options Chain":
                if len(tickers) > 1:
                    st.info("Detailed Options Chain is only available for a single ticker at a time. Please enter one ticker.")
                else:
                    ticker = tickers[0]
                    options_data = all_options_data.get(ticker)
                    interest_values = all_interest_values.get(ticker)
                    if options_data and interest_values:
                        st.subheader("🔗 Detailed Options Chain")
                        selected_expiry = st.selectbox(
                            "Select Expiry Date",
                            options_data['expiry_dates'],
                            key="selected_expiry"
                        )
                        if selected_expiry:
                            tab1, tab2 = st.tabs(["📞 Calls", "📉 Puts"])
                            with tab1:
                                if selected_expiry in interest_values['calls_detail']:
                                    calls_detail = interest_values['calls_detail'][selected_expiry]
                                    display_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'interestValue']
                                    available_cols = [col for col in display_cols if col in calls_detail.columns]
                                    if available_cols:
                                        calls_display = calls_detail[available_cols].copy()
                                        calls_display.columns = [col.title().replace('Interest', ' Interest') for col in available_cols]
                                        st.dataframe(calls_display, use_container_width=True)
                                    else:
                                        st.info("No detailed calls data available for this expiry.")
                                else:
                                    st.info("No calls data available for this expiry.")
                            with tab2:
                                if selected_expiry in interest_values['puts_detail']:
                                    puts_detail = interest_values['puts_detail'][selected_expiry]
                                    display_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'interestValue']
                                    available_cols = [col for col in display_cols if col in puts_detail.columns]
                                    if available_cols:
                                        puts_display = puts_detail[available_cols].copy()
                                        puts_display.columns = [col.title().replace('Interest', ' Interest') for col in available_cols]
                                        st.dataframe(puts_display, use_container_width=True)
                                    else:
                                        st.info("No detailed puts data available for this expiry.")
                                else:
                                    st.info("No puts data available for this expiry.")
                    else:
                        st.warning("No options data available for the selected ticker.")

render_options_analysis_page() 