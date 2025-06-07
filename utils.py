import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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