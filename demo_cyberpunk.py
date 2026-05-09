import streamlit as st
from styles import (
    apply_cyberpunk_theme, 
    create_cyberpunk_card, 
    create_neon_divider, 
    create_status_indicator,
    create_cyberpunk_metric,
    create_cyberpunk_header,
    create_data_table_style
)
import pandas as pd

# Set page config
st.set_page_config(page_title="Cyberpunk Demo", layout="wide")

# Apply cyberpunk theme
apply_cyberpunk_theme()
create_data_table_style()

# Demo header
create_cyberpunk_header("CYBERPUNK DEMO", "Showcasing the Village Gentle styling system", "🚀")

# Demo cards
col1, col2 = st.columns(2)

with col1:
    create_cyberpunk_card(
        "System Status", 
        "All agricultural systems are online and functioning optimally. Neural networks are processing crop data in real-time.",
        "🔋"
    )

with col2:
    create_cyberpunk_card(
        "Weather Matrix",
        "Current atmospheric conditions are being monitored. Precipitation probability: 23%. Temperature: 24°C. Optimal for crop growth.",
        "🌦️"
    )

create_neon_divider()

# Demo metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    create_cyberpunk_metric("Active Users", "1,247", 15, "👥")

with col2:
    create_cyberpunk_metric("Crop Yield", "94.2%", 2.3, "🌾")

with col3:
    create_cyberpunk_metric("System Health", "99.8%", 0.1, "⚡")

with col4:
    create_cyberpunk_metric("Data Points", "15.7K", -234, "📊")

create_neon_divider()

# Demo status indicators
st.markdown("### Status Indicators")
col1, col2 = st.columns(2)

with col1:
    create_status_indicator('success', "✅ CROP ANALYSIS COMPLETE")
    create_status_indicator('info', "ℹ️ WEATHER DATA SYNCING")

with col2:
    create_status_indicator('warning', "⚠️ SENSOR CALIBRATION NEEDED")
    create_status_indicator('error', "❌ CONNECTION TIMEOUT")

create_neon_divider()

# Demo data table
st.markdown("### Data Matrix")
df = pd.DataFrame({
    'Crop Type': ['Wheat', 'Rice', 'Corn', 'Soybeans'],
    'Yield (tons/ha)': [3.2, 4.1, 5.8, 2.9],
    'Growth Stage': ['Flowering', 'Maturity', 'Vegetative', 'Reproductive'],
    'Health Status': ['Excellent', 'Good', 'Fair', 'Excellent']
})

st.dataframe(df, use_container_width=True)

# Demo form elements
create_neon_divider()
st.markdown("### Input Controls")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Neural Network ID", placeholder="Enter your ID...")
    st.selectbox("Crop Selection", ["Wheat", "Rice", "Corn", "Soybeans"])
    
with col2:
    st.number_input("Field Size (hectares)", min_value=0.1, max_value=1000.0, value=10.0)
    st.slider("Irrigation Level", 0, 100, 50)

# Demo buttons
st.markdown("### Action Controls")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 ANALYZE CROP DATA"):
        st.success("Analysis initiated...")

with col2:
    if st.button("🌦️ WEATHER SYNC"):
        st.info("Syncing weather data...")

with col3:
    if st.button("📊 GENERATE REPORT"):
        st.warning("Report generation in progress...")

st.markdown("""
---
### 🎨 Cyberpunk Features Applied:

- **Background**: Uses gentle.jpg as background image with dark overlay
- **Typography**: Orbitron for headers, Rajdhani for body text
- **Color Scheme**: Cyan (#00ffff), Magenta (#ff00ff), Neon Green (#39ff14)
- **Effects**: Glowing borders, text shadows, gradient backgrounds
- **Animations**: Hover effects, glow animations
- **Components**: Custom cards, metrics, status indicators
- **Responsive**: Mobile-friendly design
""")