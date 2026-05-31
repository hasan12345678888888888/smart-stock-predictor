import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from agent.stock_agent import StockAgent
from utils.data_processor import DataProcessor
from utils.visualizer import Visualizer

st.set_page_config(
    page_title="Smart Stock-Out Predictor",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid #e94560;
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #a8b2d8;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5c;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #3d0000, #5c0a0a);
        border-left: 4px solid #ff4444;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #ffcccc;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #3d2800, #5c3a0a);
        border-left: 4px solid #ffa500;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #ffe4b3;
    }
    
    .alert-safe {
        background: linear-gradient(135deg, #003d1a, #0a5c2a);
        border-left: 4px solid #00cc66;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #b3ffe0;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e94560;
        border-bottom: 2px solid #e94560;
        padding-bottom: 0.3rem;
        margin-bottom: 1rem;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    div[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="main-header">
    <h1>📦 Smart Stock-Out Predictor</h1>
    <p>AI-Powered Inventory Intelligence for Retail Shops · Hamdard University AI Lab</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    
    critical_threshold = st.slider(
        "🚨 Critical Alert (days)",
        min_value=1, max_value=7, value=3,
        help="Alert when stock will deplete within this many days"
    )
    
    warning_threshold = st.slider(
        "⚠️ Warning Alert (days)",
        min_value=3, max_value=14, value=7,
        help="Warning when stock will deplete within this many days"
    )
    
    st.markdown("---")
    data_source = st.radio(
        "📊 Data Source",
        ["Use Sample Data", "Upload CSV File"],
        help="Choose to use built-in sample data or upload your own"
    )
    
    uploaded_file = None
    if data_source == "Upload CSV File":
        uploaded_file = st.file_uploader(
            "Upload Sales CSV",
            type=["csv"],
            help="CSV with columns: product, day_1, day_2, ..., day_10, current_stock"
        )
        st.markdown("""
        **CSV Format Required:**
        ```
        product, day_1, day_2, ..., day_10, current_stock
        Tapal Tea, 5, 4, 6, ..., 120
        ```
        """)
    
    st.markdown("---")
    st.markdown("### 👥 Team")
    st.markdown("- Inayatullah (3076-2023)")
    st.markdown("- Muhammad Hassan Raza (2903-2023)")
    st.markdown("- Ahsan Ali (3112-2023)")
    st.markdown("---")
    st.markdown("**Faculty of Engineering Sciences**")
    st.markdown("Hamdard University, Karachi")


processor = DataProcessor()
agent = StockAgent(critical_threshold=critical_threshold, warning_threshold=warning_threshold)
visualizer = Visualizer()

if data_source == "Upload CSV File" and uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    df = processor.process_uploaded_data(df_raw)
    st.success(f"✅ Loaded {len(df)} products from uploaded file!")
else:
    df = processor.load_sample_data()

alerts, df_analyzed = agent.analyze(df)

st.markdown('<div class="section-title">📊 Inventory Overview</div>', unsafe_allow_html=True)

total_products = len(df_analyzed)
critical_count = len([a for a in alerts if a['level'] == 'CRITICAL'])
warning_count = len([a for a in alerts if a['level'] == 'WARNING'])
safe_count = total_products - critical_count - warning_count

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Products", total_products)
with col2:
    st.metric("🚨 Critical Stock", critical_count, delta=f"-{critical_count} need reorder" if critical_count > 0 else "All good")
with col3:
    st.metric("⚠️ Low Stock", warning_count)
with col4:
    st.metric("✅ Safe Stock", safe_count)

st.markdown("---")

col_alerts, col_table = st.columns([1, 1.5])

with col_alerts:
    st.markdown('<div class="section-title">🤖 AI Agent Alerts</div>', unsafe_allow_html=True)
    
    if not alerts:
        st.markdown('<div class="alert-safe">✅ <b>All products are well-stocked!</b><br>No immediate action required.</div>', unsafe_allow_html=True)
    else:
        for alert in sorted(alerts, key=lambda x: x['days_remaining']):
            level = alert['level']
            icon = "🚨" if level == "CRITICAL" else "⚠️"
            css_class = "alert-critical" if level == "CRITICAL" else "alert-warning"
            
            st.markdown(f"""
            <div class="{css_class}">
                {icon} <b>[{level}] {alert['product']}</b><br>
                📅 Depletes in <b>{alert['days_remaining']:.1f} days</b><br>
                📦 Current Stock: {alert['current_stock']} units<br>
                🔄 Reorder Recommendation: <b>{alert['reorder_qty']} units</b>
            </div>
            """, unsafe_allow_html=True)

with col_table:
    st.markdown('<div class="section-title">📋 Product Analysis Table</div>', unsafe_allow_html=True)
    
    display_df = df_analyzed[['product', 'current_stock', 'avg_daily_sales', 'days_remaining', 'status']].copy()
    display_df.columns = ['Product', 'Stock', 'Avg Daily Sales', 'Days Left', 'Status']
    display_df['Avg Daily Sales'] = display_df['Avg Daily Sales'].round(2)
    display_df['Days Left'] = display_df['Days Left'].round(1)
    
    def color_status(val):
        if val == 'CRITICAL':
            return 'background-color: #5c0a0a; color: #ffcccc'
        elif val == 'WARNING':
            return 'background-color: #5c3a0a; color: #ffe4b3'
        else:
            return 'background-color: #0a5c2a; color: #b3ffe0'
    
    st.dataframe(display_df, use_container_width=True, height=350)

st.markdown("---")

st.markdown('<div class="section-title">📈 Sales Trend Dashboard</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📉 Daily Consumption Trends", "📊 Stock Duration Comparison", "🔮 Depletion Forecast"])

with tab1:
    fig_trends = visualizer.plot_sales_trends(df_analyzed)
    st.plotly_chart(fig_trends, use_container_width=True)

with tab2:
    fig_bar = visualizer.plot_stock_duration(df_analyzed, critical_threshold, warning_threshold)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    fig_forecast = visualizer.plot_depletion_forecast(df_analyzed)
    st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")

st.markdown('<div class="section-title">🖥️ Agent Evaluation Log</div>', unsafe_allow_html=True)

with st.expander("📟 View Full Terminal Log", expanded=True):
    log_text = agent.get_log()
    st.code(log_text, language="bash")

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#666; font-size:0.8rem;'>"
    "Smart Stock-Out Predictor · Hamdard University AI Lab · "
    "Faculty of Engineering Sciences and Technology, Karachi Pakistan"
    "</p>",
    unsafe_allow_html=True
)
