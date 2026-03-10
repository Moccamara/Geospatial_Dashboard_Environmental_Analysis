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
    page_title="NDVI Environmental Dashboard",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg,#1b5e20,#66bb6a);
    padding:18px;
    border-radius:6px;
    color:white;
    text-align:center;
}
</style>

<div class="header">
<h2>NDVI Geospatial Dashboard</h2>
<p>Vegetation Monitoring using Satellite Data</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Filters")

region = st.sidebar.selectbox(
    "Region",
    ["Region A", "Region B", "Region C"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [pd.to_datetime("2021-06-01"), pd.to_datetime("2021-06-30")]
)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(
    ["NDVI Map", "Vegetation Statistics", "3D Terrain"]
)

# =========================================================
# NDVI MAP
# =========================================================
with tab1:

    st.subheader("NDVI Spatial Distribution")

    np.random.seed(42)

    xmin, ymin, xmax, ymax = -12, 10, 4, 25
    n = 40

    xs = np.linspace(xmin, xmax, n)
    ys = np.linspace(ymin, ymax, n)

    records = []

    for x in xs:
        for y in ys:

            # simulate satellite bands
            nir = np.random.uniform(0.3, 0.9)
            red = np.random.uniform(0.1, 0.6)

            ndvi = (nir - red) / (nir + red)

            records.append({
                "lon": x,
                "lat": y,
                "nir": nir,
                "red": red,
                "ndvi": ndvi
            })

    df = pd.DataFrame(records)

    mean_ndvi = df["ndvi"].mean()
    max_ndvi = df["ndvi"].max()
    min_ndvi = df["ndvi"].min()

    col1, col2 = st.columns([3,1.5])

    # MAP
    with col1:

        m = folium.Map(
            location=[17,-4],
            zoom_start=5,
            tiles="cartodbpositron"
        )

        for _, r in df.iterrows():

            if r["ndvi"] > 0.6:
                color = "darkgreen"
            elif r["ndvi"] > 0.3:
                color = "lightgreen"
            elif r["ndvi"] > 0:
                color = "orange"
            else:
                color = "red"

            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=4,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                color=None,
                tooltip=f"NDVI: {r['ndvi']:.2f}"
            ).add_to(m)

        st_folium(m, height=520, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Mean NDVI", f"{mean_ndvi:.2f}")
        c2.metric("Max NDVI", f"{max_ndvi:.2f}")
        c3.metric("Min NDVI", f"{min_ndvi:.2f}")

    # TIMESERIES
    with col2:

        st.subheader("NDVI Time Series")

        dates = pd.date_range(date_range[0], date_range[1])

        ts = pd.DataFrame({
            "Date": dates,
            "NDVI": np.clip(
                np.random.normal(mean_ndvi,0.05,len(dates)),
                -1,1
            )
        })

        fig = px.line(
            ts,
            x="Date",
            y="NDVI",
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# VEGETATION STATS
# =========================================================
with tab2:

    st.subheader("Vegetation Classes")

    veg = pd.DataFrame({
        "Class":[
            "Dense Vegetation",
            "Moderate Vegetation",
            "Sparse Vegetation",
            "Bare Soil"
        ],
        "NDVI Range":[
            "0.6 – 1",
            "0.3 – 0.6",
            "0 – 0.3",
            "< 0"
        ]
    })

    st.dataframe(veg)

# =========================================================
# 3D TERRAIN
# =========================================================
with tab3:
    st.info("3D terrain visualization coming soon.")
