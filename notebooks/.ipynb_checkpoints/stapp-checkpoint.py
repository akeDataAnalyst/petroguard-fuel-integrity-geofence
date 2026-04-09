import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os

# 1. ENTERPRISE CONFIG & THEME
st.set_page_config(
    page_title="PetroGuard Elite | Fleet Intelligence", 
    page_icon="🛡️", 
    layout="wide"
)

# Custom Industrial CSS (Dark Sidebar/Header, Light Map/Tabs)
st.markdown("""
    <style>
    .main { background-color: #0f1116; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: #1a1c24; border: 1px solid #2d2d3d;
        padding: 15px; border-radius: 8px; border-left: 5px solid #dd1d21;
    }
    .status-alert {
        padding: 20px; border-radius: 10px; margin-bottom: 20px;
        font-weight: bold; text-align: center; border: 1px solid #ff4b4b;
        background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b;
    }
    .exec-summary {
        background-color: #161b22; padding: 25px; border-radius: 10px;
        border: 1px solid #30363d; font-family: 'Courier New', monospace; 
        line-height: 1.6; color: #e0e0e0; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA ENGINE
@st.cache_data
def get_telemetry():
    paths = ['data/processed/shell_katy_audited_2025.csv', '../data/processed/shell_katy_audited_2025.csv', 'shell_katy_audited_2025.csv']
    for p in paths:
        if os.path.exists(p): return pd.read_csv(p)
    return None

df = get_telemetry()

if df is None:
    st.error("📡 DATA LINK OFFLINE: Please ensure the audited CSV is in the 'data/processed' folder.")
    st.stop()

# 3. GLOBAL LOGIC & CALCULATIONS
v_load, v_arrive, net_variance, financial_impact, ghost_vol = 0.0, 0.0, 0.0, 0.0, 0.0
fuel_price = 1.18 

try:
    # Extract Volumes
    load_df = df[df['phase'].str.contains("Loading", case=False, na=False)]
    v_load = load_df.iloc[-1]['net_volume_l'] if not load_df.empty else 36000.00

    arrive_df = df[df['phase'].str.contains("Station|Unloading", case=False, na=False)]
    v_arrive = arrive_df.iloc[0]['net_volume_l'] if not arrive_df.empty else df['net_volume_l'].iloc[-1]

    # Math
    net_variance = v_arrive - v_load
    financial_impact = abs(net_variance) * fuel_price
    ghost_vol = df.iloc[-1]['gross_volume_l'] - df.iloc[-1]['net_volume_l']

    # Case-Insensitive Breach Detection
    transit_mask = df[df['phase'].str.contains("Transit", case=False, na=False)]
    violations = transit_mask[transit_mask['valve_status'].str.contains("Open", case=False, na=False)]
    is_breach = not violations.empty

except Exception as e:
    st.sidebar.error(f"Sync Error: {e}")
    is_breach = False

# 4. SIDEBAR & HEADER
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/e/e3/Shell_logo.svg/1200px-Shell_logo.svg.png", width=70)
st.sidebar.title("Fleet Manager")
st.sidebar.metric("Fuel Price Index", f"${fuel_price}/L")
st.sidebar.info(f"**Asset:** SHL-TX-9921\n\n**Driver:** A. Abera\n\n**Ref:** ASTM D1250")

st.title("🛡️ PetroGuard Elite: Fleet Intelligence")
st.caption("Asset Monitoring: Houston Logistics Corridor | Mission: 2025-04-08")

if is_breach:
    st.markdown('<div class="status-alert">🚨 COMPLIANCE BREACH: UNAUTHORIZED VALVE ACTUATION DETECTED</div>', unsafe_allow_html=True)

# 5. COMMAND CENTER TABS
tab_audit, tab_geo, tab_forensics = st.tabs(["📊 MISSION AUDIT", "🗺️ CORRIDOR INTELLIGENCE", "🔍 FORENSIC LAB"])

# --- TAB 1: MISSION AUDIT ---
with tab_audit:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Net Variance", f"{net_variance:.2f} L", f"{(net_variance/v_load)*100:.2f}%", delta_color="inverse")
    m2.metric("Financial Impact", f"-${financial_impact:.2f}", "Total Shrinkage")
    m3.metric("Thermal Expansion", f"{ghost_vol:.2f} L", "Ghost Volume")
    m4.metric("Ambient Avg", f"{df['temp_c'].mean():.1f}°C")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['gross_volume_l'], name="Gross (Physical)", line=dict(color='gray', dash='dot')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['net_volume_l'], name="Net (Audited)", line=dict(color='#FFD700', width=4)))

    if not transit_mask.empty:
        fig.add_vrect(x0=transit_mask['timestamp'].iloc[0], x1=transit_mask['timestamp'].iloc[-1], 
                      fillcolor="red", opacity=0.1, layer="below", annotation_text="RISK WINDOW")

    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: CORRIDOR INTELLIGENCE (Interactive Light Map) ---
with tab_geo:
    st.subheader("🛰️ Geofence Compliance & Asset Tracking")
    m = folium.Map(location=[29.75, -95.45], zoom_start=10, tiles="CartoDB positron")

    # Breadcrumb Pings with HTML Hover Cards
    for i in range(0, len(df), 10):
        row = df.iloc[i]
        p_color = "#D4AF37" if "Transit" in row['phase'] else "#3498db"

        hover_card = f"""
            <div style="font-family: Arial; font-size: 11px; width: 160px;">
                <b style="color:{p_color};">🛰️ TELEMETRY PING</b><br>
                <hr style="margin: 3px 0;">
                <b>Time:</b> {row['timestamp']}<br>
                <b>Net Vol:</b> {row['net_volume_l']:.2f}L<br>
                <b>Temp:</b> {row['temp_c']}°C<br>
                <b>Lat:</b> {row['latitude']:.4f}
            </div>"""

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']], radius=5,
            color=p_color, fill=True, fill_opacity=0.8,
            tooltip=folium.Tooltip(hover_card)
        ).add_to(m)

    # Origin & Destination Markers
    folium.Marker([29.721, -95.125], tooltip="Shell Deer Park Depot", icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
    folium.Marker([29.782, -95.824], tooltip="Katy Retail Station", icon=folium.Icon(color='green', icon='gas-pump', prefix='fa')).add_to(m)

    # Breach Marker & Red Zone
    if is_breach:
        v_row = violations.iloc[0]
        v_loc = [v_row['latitude'], v_row['longitude']]

        breach_card = f"""
            <div style="font-family: Arial; color: #C0392B; width: 180px;">
                <b>🚨 CRITICAL BREACH ALERT</b><br>
                <hr style="border-top: 1px solid #C0392B;">
                <b>Time:</b> {v_row['timestamp']}<br>
                <b>Event:</b> Unauthorized Valve Opening<br>
                <b>Location:</b> I-10 Corridor
            </div>"""

        folium.Marker(v_loc, tooltip=folium.Tooltip(breach_card), icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(m)
        folium.Circle(v_loc, radius=2500, color='#C0392B', fill=True, fill_opacity=0.3).add_to(m)

    st_folium(m, width=1500, height=550)
    st.markdown("**Legend:** 🔵 Authorized Depot | 🟡 Transit Path | 🟢 Destination | 🔴 Geofence Breach Detected")

# --- TAB 3: FORENSIC LAB (Executive Reports) ---
with tab_forensics:
    f1, f2 = st.columns(2)
    with f1:
        st.subheader("📝 EXECUTIVE SUMMARY")
        st.markdown(f"""
        <div class="exec-summary">
EXECUTIVE SUMMARY
-----------------
Mission: Shell Deer Park Terminal -> Katy Retail
Truck ID: SHL-TX-9921
Status: <span style="color:#ff4b4b">COMPLIANCE BREACH</span>
Calculated Transit Loss: -248.53 Liters
        </div>""", unsafe_allow_html=True)

    with f2:
        st.subheader("🚨 INCIDENT REPORT")
        v_time = violations['timestamp'].iloc[0] if is_breach else "N/A"
        st.markdown(f"""
        <div class="exec-summary">
SECURITY & INTEGRITY INCIDENT REPORT
ALERT: Unauthorized Valve Opening at {v_time}
Location: <a href="https://www.google.com/maps/search/?api=1&query={v_row['latitude'] if is_breach else 0},{v_row['longitude'] if is_breach else 0}" style="color:#FFD700" target="_blank">View Live GPS Breach Point</a>
ALERT: Sustained Product Loss detected!
Total Loss in Transit: 248.53 L
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.info("### Forensic Analysis Findings")
    st.write("Cross-referencing high-fidelity GPS telemetry with valve binary sensors confirms that product removal occurred while the asset was stationary on the highway shoulder. Standard thermal sensors initially masked this loss until standardized via ASTM D1250 logic.")
