import streamlit as st
import numpy as np
import pandas as pd
import folium
import plotly.express as px
import geopandas as gpd
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
    margin-bottom:15px;
}
</style>

<div class="header">
<h2>Geospatial Environmental Dashboard</h2>
<p>NDVI Vegetation Monitoring Platform</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Analysis Parameters")

region = st.sidebar.selectbox(
    "Region",
    ["National", "Region A", "Region B"]
)

dataset = st.sidebar.selectbox(
    "Dataset",
    ["NDVI"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [pd.to_datetime("2023-06-01"), pd.to_datetime("2023-06-30")]
)

# =========================================================
# FUNCTIONS
# =========================================================

def generate_ndvi_grid():

    """Generate NDVI sample grid (replace with satellite data later)"""

    xmin, ymin, xmax, ymax = -12, 10, 4, 25
    n = 40

    xs = np.linspace(xmin, xmax, n)
    ys = np.linspace(ymin, ymax, n)

    records = []

    for x in xs:
        for y in ys:

            nir = np.random.uniform(0.4,0.9)
            red = np.random.uniform(0.1,0.6)

            ndvi = (nir-red)/(nir+red)

            records.append({
                "lon":x,
                "lat":y,
                "ndvi":ndvi
            })

    return pd.DataFrame(records)


def add_country_boundary(map_obj):

    """Add Mali boundary if file exists"""

    try:

        mali = gpd.read_file("mali_boundary.geojson")

        folium.GeoJson(
            mali,
            name="Mali Boundary",
            style_function=lambda x:{
                "fillColor":"none",
                "color":"black",
                "weight":2
            }
        ).add_to(map_obj)

    except:
        st.warning("Country boundary file not found.")


def ndvi_color(val):

    """NDVI color classification"""

    if val > 0.6:
        return "darkgreen"
    elif val > 0.3:
        return "green"
    elif val > 0:
        return "orange"
    else:
        return "red"


# =========================================================
# DATA
# =========================================================

df = generate_ndvi_grid()

mean_ndvi = df["ndvi"].mean()
max_ndvi = df["ndvi"].max()
min_ndvi = df["ndvi"].min()

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "NDVI Map",
    "Statistics",
    "3D Terrain"
])

# =========================================================
# MAP TAB
# =========================================================

with tab1:

    col_map, col_chart = st.columns([3,1.5])

    with col_map:

        st.subheader("NDVI Spatial Distribution")

        m = folium.Map(
            location=[17,-4],
            zoom_start=5,
            tiles="cartodbpositron"
        )

        add_country_boundary(m)

        for _, r in df.iterrows():

            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=4,
                fill=True,
                fill_color=ndvi_color(r["ndvi"]),
                fill_opacity=0.8,
                color=None,
                tooltip=f"NDVI: {r['ndvi']:.2f}"
            ).add_to(m)

        folium.LayerControl().add_to(m)

        st_folium(m, height=520, use_container_width=True)

        st.markdown("### NDVI Statistics")

        c1,c2,c3 = st.columns(3)

        c1.metric("Mean NDVI",f"{mean_ndvi:.2f}")
        c2.metric("Max NDVI",f"{max_ndvi:.2f}")
        c3.metric("Min NDVI",f"{min_ndvi:.2f}")

    # -----------------------------------------------------
    # TIMESERIES
    # -----------------------------------------------------

    with col_chart:

        st.subheader("NDVI Time Series")

        dates = pd.date_range(date_range[0],date_range[1])

        ts = pd.DataFrame({
            "Date":dates,
            "NDVI":np.clip(
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

        st.plotly_chart(fig,use_container_width=True)

# =========================================================
# STATISTICS TAB
# =========================================================

with tab2:

    st.subheader("Vegetation Classification")

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
# TERRAIN TAB
# =========================================================

with tab3:
    st.info("3D terrain visualization coming soon.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

c1,c2,c3 = st.columns(3)

c1.button("Download Data")
c2.button("Generate Report")
c3.button("About Dashboard")
