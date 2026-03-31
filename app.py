import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Melghat Cold Storage Live", layout="wide")

# ADVANCED CSS: Hides GitHub name, Header, Footer, and Toolbar
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
# Updated with your specific Sheet ID
SHEET_ID = "1RiDh11R8FhczC5zbzucf_gsbLu-T7N0iiG3g9c80f20"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=30)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        # SAFETY SHIELD: Forces all headers to lowercase and removes spaces
        data.columns = data.columns.str.strip().str.lower()
        return data
    except Exception as e:
        return pd.DataFrame()

# --- 3. FLOATING ADMIN LOGIN (BOTTOM RIGHT) ---
with st.container():
    st.markdown('<div class="float-login">', unsafe_allow_html=True)
    with st.expander("⚙️"):
        password_input = st.text_input("Access Code", type="password")
        admin_logged_in = (password_input == ADMIN_PASSWORD)
        show_all = st.checkbox("Show Backend Data") if admin_logged_in else False
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. MAIN DASHBOARD UI ---
st.title("❄️ Melghat Cold Storage Live")

df_raw = load_data()

if not df_raw.empty:
    df = df_raw.copy()
    
    # Check if required columns exist
    if 'date' in df.columns and 'time' in df.columns:
        df['date'] = df['date'].astype(str).str.strip()
        df['time'] = df['time'].astype(str).str.strip()
        
        # Combine and convert to timestamp
        df['full_timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
        df = df.dropna(subset=['full_timestamp'])
        
        if not df.empty:
            df = df.sort_values('full_timestamp')
            now_ist = datetime.now(IST).replace(tzinfo=None) 
            
            public_view = df[df['full_timestamp'] <= now_ist]
            display_df = df if show_all else public_view

            # --- 5. LIVE METRICS ---
            if not public_view.empty:
                latest = public_view.iloc[-1]
                m1, m2, m3, m4 = st.columns(4)
                
                temp_val = latest['temperature'] if 'temperature' in latest else "N/A"
                m1.metric("Live Temp", f"{temp_val} °C")
                
                hum_val = latest['humidity'] if 'humidity' in latest else "N/A"
                m2.metric("Live Humidity", f"{hum_val} %")
                
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

            # --- 8. HISTORY TABLE ---
            st.divider()
            st.subheader("📋 Recent Logs")
            cols_to_show = [c for c in ['date', 'time', 'temperature', 'humidity'] if c in display_df.columns]
            st.dataframe(display_df[cols_to_show].iloc[::-1], use_container_width=True)
            
        else:
            st.warning("Data found, but Date/Time formats are incorrect. Please use YYYY-MM-DD and HH:MM.")
    else:
        st.error(f"Missing columns! I found: {list(df.columns)}. Ensure Row 1 has: date, time, temperature, humidity.")
else:
    st.info("Waiting for data. Ensure your Sheet is 'Published
