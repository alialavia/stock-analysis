import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_options_analysis_page():
    st.header("📊 Options Analysis")
    
    # Stock input for options analysis
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker Symbol", value="AAPL", key="options_ticker")
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Open Interest Value", "Detailed Options Chain"],
            key="options_analysis_type"
        )
    
    if ticker:
        with st.spinner(f"Fetching options data for {ticker.upper()}..."):
            # Get options data
            options_data = st.session_state.analyzer.get_options_data(ticker)
            
            if options_data and 'expiry_dates' in options_data:
                # Calculate interest values
                interest_values = st.session_state.analyzer.calculate_options_interest_value(options_data)
                
                if interest_values:
                    if analysis_type == "Open Interest Value":
                        st.subheader("📈 Open Interest × Last Price by Expiry Date")
                        
                        # Create tabs for calls and puts
                        tab1, tab2 = st.tabs(["📞 Calls", "📉 Puts"])
                        
                        with tab1:
                            if isinstance(interest_values['calls_summary'], pd.DataFrame) and not interest_values['calls_summary'].empty:
                                # Create line chart for calls to better show anomalies
                                fig_calls = go.Figure()
                                
                                fig_calls.add_trace(go.Scatter(
                                    x=interest_values['calls_summary']['expiry'],
                                    y=interest_values['calls_summary']['total_interest_value'],
                                    mode='lines+markers',
                                    name='Calls Interest Value',
                                    line=dict(color='green', width=3),
                                    marker=dict(size=8, color='green'),
                                    customdata=list(zip(
                                        interest_values['calls_summary']['total_open_interest'],
                                        interest_values['calls_summary']['avg_last_price'],
                                        interest_values['calls_summary']['total_volume'],
                                        interest_values['calls_summary']['avg_volume']
                                    )),
                                    hovertemplate='<b>Expiry:</b> %{x}<br>' +
                                                '<b>Total Interest Value:</b> $%{y:,.0f}<br>' +
                                                '<b>Total Open Interest:</b> %{customdata[0]:,}<br>' +
                                                '<b>Avg Last Price:</b> $%{customdata[1]:.2f}<br>' +
                                                '<b>Total Volume:</b> %{customdata[2]:,}<br>' +
                                                '<b>Avg Volume:</b> %{customdata[3]:,.0f}<extra></extra>'
                                ))
                                
                                # Add reference line for average to help identify anomalies
                                avg_value = interest_values['calls_summary']['total_interest_value'].mean()
                                fig_calls.add_hline(
                                    y=avg_value,
                                    line_dash="dash",
                                    line_color="gray",
                                    annotation_text=f"Average: ${avg_value:,.0f}"
                                )
                                
                                fig_calls.update_layout(
                                    title='Calls: Open Interest × Last Price by Expiry (Line shows anomalies better)',
                                    xaxis_title='Expiry Date',
                                    yaxis_title='Total Interest Value ($)',
                                    height=400,
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig_calls, use_container_width=True)
                                
                                # Summary table for calls
                                st.subheader("Calls Summary")
                                calls_display = interest_values['calls_summary'].copy()
                                
                                # Format the numeric columns
                                calls_display['total_interest_value'] = calls_display['total_interest_value'].apply(lambda x: f"${x:,.0f}")
                                calls_display['total_open_interest'] = calls_display['total_open_interest'].apply(lambda x: f"{x:,}")
                                calls_display['avg_last_price'] = calls_display['avg_last_price'].apply(lambda x: f"${x:.2f}")
                                calls_display['total_volume'] = calls_display['total_volume'].apply(lambda x: f"{x:,}")
                                calls_display['avg_volume'] = calls_display['avg_volume'].apply(lambda x: f"{x:,.0f}")
                                
                                # Rename columns to be more user-friendly
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
                            else:
                                st.info("No calls data available for this ticker.")
                        
                        with tab2:
                            if isinstance(interest_values['puts_summary'], pd.DataFrame) and not interest_values['puts_summary'].empty:
                                # Create line chart for puts to better show anomalies
                                fig_puts = go.Figure()
                                
                                fig_puts.add_trace(go.Scatter(
                                    x=interest_values['puts_summary']['expiry'],
                                    y=interest_values['puts_summary']['total_interest_value'],
                                    mode='lines+markers',
                                    name='Puts Interest Value',
                                    line=dict(color='red', width=3),
                                    marker=dict(size=8, color='red'),
                                    customdata=list(zip(
                                        interest_values['puts_summary']['total_open_interest'],
                                        interest_values['puts_summary']['avg_last_price'],
                                        interest_values['puts_summary']['total_volume'],
                                        interest_values['puts_summary']['avg_volume']
                                    )),
                                    hovertemplate='<b>Expiry:</b> %{x}<br>' +
                                                '<b>Total Interest Value:</b> $%{y:,.0f}<br>' +
                                                '<b>Total Open Interest:</b> %{customdata[0]:,}<br>' +
                                                '<b>Avg Last Price:</b> $%{customdata[1]:.2f}<br>' +
                                                '<b>Total Volume:</b> %{customdata[2]:,}<br>' +
                                                '<b>Avg Volume:</b> %{customdata[3]:,.0f}<extra></extra>'
                                ))
                                
                                # Add reference line for average to help identify anomalies
                                avg_value = interest_values['puts_summary']['total_interest_value'].mean()
                                fig_puts.add_hline(
                                    y=avg_value,
                                    line_dash="dash",
                                    line_color="gray",
                                    annotation_text=f"Average: ${avg_value:,.0f}"
                                )
                                
                                fig_puts.update_layout(
                                    title='Puts: Open Interest × Last Price by Expiry (Line shows anomalies better)',
                                    xaxis_title='Expiry Date',
                                    yaxis_title='Total Interest Value ($)',
                                    height=400,
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig_puts, use_container_width=True)
                                
                                # Summary table for puts
                                st.subheader("Puts Summary")
                                puts_display = interest_values['puts_summary'].copy()
                                
                                # Format the numeric columns
                                puts_display['total_interest_value'] = puts_display['total_interest_value'].apply(lambda x: f"${x:,.0f}")
                                puts_display['total_open_interest'] = puts_display['total_open_interest'].apply(lambda x: f"{x:,}")
                                puts_display['avg_last_price'] = puts_display['avg_last_price'].apply(lambda x: f"${x:.2f}")
                                puts_display['total_volume'] = puts_display['total_volume'].apply(lambda x: f"{x:,}")
                                puts_display['avg_volume'] = puts_display['avg_volume'].apply(lambda x: f"{x:,.0f}")
                                
                                # Rename columns to be more user-friendly
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
                            else:
                                st.info("No puts data available for this ticker.")
                    
                    elif analysis_type == "Detailed Options Chain":
                        st.subheader("🔗 Detailed Options Chain")
                        
                        # Expiry date selector
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
                                    
                                    # Display key columns
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
                                    
                                    # Display key columns
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
                    st.warning("⚠️ Could not calculate options interest values. The ticker may not have options data available.")
            
            else:
                st.error(f"❌ No options data available for ticker '{ticker.upper()}'. This ticker may not have listed options.")

render_options_analysis_page() 