
import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import st_folium
from shapely.geometry import box


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Geospatial Dashboard – Environmental Analysis",
    layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center;'>Geospatial Dashboard – Environmental Analysis</h1>
    <h4 style='text-align:center; color:gray;'>
    Interactive Geospatial Analysis & Remote Sensing Visualization
    </h4>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Sidebar – Filters
# --------------------------------------------------
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
    min_value=0,
    max_value=2000,
    value=(0, 2000)
)

apply = st.sidebar.button("Apply Filters")

# --------------------------------------------------
# Simulated geospatial data (NDVI-like raster grid)
# --------------------------------------------------
np.random.seed(42)

xmin, ymin, xmax, ymax = -12, 10, 4, 25  # West Africa bbox
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

df_points = pd.DataFrame(records)

# Statistics
mean_val = df_points["value"].mean()
max_val = df_points["value"].max()
min_val = df_points["value"].min()

# --------------------------------------------------
# Layout
# --------------------------------------------------
col_map, col_right = st.columns([2.5, 1.5])

# --------------------------------------------------
# Map
# --------------------------------------------------
with col_map:
    st.subheader(f"{dataset} Map")

    m = folium.Map(location=[17, -4], zoom_start=5, tiles="cartodbpositron")

    for _, row in df_points.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color=None,
            fill=True,
            fill_color=(
                "green" if row["value"] > 0.6
                else "orange" if row["value"] > 0.4
                else "red"
            ),
            fill_opacity=0.7,
            tooltip=f"{dataset}: {row['value']:.2f}"
        ).add_to(m)

    st_folium(m, height=520, width=None)

    # Statistics
    st.markdown("### Statistics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean", f"{mean_val:.2f}")
    c2.metric("Max", f"{max_val:.2f}")
    c3.metric("Min", f"{min_val:.2f}")

# --------------------------------------------------
# Right panel – Charts
# --------------------------------------------------
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

# --------------------------------------------------
# Footer buttons
# --------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

c1.button("⬇️ Download Data")
c2.button("📄 Generate Report")

c3.button("ℹ️ About this Dashboard")
