import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from utils import (
    SEMICONDUCTOR_TICKERS, 
    fetch_stock_data, 
    calculate_correlation,
    get_company_info,
    get_price_changes
)

# Page configuration
st.set_page_config(
    page_title="Semiconductor Stocks Analysis",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("Semiconductor Stocks Correlation Analysis")
st.markdown("""
This application analyzes the correlation between major semiconductor stocks listed on NYSE.
Select different timeframes and explore the relationships between stock price movements.
""")

# Timeframe selection
timeframe = st.selectbox(
    "Select Analysis Timeframe",
    options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
    index=3
)

# Fetch and process data
with st.spinner('Fetching stock data...'):
    stock_data = fetch_stock_data(SEMICONDUCTOR_TICKERS, timeframe)
    
    if stock_data is None:
        st.error("Failed to fetch stock data. Please try again later.")
        st.stop()
    
    correlation_matrix = calculate_correlation(stock_data)
    price_changes = get_price_changes(stock_data)

# Display price trends
st.header("Stock Price Trends")
fig_trends = px.line(stock_data, title="Stock Price Evolution")
fig_trends.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    showlegend=True
)
st.plotly_chart(fig_trends, use_container_width=True)

# Display price changes
st.header("Price Changes")
if price_changes:
    cols = st.columns(5)
    for idx, (ticker, changes) in enumerate(price_changes.items()):
        with cols[idx % 5]:
            st.metric(
                ticker,
                f"${changes['final_price']}",
                f"{changes['percent_change']}%"
            )

# Correlation Analysis
st.header("Correlation Analysis")

# Correlation Matrix using Plotly
fig_corr = px.imshow(
    correlation_matrix,
    color_continuous_scale='RdBu',
    aspect='auto',
    title='Correlation Heatmap'
)
fig_corr.update_layout(
    xaxis_title="Stock Ticker",
    yaxis_title="Stock Ticker"
)
st.plotly_chart(fig_corr, use_container_width=True)

# Company Information
st.header("Company Information")
selected_company = st.selectbox("Select a company", SEMICONDUCTOR_TICKERS)

company_info = get_company_info(selected_company)
if company_info:
    st.subheader(company_info['name'])
    st.write("**Sector:** ", company_info['sector'])
    st.write("**Industry:** ", company_info['industry'])
    st.write("**Website:** ", company_info['website'])
    st.write("**Description:**")
    st.write(company_info['description'])
else:
    st.error(f"Could not fetch information for {selected_company}")

# Footer
st.markdown("---")
st.markdown("""
*Data provided by Yahoo Finance. This tool is for informational purposes only and 
should not be considered as financial advice.*
""")
