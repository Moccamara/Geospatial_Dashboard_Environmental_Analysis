import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import ee
import plotly.express as px

# =========================================================
# INITIALIZE EARTH ENGINE
# =========================================================
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

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
    ["MODIS", "Landsat 8"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [pd.to_datetime("2023-06-01"), pd.to_datetime("2023-06-30")]
)

# =========================================================
# FUNCTIONS
# =========================================================
def add_country_boundary(map_obj):
    """Add Mali boundary if file exists"""
    try:
        mali = gpd.read_file("mali_boundary.geojson")
        folium.GeoJson(
            mali,
            name="Mali Boundary",
            style_function=lambda x: {"fillColor":"none","color":"black","weight":2}
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

def fetch_ndvi(region_geom, start_date, end_date, dataset_name="MODIS"):
    """Fetch NDVI from MODIS or Landsat"""
    if dataset_name == "MODIS":
        collection = ee.ImageCollection('MODIS/006/MOD13Q1') \
            .select('NDVI') \
            .filterDate(start_date, end_date)
        ndvi_img = collection.mean().clip(region_geom)
    elif dataset_name == "Landsat 8":
        collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
            .filterDate(start_date, end_date) \
            .map(lambda img: img.normalizedDifference(['B5','B4']).rename('NDVI'))
        ndvi_img = collection.mean().clip(region_geom)
    else:
        st.error("Dataset not supported")
        return None
    return ndvi_img

def sample_ndvi_image(ndvi_img, region_geom, num_pixels=1000, scale=500):
    """Convert NDVI image to pandas DataFrame for visualization"""
    sample = ndvi_img.sample(region=region_geom, scale=scale, numPixels=num_pixels)
    sample_dict = sample.getInfo()
    features = sample_dict['features']
    df = pd.DataFrame([{
        'lon': f['geometry']['coordinates'][0],
        'lat': f['geometry']['coordinates'][1],
        'ndvi': f['properties']['NDVI']/10000.0 if f['properties']['NDVI'] > 1 else f['properties']['NDVI']
    } for f in features])
    return df

# =========================================================
# LOAD REGION GEOMETRY
# =========================================================
try:
    mali_gdf = gpd.read_file("mali_boundary.geojson")
    mali_geom = ee.Geometry.Polygon(list(mali_gdf.geometry.iloc[0].exterior.coords))
except:
    st.warning("Mali boundary file not found. Using default rectangle.")
    mali_geom = ee.Geometry.Rectangle([-12,10,4,25])

# =========================================================
# FETCH NDVI DATA
# =========================================================
with st.spinner("Fetching NDVI data from Earth Engine..."):
    ndvi_image = fetch_ndvi(mali_geom, str(date_range[0]), str(date_range[1]), dataset)
    ndvi_df = sample_ndvi_image(ndvi_image, mali_geom)

# NDVI stats
mean_ndvi = ndvi_df["ndvi"].mean()
max_ndvi = ndvi_df["ndvi"].max()
min_ndvi = ndvi_df["ndvi"].min()

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(["NDVI Map","Statistics","3D Terrain"])

# =========================================================
# MAP TAB
# =========================================================
with tab1:
    col_map, col_chart = st.columns([3,1.5])

    with col_map:
        st.subheader("NDVI Spatial Distribution")
        m = folium.Map(location=[17,-4], zoom_start=5, tiles="cartodbpositron")
        add_country_boundary(m)

        for _, r in ndvi_df.iterrows():
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
        c1.metric("Mean NDVI", f"{mean_ndvi:.2f}")
        c2.metric("Max NDVI", f"{max_ndvi:.2f}")
        c3.metric("Min NDVI", f"{min_ndvi:.2f}")

    with col_chart:
        st.subheader("NDVI Time Series")
        dates = pd.date_range(date_range[0], date_range[1])
        ts = pd.DataFrame({
            "Date": dates,
            "NDVI": ndvi_df["ndvi"].sample(len(dates), replace=True).values
        })
        fig = px.line(ts, x="Date", y="NDVI", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# STATISTICS TAB
# =========================================================
with tab2:
    st.subheader("Vegetation Classification")
    veg = pd.DataFrame({
        "Class":["Dense Vegetation","Moderate Vegetation","Sparse Vegetation","Bare Soil"],
        "NDVI Range":["0.6 – 1","0.3 – 0.6","0 – 0.3","< 0"]
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
