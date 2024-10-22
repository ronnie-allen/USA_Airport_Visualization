import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from datetime import datetime

# Load your dataset (replace with your file path or database)
@st.cache
def load_data():
    data = pd.read_csv('./Airports2.csv')
    data['Fly_date'] = pd.to_datetime(data['Fly_date'])  # Convert date column to datetime
    return data

# Load and cache data
data = load_data()

# Sidebar filters
st.sidebar.title("Filter Options")
selected_origin_airport = st.sidebar.selectbox("Select Origin Airport", data['Origin_airport'].unique())
selected_destination_airport = st.sidebar.selectbox("Select Destination Airport", data['Destination_airport'].unique())
selected_date_range = st.sidebar.date_input("Select Date Range", [data['Fly_date'].min(), data['Fly_date'].max()])
selected_distance_range = st.sidebar.slider("Select Flight Distance Range", int(data['Distance'].min()), int(data['Distance'].max()), (100, 3000))

# Apply filters
filtered_data = data[
    (data['Origin_airport'] == selected_origin_airport) &
    (data['Destination_airport'] == selected_destination_airport) &
    (data['Fly_date'] >= pd.to_datetime(selected_date_range[0])) &
    (data['Fly_date'] <= pd.to_datetime(selected_date_range[1])) &
    (data['Distance'] >= selected_distance_range[0]) &
    (data['Distance'] <= selected_distance_range[1])
]

# Flight Route Visualization (Map)
st.subheader("Flight Route Map")
if len(filtered_data) > 0:
    fig = px.scatter_mapbox(
        filtered_data,
        lat="Org_airport_lat",
        lon="Org_airport_long",
        color="Passengers",
        size="Passengers",
        hover_name="Origin_city",
        hover_data=["Destination_city", "Distance", "Passengers"],
        title=f"Flights from {selected_origin_airport} to {selected_destination_airport}",
        mapbox_style="carto-positron",
        zoom=3,
        height=500
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

# Passenger Flow Scatter Plot
st.subheader("Passenger Flow Analysis")
if len(filtered_data) > 0:
    scatter_fig = px.scatter(
        filtered_data, 
        x="Distance", 
        y="Passengers", 
        size="Flights", 
        color="Flights",
        hover_name="Origin_airport",
        title="Distance vs. Passengers",
        labels={"Distance": "Flight Distance (miles)", "Passengers": "Passenger Count"}
    )
    st.plotly_chart(scatter_fig)
else:
    st.write("No data available for the selected filters.")

# Flight Capacity Utilization
st.subheader("Flight Capacity Utilization")
if len(filtered_data) > 0:
    capacity_utilization = filtered_data.copy()
    capacity_utilization['Utilization (%)'] = (capacity_utilization['Passengers'] / capacity_utilization['Seats']) * 100
    bar_chart = px.bar(
        capacity_utilization,
        x="Origin_airport",
        y="Utilization (%)",
        color="Utilization (%)",
        hover_data=["Passengers", "Seats"],
        title="Flight Capacity Utilization",
        labels={"Origin_airport": "Airport", "Utilization (%)": "Utilization (%)"}
    )
    st.plotly_chart(bar_chart)
else:
    st.write("No data available for the selected filters.")

# Busiest Airports
st.subheader("Top 10 Busiest Airports")
busiest_airports = data.groupby('Origin_airport').agg({'Passengers': 'sum'}).reset_index().nlargest(10, 'Passengers')
if len(busiest_airports) > 0:
    bar_chart_airports = px.bar(
        busiest_airports,
        x="Origin_airport",
        y="Passengers",
        title="Top 10 Busiest Airports by Passenger Count",
        labels={"Origin_airport": "Airport", "Passengers": "Total Passengers"}
    )
    st.plotly_chart(bar_chart_airports)
else:
    st.write("No data available for the selected filters.")

# Footer
st.markdown("---")
st.write("Dashboard built using Streamlit, Plotly, and Geopandas.")
