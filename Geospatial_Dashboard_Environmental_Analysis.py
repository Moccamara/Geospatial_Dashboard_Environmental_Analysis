import streamlit as st
import ee
import geemap.foliumap as geemap
import geopandas as gpd
from fpdf import FPDF
import tempfile
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Geospatial Dashboard – Environmental Analysis",
    layout="wide"
)

# =========================================================
# GOOGLE EARTH ENGINE INIT
# =========================================================
ee.Initialize()

# =========================================================
# HEADER
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
</style>

<div class="header">
    <h2>Geospatial Dashboard – Environmental Analysis</h2>
    <p>Sentinel-2 NDVI | Google Earth Engine | Mali</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR – FILTERS
# =========================================================
st.sidebar.header("Data Filters")

dataset = st.sidebar.selectbox(
    "Dataset",
    ["NDVI (Sentinel-2)"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [pd.to_datetime("2021-06-01"), pd.to_datetime("2021-06-30")]
)

apply = st.sidebar.button("Apply Filters", use_container_width=True)

if not apply:
    st.info("Adjust filters and click **Apply Filters**")
    st.stop()

# =========================================================
# LOAD MALI BOUNDARY (GEE)
# =========================================================
mali = ee.FeatureCollection("FAO/GAUL/2015/level0") \
          .filter(ee.Filter.eq("ADM0_NAME", "Mali"))

# =========================================================
# SENTINEL-2 NDVI
# =========================================================
start_date = str(date_range[0])
end_date = str(date_range[1])

s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
    .filterBounds(mali) \
    .filterDate(start_date, end_date) \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))

ndvi = s2.map(
    lambda img: img.normalizedDifference(["B8", "B4"])
                  .rename("NDVI")
).mean().clip(mali)

# =========================================================
# NDVI STATISTICS
# =========================================================
stats = ndvi.reduceRegion(
    reducer=ee.Reducer.mean()
            .combine(ee.Reducer.min(), "", True)
            .combine(ee.Reducer.max(), "", True),
    geometry=mali.geometry(),
    scale=10,
    maxPixels=1e13
).getInfo()

mean_val = stats["NDVI_mean"]
min_val = stats["NDVI_min"]
max_val = stats["NDVI_max"]

# =========================================================
# LAYOUT
# =========================================================
col_map, col_stats = st.columns([3, 1])

# =========================================================
# MAP
# =========================================================
with col_map:
    st.subheader("NDVI Map – Mali (Sentinel-2)")

    Map = geemap.Map(center=[17, -4], zoom=5)

    ndvi_vis = {
        "min": 0,
        "max": 1,
        "palette": ["red", "yellow", "green"]
    }

    Map.addLayer(ndvi, ndvi_vis, "NDVI")
    Map.addLayer(mali, {"color": "black"}, "Mali Boundary")

    Map.to_streamlit(height=520)

# =========================================================
# STATISTICS
# =========================================================
with col_stats:
    st.subheader("Statistics")

    st.metric("Mean NDVI", f"{mean_val:.2f}")
    st.metric("Max NDVI", f"{max_val:.2f}")
    st.metric("Min NDVI", f"{min_val:.2f}")

    st.markdown("---")

    # =====================================================
    # PDF REPORT
    # =====================================================
    def generate_pdf(mean_v, min_v, max_v):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        pdf.cell(0, 10, "NDVI Environmental Report – Mali", ln=True)
        pdf.ln(5)

        pdf.cell(0, 10, f"Period: {start_date} to {end_date}", ln=True)
        pdf.ln(5)

        pdf.cell(0, 10, f"Mean NDVI: {mean_v:.2f}", ln=True)
        pdf.cell(0, 10, f"Maximum NDVI: {max_v:.2f}", ln=True)
        pdf.cell(0, 10, f"Minimum NDVI: {min_v:.2f}", ln=True)

        pdf.ln(10)
        pdf.multi_cell(
            0, 8,
            "This report was generated using Sentinel-2 imagery "
            "processed in Google Earth Engine and visualized "
            "through a Streamlit-based Geospatial Dashboard."
        )

        path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        pdf.output(path)
        return path

    pdf_path = generate_pdf(mean_val, min_val, max_val)

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📄 Download NDVI Report (PDF)",
            f,
            file_name="NDVI_Mali_Report.pdf",
            mime="application/pdf"
        )

# =========================================================
# FOOTER
# =========================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.caption(
    "© Geospatial Dashboard | Sentinel-2 • Google Earth Engine • Mali"
)
