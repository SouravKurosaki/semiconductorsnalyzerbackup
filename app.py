import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import time
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

# Initialize session state for auto refresh
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Custom CSS with dark mode support
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
    /* Custom styling for metrics */
    .stMetric {
        background-color: var(--background-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    /* Dark mode specific styles */
    [data-theme="dark"] .stMetric {
        --background-color: rgba(255, 255, 255, 0.1);
        --border-color: rgba(255, 255, 255, 0.2);
        color: white !important;
    }
    /* Light mode specific styles */
    [data-theme="light"] .stMetric {
        --background-color: rgba(240, 242, 246, 0.8);
        --border-color: rgba(0, 0, 0, 0.1);
        color: black !important;
    }
    /* Ensure text contrast */
    .metric-value, .metric-label {
        color: inherit !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("Analysis Settings")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=True)
st.session_state.auto_refresh = auto_refresh

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

# Auto-refresh logic
if st.session_state.auto_refresh and time.time() - st.session_state.last_refresh >= 2:
    st.session_state.last_refresh = time.time()
    st.rerun()

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

# Display last update time
st.sidebar.text(f"Last updated: {time.strftime('%H:%M:%S')}")

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
                rsi_value = technical_indicators[ticker]['RSI']
                ma20_value = technical_indicators[ticker]['MA20']

                # RSI color coding
                rsi_color = (
                    "🔴" if rsi_value > 70 else
                    "🟢" if rsi_value < 30 else
                    "⚪"
                )

                st.markdown(f"""
                    <div class="stMetric">
                        <h3>{ticker}</h3>
                        <p class="metric-value">RSI: {rsi_color} {rsi_value:.2f}</p>
                        <p class="metric-value">MA20: ${ma20_value:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)

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