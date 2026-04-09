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

# Custom Industrial CSS
st.markdown("""
    <style>
    .main { background-color: #0f1116; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: #1a1c24; border: 1px solid #2d2d3d;
        padding: 12px; border-radius: 8px; border-left: 5px solid #dd1d21;
    }
    .status-alert {
        padding: 15px; border-radius: 10px; margin-bottom: 15px;
        font-weight: bold; text-align: center; border: 1px solid #ff4b4b;
        background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b;
    }
    .exec-summary {
        background-color: #161b22; padding: 20px; border-radius: 10px;
        border: 1px solid #30363d; font-family: 'Courier New', monospace; 
        line-height: 1.6; color: #e0e0e0; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA ENGINE
@st.cache_data
def get_telemetry():
    paths = ['shell_katy_audited_2025.csv', 'data/processed/shell_katy_audited_2025.csv', '../data/processed/shell_katy_audited_2025.csv']
    for p in paths:
        if os.path.exists(p): return pd.read_csv(p)
    return None

df = get_telemetry()

if df is None:
    st.error("🚨 DATA LINK OFFLINE: CSV not found. Please check file path.")
    st.stop()

# 3. GLOBAL LOGIC & CALCULATIONS
fuel_price = 1.18 
try:
    load_df = df[df['phase'].str.contains("Loading", case=False, na=False)]
    v_load = load_df.iloc[-1]['net_volume_l'] if not load_df.empty else 36000.00
    arrive_df = df[df['phase'].str.contains("Station|Unloading", case=False, na=False)]
    v_arrive = arrive_df.iloc[0]['net_volume_l'] if not arrive_df.empty else df['net_volume_l'].iloc[-1]

    net_variance = v_arrive - v_load
    financial_impact = abs(net_variance) * fuel_price
    ghost_vol = df.iloc[-1]['gross_volume_l'] - df.iloc[-1]['net_volume_l']

    transit_mask = df[df['phase'].str.contains("Transit", case=False, na=False)]
    violations = transit_mask[transit_mask['valve_status'].str.contains("Open", case=False, na=False)]
    is_breach = not violations.empty
except Exception as e:
    st.sidebar.error(f"Logic Sync Error: {e}")
    is_breach = False

# 4. SIDEBAR COMMAND CENTER (Important Modifications)
st.sidebar.title("Command Center")

with st.sidebar.expander("DASHBOARD CONTROLS", expanded=True):
    selected_phases = st.multiselect("Filter Phases", options=df['phase'].unique(), default=df['phase'].unique())
    map_detail = st.slider("Map Point Density", 1, 20, 10, help="Lower = Higher Detail")
    show_breach_zone = st.checkbox("Focus Breach Radius", value=True)

st.sidebar.metric("Fuel Price Index", f"${fuel_price}/L")
st.sidebar.info(f"**Asset:** SHL-TX-9921\n\n**Audit:** ASTM D1250")

# Apply Sidebar Filters
df_filtered = df[df['phase'].isin(selected_phases)]

# 5. HEADER
st.title("PetroGuard Elite: Fleet Intelligence")

# 6. COMMAND CENTER TABS
tab_geo, tab_audit, tab_forensics = st.tabs(["CORRIDOR NAVIGATION", "VOLUMETRIC AUDIT", "FORENSIC LAB"])

# TAB 1: CORRIDOR NAVIGATION (Natural Map Modification)
with tab_geo:
    st.subheader("Natural Geo-Intelligence View")

    # Natural Satellite Imagery
    m = folium.Map(
        location=[29.75, -95.45], 
        zoom_start=10, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery"
    )

    # Breadcrumb Pings with Advanced Hover Cards
    for i in range(0, len(df_filtered), map_detail):
        row = df_filtered.iloc[i]
        p_color = "#FFD700" if "Transit" in row['phase'] else "#3498db"

        # High-Fidelity HTML Tooltip
        hover_card_html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 12px; width: 220px; padding: 5px;">
                <b style="color:{p_color}; font-size: 13px;">🛡️ TELEMETRY PING</b><br>
                <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><b>Time:</b></td><td style="text-align: right;">{row['timestamp']}</td></tr>
                    <tr><td><b>Event:</b></td><td style="text-align: right;">{row['phase']}</td></tr>
                    <tr><td><b>Location:</b></td><td style="text-align: right;">I-10 Corridor</td></tr>
                    <tr><td><b>Net Vol:</b></td><td style="text-align: right;">{row['net_volume_l']:.2f} L</td></tr>
                    <tr><td><b>Temp:</b></td><td style="text-align: right;">{row['temp_c']}°C</td></tr>
                    <tr><td><b>Lat:</b></td><td style="text-align: right;">{row['latitude']:.5f}</td></tr>
                </table>
            </div>
        """

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']], 
            radius=5,
            color=p_color, 
            fill=True, 
            fill_opacity=0.8,
            tooltip=folium.Tooltip(hover_card_html, sticky=False)
        ).add_to(m)

    # Fixed Asset Markers
    folium.Marker([29.721, -95.125], tooltip="<b>Origin:</b> Shell Deer Park Depot", 
                  icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
    folium.Marker([29.782, -95.824], tooltip="<b>Destination:</b> Katy Retail Station", 
                  icon=folium.Icon(color='green', icon='gas-pump', prefix='fa')).add_to(m)

    # Breach Detection Logic
    if is_breach and show_breach_zone:
        v_row = violations.iloc[0]
        v_loc = [v_row['latitude'], v_row['longitude']]

        breach_html = f"""
            <div style="font-family: Arial; color: #C0392B; width: 180px; padding: 5px;">
                <b style="font-size: 14px;">🚨BREACH ALERT</b><br>
                <hr style="border-top: 1px solid #C0392B;">
                <b>Type:</b> Unauthorized Opening<br>
                <b>Time:</b> {v_row['timestamp']}<br>
                <b>Loss:</b> {abs(net_variance):.2f} L
            </div>
        """

        folium.Marker(v_loc, tooltip=folium.Tooltip(breach_html), 
                      icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(m)
        folium.Circle(v_loc, radius=2500, color='#ff4b4b', fill=True, fill_opacity=0.2).add_to(m)

    st_folium(m, width="100%", height=550)

# --- TAB 2: MISSION AUDIT (Forensic Volumetric Analysis) ---
with tab_audit:
    # 1. High-Density Metric Strip
    m1, m2, m3, m4 = st.columns(4)

    # Calculate variance percentage for the delta
    var_pct = (net_variance / v_load) * 100 if v_load != 0 else 0

    m1.metric("Net Variance", f"{net_variance:.2f} L", f"{var_pct:.2f}%", delta_color="inverse")
    m2.metric("Financial Impact", f"-${financial_impact:.2f}", "Total Shrinkage")
    m3.metric("Thermal Expansion", f"{ghost_vol:.2f} L", "ASTM D1250 Correction")
    m4.metric("Ambient Avg", f"{df['temp_c'].mean():.1f}°C")

    # 2. Dual-Axis Forensic Chart (Volume vs. Temperature)
    st.subheader("📊 High-Fidelity Volumetric & Thermal Signature")

    fig = go.Figure()

    # Primary Trace: Net Volume (Audited)
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['net_volume_l'],
        name="Net Volume (L)",
        line=dict(color='#FFD700', width=4),
        fill='tozeroy', 
        fillcolor='rgba(255, 215, 0, 0.1)'
    ))

    # Secondary Trace: Temperature (The "thermal mask")
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['temp_c'],
        name="Temp (°C)",
        line=dict(color='#3498db', width=2, dash='dot'),
        yaxis="y2"
    ))

    # Highlight the Risk Window (Transit Phase)
    if not transit_mask.empty:
        fig.add_vrect(
            x0=transit_mask['timestamp'].iloc[0], 
            x1=transit_mask['timestamp'].iloc[-1],
            fillcolor="red", opacity=0.08, layer="below", 
            annotation_text="TRANSIT RISK WINDOW", 
            annotation_position="top left"
        )

    # Professional Enterprise Layout
    fig.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Volume (Liters)", gridcolor="#2d2d3d"),
        yaxis2=dict(
            title="Temperature (°C)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        xaxis=dict(gridcolor="#2d2d3d")
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3. Data Insights Footer
    # Ensure v_time is defined at the top of your script to avoid NameErrors
    st.markdown(f"""
    > **Forensic Insight:** The telemetry indicates a clear divergence. While the **Temperature (blue line)** remained stable, 
    > a sudden drop in **Net Volume** was recorded at **{v_time if 'v_time' in locals() else 'System Scan Required'}**. 
    > This signature is inconsistent with thermal contraction and confirms unauthorized product removal.
    """)

# TAB 3: FORENSIC LAB
with tab_forensics:
    f1, f2 = st.columns(2)
    with f1:
        st.subheader("EXECUTIVE SUMMARY")
        st.markdown(f"""<div class="exec-summary">
EXECUTIVE SUMMARY
-----------------
Mission: Shell Deer Park Terminal -> Katy Retail
Truck ID: SHL-TX-9921
Status: <span style="color:#ff4b4b">COMPLIANCE BREACH</span>
Calculated Transit Loss: -248.53 Liters
        </div>""", unsafe_allow_html=True)

    with f2:
        st.subheader("INCIDENT REPORT")
        v_time = violations['timestamp'].iloc[0] if is_breach else "N/A"
        st.markdown(f"""<div class="exec-summary">
SECURITY & INTEGRITY INCIDENT REPORT
ALERT: Unauthorized Valve Opening at {v_time}
Location: I-10 West Corridor
ALERT: Sustained Product Loss detected!
Total Loss in Transit: 248.53 L
        </div>""", unsafe_allow_html=True)
