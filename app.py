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
    get_price_changes,
    calculate_technical_indicators,
    normalize_data
)

# Page configuration
st.set_page_config(
    page_title="Semiconductor Stocks Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("Analysis Settings")

# Timeframe selection with custom periods
timeframe = st.sidebar.selectbox(
    "Select Analysis Timeframe",
    options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
    index=3
)

# Stock selection for comparison
selected_stocks = st.sidebar.multiselect(
    "Select Stocks to Compare",
    options=SEMICONDUCTOR_TICKERS,
    default=SEMICONDUCTOR_TICKERS[:3]
)

if not selected_stocks:
    selected_stocks = SEMICONDUCTOR_TICKERS[:3]
    st.sidebar.warning("At least one stock must be selected. Defaulting to first three stocks.")

# Fetch and process data
with st.spinner('Fetching stock data...'):
    stock_data, volume_data = fetch_stock_data(selected_stocks, timeframe)

    if stock_data is None:
        st.error("Failed to fetch stock data. Please try again later.")
        st.stop()

    correlation_matrix = calculate_correlation(stock_data)
    price_changes = get_price_changes(stock_data)
    technical_indicators = calculate_technical_indicators(stock_data)
    normalized_data = normalize_data(stock_data)

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Price Analysis",
    "🔄 Correlation Analysis",
    "📊 Volume Analysis",
    "ℹ️ Company Information"
])

with tab1:
    st.header("Stock Price Analysis")

    # Price chart type selector
    chart_type = st.radio(
        "Select Chart Type",
        options=["Absolute Prices", "Normalized (Base 100)"],
        horizontal=True
    )

    # Display selected chart
    if chart_type == "Absolute Prices":
        fig_trends = px.line(stock_data, title="Stock Price Evolution")
    else:
        fig_trends = px.line(normalized_data, title="Normalized Price Evolution (Base 100)")

    fig_trends.update_layout(
        height=600,
        xaxis_title="Date",
        yaxis_title="Price (USD)" if chart_type == "Absolute Prices" else "Normalized Price",
        hovermode="x unified"
    )
    st.plotly_chart(fig_trends, use_container_width=True)

    # Technical Indicators
    if technical_indicators:
        st.subheader("Technical Indicators")
        indicator_cols = st.columns(len(selected_stocks))
        for idx, ticker in enumerate(selected_stocks):
            with indicator_cols[idx]:
                st.metric(
                    f"{ticker} Indicators",
                    f"RSI: {technical_indicators[ticker]['RSI']:.2f}",
                    f"MA20: ${technical_indicators[ticker]['MA20']:.2f}"
                )

with tab2:
    st.header("Correlation Analysis")

    # Correlation Matrix using Plotly
    fig_corr = px.imshow(
        correlation_matrix,
        color_continuous_scale='RdBu',
        aspect='auto',
        title='Correlation Heatmap'
    )
    fig_corr.update_layout(
        height=500,
        xaxis_title="Stock Ticker",
        yaxis_title="Stock Ticker"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Correlation explanation
    st.markdown("""
        ### Understanding Correlation Values
        - **1.0**: Perfect positive correlation
        - **0.0**: No correlation
        - **-1.0**: Perfect negative correlation

        Stocks with high positive correlation tend to move in the same direction,
        while negative correlation indicates opposite movements.
    """)

with tab3:
    st.header("Volume Analysis")

    # Volume chart
    fig_volume = px.bar(
        volume_data,
        title="Trading Volume Over Time",
        barmode='group'
    )
    fig_volume.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Volume",
        hovermode="x unified"
    )
    st.plotly_chart(fig_volume, use_container_width=True)

with tab4:
    st.header("Company Information")

    # Company selector
    selected_company = st.selectbox("Select a company", selected_stocks)

    company_info = get_company_info(selected_company)
    if company_info:
        # Company metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Market Cap", f"${company_info['market_cap']:,.0f}" if isinstance(company_info['market_cap'], (int, float)) else "N/A")
        with col2:
            st.metric("P/E Ratio", f"{company_info['pe_ratio']:.2f}" if isinstance(company_info['pe_ratio'], (int, float)) else "N/A")
        with col3:
            st.metric("Dividend Yield", f"{company_info['dividend_yield']:.2%}" if isinstance(company_info['dividend_yield'], (int, float)) else "N/A")

        # Company details
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