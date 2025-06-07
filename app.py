import streamlit as st
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis

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
