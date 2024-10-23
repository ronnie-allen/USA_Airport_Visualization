import streamlit as st  # Web app framework  
import numpy as np  # Numerical operations
import pandas as pd  # DataFrame manipulation
import plotly.express as px  # For interactive charts
import folium  # For geographic visualization
from folium.plugins import AntPath  # For animated paths
from streamlit_folium import folium_static  # Import folium_static for displaying Folium maps
import time  # For live simulation delay

# Load your data
df = pd.read_csv('./droped_data.csv')

# Ensure 'Fly_date' is in datetime format
df['Fly_date'] = pd.to_datetime(df['Fly_date'])

# Set Streamlit page configuration
st.set_page_config(
    page_title="Real-Time USA Airport Dashboard",
    page_icon="✅",
    layout="wide"
)

# Dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# Top-level filter (e.g., select airport)
airport_filter = st.selectbox("Select the Airport", pd.unique(df['Origin_airport']))

# Initialize session state for live data accumulation
if 'df_live' not in st.session_state:
    st.session_state.df_live = pd.DataFrame(columns=df.columns)

# Create a placeholder for the dashboard
placeholder = st.empty()

# Infinite loop for real-time updates
while True:
    # Filter the DataFrame based on the selected airport
    df_filtered = df[df['Origin_airport'] == airport_filter]

    # Simulate real-time data updates
    df_filtered['Passengers_new'] = df_filtered['Passengers'] * np.random.choice(range(1, 500))
    df_filtered['Flights_new'] = df_filtered['Flights'] * np.random.choice(range(1, 500))

    # Append the new data to the live DataFrame
    st.session_state.df_live = pd.concat([st.session_state.df_live, df_filtered], ignore_index=True)

    # Calculate KPIs (Key Performance Indicators)
    avg_passengers = np.mean(df_filtered['Passengers_new'])
    total_seats = int(df_filtered['Seats'].sum() + np.random.choice(range(1, 300)))
    avg_flights = np.mean(df_filtered['Flights_new'])

    # Display the updated metrics and visualizations
    with placeholder.container():
        # Create three columns for the KPIs
        kpi1, kpi2, kpi3 = st.columns(3)

        # Fill in the columns with the KPI values
        kpi1.metric(label="Avg Passengers ✈️", value=round(avg_passengers), delta=round(avg_passengers) - 100)
        kpi2.metric(label="Total Seats 💺", value=total_seats, delta=-10 + total_seats)
        kpi3.metric(label="Avg Flights 🛫", value=round(avg_flights), delta=round(avg_flights) - 50)

        # Create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Flights vs Seats Heatmap")
            fig1 = px.density_heatmap(data_frame=df_filtered, x='Flights_new', y='Seats')
            st.write(fig1)

        with fig_col2:
            st.markdown("### Passengers Distribution")
            fig2 = px.histogram(data_frame=df_filtered, x='Passengers_new', nbins=50)
            st.write(fig2)

        # Add a new column for scatter plot and pie chart
        scatter_col, pie_col = st.columns(2)

        with scatter_col:
            st.markdown("### Passengers vs Flights Scatter Plot")
            scatter_fig = px.scatter(df_filtered, x='Passengers_new', y='Flights_new', 
                                     title="Scatter Plot of Passengers vs Flights",
                                     labels={'Passengers_new': 'Number of Passengers', 'Flights_new': 'Number of Flights'})
            st.write(scatter_fig)

        with pie_col:
            st.markdown("### Passenger Distribution Pie Chart")
            pie_fig = px.pie(df_filtered, names='Destination_city', values='Passengers_new', 
                             title='Passenger Distribution by Origin City')
            st.write(pie_fig)

        # Create histogram for Fly_date
        st.markdown("### Flights Over Time Histogram")
        histogram_fig = px.histogram(
            df_filtered,
            x='Fly_date',
            title="Histogram of Flights Over Time",
            labels={'Fly_date': 'Date', 'count': 'Number of Flights'},
            nbins=30  # Adjust the number of bins as necessary
        )
        st.write(histogram_fig)

        # Normalize flights and passengers data to percentages
        df_filtered['Flights_percentage'] = df_filtered['Flights_new'] / df_filtered['Flights_new'].sum() * 100
        df_filtered['Passengers_percentage'] = df_filtered['Passengers_new'] / df_filtered['Passengers_new'].sum() * 100

        # Histogram for Flights and Passengers as percentages
        st.markdown("### Flights and Passengers Percentage Over Time (Yearly)")
        fig3 = px.histogram(
            df_filtered, 
            x='Fly_date', 
            y=['Flights_percentage', 'Passengers_percentage'], 
            barmode='group',
            labels={'value': 'Percentage', 'Year': 'Year'}, 
            title="Flights and Passengers as Percentage per Year"
        )
        st.write(fig3)

        # Add a new line chart for Total Passengers Over Time
        st.markdown("### Total Passengers Over Time")
        line_chart = px.line(
            df_filtered,
            x='Fly_date',
            y='Passengers_new',
            title="Total Passengers Over Time",
            labels={'Passengers_new': 'Total Passengers', 'Fly_date': 'Date'}
        )
        st.write(line_chart)

        # Live Detailed Data View (Accumulated Data)
        st.markdown("### Live Detailed Data View (Accumulated Data)")
        st.dataframe(st.session_state.df_live)

        # Folium Map for Flight Routes
        st.markdown("### Flight Routes Map")
        flight_map = folium.Map(location=[df_filtered['Org_airport_lat'].mean(), df_filtered['Org_airport_long'].mean()], zoom_start=4)

        # Add flight routes
        for index, row in df_filtered.iterrows():
            folium.Marker(
                location=[row['Org_airport_lat'], row['Org_airport_long']],
                popup=f"Origin: {row['Origin_city']}",
                icon=folium.Icon(color='blue')
            ).add_to(flight_map)

            folium.Marker(
                location=[row['Dest_airport_lat'], row['Dest_airport_long']],
                popup=f"Destination: {row['Destination_city']}",
                icon=folium.Icon(color='red')
            ).add_to(flight_map)

            # Add an animated path from origin to destination
            AntPath(
                locations=[
                    [row['Org_airport_lat'], row['Org_airport_long']],
                    [row['Dest_airport_lat'], row['Dest_airport_long']]
                ],
                dash_array=[20, 20],
                delay=999990000,
                color='green',
                # pulse_color='blue',
                weight=5,
                opacity=0.8,
            ).add_to(flight_map)

        # Render the Folium map with increased size
        folium_static(flight_map, width=1000, height=600)  # Set the width and height to desired values

# Delay for 2 seconds before rerunning
time.sleep(2)

    # Rerun the Streamlit script to refresh the output
    # st.experimental_rerun()
