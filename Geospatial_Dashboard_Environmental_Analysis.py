import streamlit as st
import numpy as np
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import st_folium

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Geospatial Dashboard – Environmental Analysis",
    layout="wide"
)

# =========================================================
# HEADER (Styled)
# =========================================================
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #2e7d32, #66bb6a);
    padding: 18px;
    border-radius: 6px;
    color: white;
    text-align: center;
    margin-bottom: 15px;
}
.card {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 6px;
}
</style>

<div class="header">
    <h2>Geospatial Dashboard – Environmental Analysis</h2>
    <p>Interactive Geospatial Analysis & Remote Sensing Visualization</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR – FILTERS
# =========================================================
st.sidebar.header("Data Filters")

region = st.sidebar.selectbox(
    "Select Region",
    ["Region A", "Region B", "Region C"]
)

dataset = st.sidebar.selectbox(
    "Select Dataset",
    ["NDVI", "NDBI", "NDWI"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [pd.to_datetime("2021-06-01"), pd.to_datetime("2021-06-30")]
)

elevation = st.sidebar.slider(
    "Elevation (m)",
    0, 2000, (0, 2000)
)

apply = st.sidebar.button("Apply Filters", use_container_width=True)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(
    ["Raster Analysis", "Vector Data", "3D Terrain"]
)

# =========================================================
# RASTER ANALYSIS TAB
# =========================================================
with tab1:

    # -----------------------------------------------------
    # SIMULATED NDVI DATA
    # -----------------------------------------------------
    np.random.seed(42)

    xmin, ymin, xmax, ymax = -12, 10, 4, 25  # West Africa
    n = 40

    xs = np.linspace(xmin, xmax, n)
    ys = np.linspace(ymin, ymax, n)

    records = []
    for x in xs:
        for y in ys:
            records.append({
                "lon": x,
                "lat": y,
                "value": np.clip(np.random.normal(0.6, 0.15), 0, 1)
            })

    df = pd.DataFrame(records)

    mean_val = df["value"].mean()
    max_val = df["value"].max()
    min_val = df["value"].min()

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------
    col_map, col_right = st.columns([3, 1.6])

    # -----------------------------------------------------
    # MAP
    # -----------------------------------------------------
    with col_map:
        st.subheader(f"{dataset} Map")

        m = folium.Map(
            location=[17, -4],
            zoom_start=5,
            tiles="cartodbpositron"
        )

        for _, r in df.iterrows():
            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=4,
                fill=True,
                fill_color=(
                    "green" if r["value"] > 0.6
                    else "orange" if r["value"] > 0.4
                    else "red"
                ),
                fill_opacity=0.7,
                color=None,
                tooltip=f"{dataset}: {r['value']:.2f}"
            ).add_to(m)

        st_folium(m, height=520, use_container_width=True)

        # KPI Cards
        st.markdown("### Statistics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Mean NDVI", f"{mean_val:.2f}")
        c2.metric("Max NDVI", f"{max_val:.2f}")
        c3.metric("Min NDVI", f"{min_val:.2f}")

    # -----------------------------------------------------
    # CHARTS
    # -----------------------------------------------------
    with col_right:
        st.subheader(f"{dataset} Time Series")

        dates = pd.date_range(date_range[0], date_range[1])
        ts = pd.DataFrame({
            "Date": dates,
            "Value": np.clip(
                np.random.normal(mean_val, 0.05, len(dates)), 0, 1
            )
        })

        fig_ts = px.line(
            ts,
            x="Date",
            y="Value",
            markers=True,
            labels={"Value": dataset}
        )
        st.plotly_chart(fig_ts, use_container_width=True)

        st.subheader("Land Cover Distribution")

        lc = pd.DataFrame({
            "Class": ["Forest", "Agriculture", "Water", "Urban"],
            "Percentage": [45, 30, 15, 10]
        })

        fig_pie = px.pie(
            lc,
            names="Class",
            values="Percentage",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# =========================================================
# VECTOR DATA TAB
# =========================================================
with tab2:
    st.info("Vector data visualization coming soon.")

# =========================================================
# 3D TERRAIN TAB
# =========================================================
with tab3:
    st.info("3D terrain visualization coming soon.")

# =========================================================
# FOOTER ACTIONS
# =========================================================
st.markdown("<hr>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
b1.button("⬇️ Download Data")
b2.button("📄 Generate Report")
b3.button("ℹ️ About this Dashboard")
