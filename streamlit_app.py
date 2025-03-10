import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import openaq

st.title("🌳 Tree Map (New York)")
st.markdown("Visualizing tree data with options for density, canopy coverage, heat island effect, and air quality correlation.")

# Sidebar for user controls
with st.sidebar:
    st.header("Map Controls")
    view_option = st.radio("Select View", ["Tree Density", "Tree Canopy Coverage", "Heat Island Effect", "Air Quality Correlation"])
    zoom_level = st.slider("Zoom Level", 10, 18, 12)
    radius = st.slider("Hexagon Radius (meters)", 50, 200, 50)
    elevation_scale = st.slider("Elevation Scale", 5, 20, 5)
    pitch = 45 if view_option == "Tree Density" else 0  # 3D for density, 2D otherwise
    bearing = st.slider("Map Bearing", 0, 360, 0)

st.markdown("### How Elevation is Calculated")
st.markdown("""
For **Tree Density**, elevation represents the number of trees within each hexagon.
For **Tree Canopy Coverage**, elevation represents estimated canopy coverage based on OSM data.
For **Heat Island Effect**, temperature data is overlaid with tree density to highlight urban heat zones.
For **Air Quality Correlation**, tree coverage is compared against AQI data from OpenAQ.

Higher density areas will have more intense colors in the heatmap.
""")

# Overpass API endpoint
url = "http://overpass-api.de/api/interpreter"

# Overpass Query for Trees in New York
query_trees = """
[out:json];
(
  node["natural"="tree"](40.70,-74.00,40.80,-73.90);
);
out;
"""

query_forest = """
[out:json];
(
  way["landuse"="forest"](40.70,-74.00,40.80,-73.90);
);
out geom;
"""

# Fetch tree data
response_trees = requests.get(url, params={"data": query_trees})
response_forest = requests.get(url, params={"data": query_forest})

tree_locations = []
df_trees = pd.DataFrame()
forest_polygons = []

if response_trees.status_code == 200:
    data_trees = response_trees.json()
    tree_locations = [
        {"lat": element["lat"], "lon": element["lon"]}
        for element in data_trees.get("elements", [])
    ]
    df_trees = pd.DataFrame(tree_locations)

if response_forest.status_code == 200:
    data_forest = response_forest.json()
    forest_polygons = [
        {"coordinates": [[(p["lon"], p["lat"]) for p in element["geometry"]]]}
        for element in data_forest.get("elements", [])
    ]

# Fetch AQI data from OpenAQ
api = openaq.OpenAQ()

def fetch_aqi_data(city='New York'):
    # status, resp = api.measurements.get(city=city, parameter='pm25', limit=100)
    # if status == 200:
    #     results = resp['results']
    #     aqi_data = [{'location': r['location'], 'value': r['value'], 'latitude': r['coordinates']['latitude'], 'longitude': r['coordinates']['longitude']} for r in results if 'coordinates' in r]
    #     return pd.DataFrame(aqi_data)
    # else:
    #     st.error("Failed to fetch AQI data.")
    #     return pd.DataFrame()
    print("LOL")

df_aqi = fetch_aqi_data()

def create_layer():
    hex_layer = pdk.Layer(
        "HexagonLayer",
        df_trees,
        get_position=["lon", "lat"],
        radius=radius,
        elevation_scale=elevation_scale,
        elevation_range=[0, 1000],
        extruded=True,
        coverage=1,
        color_range=[
            [0, 50, 0], [100, 200, 100], [150, 255, 150],
            [255, 255, 100], [255, 100, 50], [255, 0, 0]
        ],
        pickable=True,
    )
    canopy_layer = pdk.Layer(
        "ScatterplotLayer",
        df_trees,
        get_position=["lon", "lat"],
        get_radius=5,
        get_fill_color=[0, 0, 255, 255],
        pickable=True,
    )
    forest_layer = pdk.Layer(
        "PolygonLayer",
        forest_polygons,
        get_polygon="coordinates",
        get_fill_color=[0, 100, 0, 150],
        get_line_color=[0, 50, 0, 200],
        pickable=True,
    )
    # aqi_layer = pdk.Layer(
    #     "ScatterplotLayer",
    #     df_aqi,
    #     get_position=["longitude", "latitude"],
    #     get_color=[255, 0, 0, 160],
    #     get_radius=200,
    #     pickable=True,
    # )
    if view_option == "Tree Density":
        return [hex_layer]
    elif view_option == "Tree Canopy Coverage":
        return [canopy_layer, forest_layer]
    elif view_option == "Air Quality Correlation":
        # return [aqi_layer, canopy_layer, forest_layer]
        print("LOL")
    return []

if not df_trees.empty:
    layers = create_layer()
    view_state = pdk.ViewState(
        longitude=df_trees["lon"].mean() if not df_trees.empty else -73.95,
        latitude=df_trees["lat"].mean() if not df_trees.empty else 40.75,
        zoom=zoom_level,
        pitch=pitch,
        bearing=bearing,
    )

    tooltip = {
        "html": "<b>Location:</b> {location} <br/> <b>PM2.5:</b> {value} µg/m³" if view_option == "Air Quality Correlation" else "<b>Tree Data:</b> {elevationValue}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip
    )

    st.pydeck_chart(deck)
