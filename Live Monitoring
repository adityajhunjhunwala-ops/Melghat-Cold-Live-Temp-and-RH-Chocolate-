import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Melghat Cold Storage Live", layout="wide")

# Advanced CSS: Hides GitHub name, Header, Footer, and Toolbar
hide_style = """
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Subtle Floating Admin Button */
    .float-login {
        position: fixed;
        bottom: 10px;
        right: 10px;
        z-index: 1000;
        opacity: 0.1;
    }
    .float-login:hover {opacity: 1.0;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

ADMIN_PASSWORD = "admin_melghat_123" 
IST = pytz.timezone('Asia/Kolkata')

# --- 2. DATABASE LINK ---
SHEET_ID = "1VdlrBRqSHffGA32cCUCHm7Vbn5zA8CP-5A53Gjc-g9Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=30)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        data.columns = data.columns.str.strip().str.lower()
        return data
    except:
        return pd.DataFrame(columns=['date', 'time', 'temperature', 'humidity'])

# --- 3. FLOATING ADMIN LOGIN ---
with st.container():
    st.markdown('<div class="float-login">', unsafe_allow_html=True)
    with st.expander("⚙️"):
        password_input = st.text_input("Access Code", type="password")
        admin_logged_in = (password_input == ADMIN_PASSWORD)
        show_all = st.checkbox("Show Backend Data") if admin_logged_in else False
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DATA PROCESSING ---
df_raw = load_data()

if not df_raw.empty:
    df = df_raw.copy()
    for col in ['date', 'time']:
        df[col] = df[col].astype(str).str.strip()
    
    df['full_timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
    df = df.dropna(subset=['full_timestamp'])
    
    if not df.empty:
        df = df.sort_values('full_timestamp')
        now_ist = datetime.now(IST).replace(tzinfo=None) 
        
        public_view = df[df['full_timestamp'] <= now_ist]
        display_df = df if show_all else public_view

        # --- 5. MAIN DASHBOARD UI ---
        st.title("❄️ Melghat Cold Storage Live")
        
        # Live Metrics Row
        if not public_view.empty:
            latest = public_view.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Live Temp", f"{latest['temperature']} °C")
            # Only show humidity if column exists
            if 'humidity' in latest:
                m2.metric("Live Humidity", f"{latest['humidity']} %")
            else:
                m2.metric("Live Humidity", "N/A")
            m3.metric("Date", latest['date'])
            m4.metric("Last Update", latest['time'])

        st.divider()

        # --- 6. TEMPERATURE GRAPH ---
        st.subheader("🌡️ Temperature Trend (°C)")
        fig_temp = px.line(display_df, x='full_timestamp', y='temperature', 
                          markers=True, color_discrete_sequence=['#FF4B4B'],
                          labels={'full_timestamp': 'Time', 'temperature': 'Temp (°C)'},
                          template="plotly_white")
        fig_temp.add_shape(type="line", x0=now_ist, x1=now_ist, y0=0, y1=1, yref="paper",
                          line=dict(color="Red", width=2, dash="dash"))
        st.plotly_chart(fig_temp, use_container_width=True)

        # --- 7. HUMIDITY GRAPH ---
        if 'humidity' in display_df.columns:
            st.subheader("💧 Humidity Trend (%)")
            fig_hum = px.line(display_df, x='full_timestamp', y='humidity', 
                             markers=True, color_discrete_sequence=['#00B4D8'],
                             labels={'full_timestamp': 'Time', 'humidity': 'Humidity (%)'},
                             template="plotly_white")
            fig_hum.add_shape(type="line", x0=now_ist, x1=now_ist, y0=0, y1=1, yref="paper",
                             line=dict(color="Red", width=2, dash="dash"))
            st.plotly_chart(fig_hum, use_container_width=True)

        # --- 8. LOG TABLE ---
        st.divider()
        st.subheader("📋 Recent Logs")
        cols_to_show = ['date', 'time', 'temperature']
        if 'humidity' in display_df.columns: cols_to_show.append('humidity')
        st.dataframe(display_df[cols_to_show].iloc[::-1], use_container_width=True)

    else:
        st.warning("Invalid Data Format in Google Sheet.")
else:
    st.info("Waiting for data from Google Sheet...")

st.caption("Melghat Cold Storage Monitoring System")
