import streamlit as st
import pydeck as pdk

# 🔑 Your Mapbox API Key (replace with your real key)
MAPBOX_TOKEN = "pk.eyJ1IjoicmFtYWRoYW5pMDE1IiwiYSI6ImNtN2p6N21oaDBhaDcyanMzMHRiNjJsOTEifQ.tS3O3ERXLBjrqlfYep2OLQ"

# 📌 Define locations
locations = {
    "Mount Merapi, Indonesia": [110.44, -7.54, 10],
    "Mount Bromo, Indonesia": [112.95, -7.92, 11],
    "Jakarta, Indonesia": [106.85, -6.2, 10]
}

# 🌍 Select a location
selected_location = st.selectbox("Choose a location:", list(locations.keys()))
longitude, latitude, zoom = locations[selected_location]

# 🎨 Define a color ramp (low = green, high = white)
color_ramp = [
    [0, [34, 139, 34]],  # Low elevation = Green
    [500, [110, 204, 57]],  # Slightly higher = Light green
    [1000, [255, 255, 102]],  # Medium = Yellow
    [2000, [255, 165, 0]],  # Higher = Orange
    [3000, [255, 69, 0]],  # Very high = Red
    [4000, [255, 255, 255]]  # Highest = White
]

# 🏔️ Pydeck TerrainLayer with Color Ramp
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={
        "rScaler": 65536,
        "gScaler": 256,
        "bScaler": 1,
        "off
