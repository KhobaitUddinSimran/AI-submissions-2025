# app.py
import time
import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import pandas as pd

from mock_data import generate_mock_tick

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="YSMAI - Engine Monitoring SCADA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SCHEMA GUARD (CRITICAL)
# =========================================================
SCHEMA_VERSION = "v3_multi_sensor"

if "schema_version" not in st.session_state:
    st.session_state.clear()
    st.session_state.schema_version = SCHEMA_VERSION
elif st.session_state.schema_version != SCHEMA_VERSION:
    st.session_state.clear()
    st.session_state.schema_version = SCHEMA_VERSION

# =========================================================
# SESSION STATE INIT
# =========================================================
defaults = {
    "running": False,
    "start_time": None,
    "tick_count": 0,
    "sensor_history": [],
    "alert_history": [],
    "scheduler": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.title("Simulation Controls")

if st.sidebar.button("▶ Start"):
    st.session_state.running = True
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

if st.sidebar.button("⏸ Stop"):
    st.session_state.running = False

if st.sidebar.button("🔄 Reset"):
    st.session_state.clear()
    st.session_state.schema_version = SCHEMA_VERSION
    st.rerun()

st.sidebar.divider()

initial_temp = st.sidebar.slider("Initial Temp (°F)", 50, 100, 60)
drift_rate = st.sidebar.slider("Drift Rate (°F/sec)", 0.1, 2.0, 0.5)
high_threshold = st.sidebar.slider("High Threshold (°F)", 70, 110, 85)
low_threshold = st.sidebar.slider("Low Threshold (°F)", 40, 80, 50)

# =========================================================
# AUTO REFRESH
# =========================================================
st_autorefresh(interval=1500, limit=None, key="refresh")

# =========================================================
# DATA UPDATE LOOP
# =========================================================
if st.session_state.running:
    base_tick = generate_mock_tick(
        tick_count=st.session_state.tick_count,
        start_time=st.session_state.start_time,
        initial_temp_f=initial_temp,
        drift_rate_f=drift_rate,
        high_threshold_f=high_threshold,
        low_threshold_f=low_threshold,
    )

    # ---- DERIVED MOCK SENSORS (SAFE & REALISTIC) ----
    rpm = int(1800 + random.randint(-200, 200))
    oil_pressure = max(10, 60 - (rpm / 100))
    vibration = max(2, random.uniform(3, 8) + (0.05 * st.session_state.tick_count))
    voltage = round(random.uniform(12.2, 13.8), 2)

    # ---- MOCK ML OUTPUTS ----
    # ---- MOCK ML OUTPUTS (SCHEMA-SAFE) ----
    temp_val = base_tick.get("temperature_f")

    ml_fault = False
    if isinstance(temp_val, (int, float)):
        ml_fault = temp_val > high_threshold

    ml_confidence = round(random.uniform(0.85, 0.99), 2)
    vib_anomaly = vibration > 18


    full_tick = {
        **base_tick,
        "rpm": rpm,
        "oil_pressure_psi": round(oil_pressure, 1),
        "vibration_mms": round(vibration, 2),
        "voltage_v": voltage,
        "ml": {
            "fault_detected": ml_fault,
            "confidence": ml_confidence,
            "vibration_anomaly": vib_anomaly
        }
    }

    st.session_state.sensor_history.append(full_tick)
    st.session_state.tick_count += 1

    if len(st.session_state.sensor_history) > 300:
        st.session_state.sensor_history = st.session_state.sensor_history[-300:]

    # ---- ALERT LOGIC (STATE CHANGE ONLY) ----
    if len(st.session_state.sensor_history) > 1:
        prev = st.session_state.sensor_history[-2]
        if prev["state"] != full_tick["state"]:
            st.session_state.alert_history.append({
                "time": time.strftime("%H:%M:%S"),
                "message": f"State changed {prev['state']} → {full_tick['state']}",
                "severity": "CRITICAL" if full_tick["state"] == "CRITICAL" else "WARNING"
            })
            if len(st.session_state.alert_history) > 100:
                st.session_state.alert_history = st.session_state.alert_history[-100:]

            # ---- MAINTENANCE SCHEDULER ----
            st.session_state.scheduler.append({
                "priority": 1 if full_tick["state"] == "CRITICAL" else 2,
                "task": "Inspect cooling system",
                "status": "Pending",
                "confidence": ml_confidence
            })

# =========================================================
# HEADER
# =========================================================
st.title("YSMAI – Real-Time Engine Monitoring SCADA")
st.caption("Multi-Sensor Mock Simulation • Fahrenheit")

# =========================================================
# LATEST DATA
# =========================================================
latest = st.session_state.sensor_history[-1] if st.session_state.sensor_history else {}

# =========================================================
# KPI CARDS
# =========================================================
cols = st.columns(5)

cols[0].metric("Temp (°F)", latest.get("temperature_f", "--"))
cols[1].metric("State", latest.get("state", "IDLE"))
cols[2].metric("RPM", latest.get("rpm", "--"))
cols[3].metric("Oil PSI", latest.get("oil_pressure_psi", "--"))
cols[4].metric("Vibration", latest.get("vibration_mms", "--"))

# =========================================================
# MAIN TEMPERATURE CHART
# =========================================================
times = [
    x.get("simulation_time", 0)
    for x in st.session_state.sensor_history
]

temps = [
    x.get("temperature_f", x.get("temperature"))
    for x in st.session_state.sensor_history
    if x.get("temperature_f") is not None or x.get("temperature") is not None
]


fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=times, y=temps, mode="lines", name="Temp (°F)"))
fig_temp.add_hline(y=high_threshold, line_dash="dash", line_color="red")
fig_temp.add_hline(y=low_threshold, line_dash="dash", line_color="blue")
fig_temp.update_layout(height=400, yaxis_range=[40, 120])

st.plotly_chart(fig_temp, use_container_width=True)

# =========================================================
# SECONDARY CHARTS
# =========================================================
c1, c2, c3 = st.columns(3)

# Oil pressure
c1.plotly_chart(go.Figure(
    data=[go.Scatter(y=[x["oil_pressure_psi"] for x in st.session_state.sensor_history])],
    layout=go.Layout(title="Oil Pressure (PSI)", yaxis_range=[0, 80])
), use_container_width=True)

# Vibration
c2.plotly_chart(go.Figure(
    data=[go.Scatter(y=[x["vibration_mms"] for x in st.session_state.sensor_history])],
    layout=go.Layout(title="Vibration (mm/s)", yaxis_range=[0, 50])
), use_container_width=True)

# RPM
c3.plotly_chart(go.Figure(
    data=[go.Scatter(y=[x["rpm"] for x in st.session_state.sensor_history])],
    layout=go.Layout(title="RPM", yaxis_range=[0, 3000])
), use_container_width=True)

# =========================================================
# ML INSIGHTS
# =========================================================
st.subheader("ML Insights")
if latest:
    st.json(latest.get("ml", {}))

# =========================================================
# ALERT LOG
# =========================================================
st.subheader("Alert Log")
st.dataframe(pd.DataFrame(st.session_state.alert_history), use_container_width=True)

# =========================================================
# MAINTENANCE SCHEDULER
# =========================================================
st.subheader("Maintenance Scheduler")
st.dataframe(pd.DataFrame(st.session_state.scheduler), use_container_width=True)
