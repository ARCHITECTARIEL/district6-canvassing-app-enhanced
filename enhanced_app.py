import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from datetime import datetime
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import geopandas as gpd
from folium.plugins import MarkerCluster, LocateControl

# Set page configuration
st.set_page_config(
    page_title="District 6 Canvassing App",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create database connection
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('canvassing_data.db', check_same_thread=False)
    return conn

# Initialize database
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create volunteers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create precincts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS precincts (
        id TEXT PRIMARY KEY,
        name TEXT,
        total_addresses INTEGER,
        owner_occupied INTEGER,
        non_owner_occupied INTEGER
    )
    ''')
    
    # Create interaction_notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interaction_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address_id INTEGER NOT NULL,
        volunteer_name TEXT NOT NULL,
        note_text TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()

# Load real precinct data from shapefile
@st.cache_data
def load_precinct_boundaries():
    try:
        # Path to the shapefile
        shapefile_path = "PrecinctsDistrict6.shp"
        
        # Read the shapefile
        gdf = gpd.read_file(shapefile_path)
        return gdf
    except Exception as e:
        st.error(f"Error loading precinct boundaries: {e}")
        return None

# Load real voter data from JSON
@st.cache_data
def load_voter_data():
    try:
        # Path to the JSON file
        json_path = "Advanced Search 4-11-2025.json"
        
        # Read the JSON file
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading voter data: {e}")
        return []

# Load past election results
@st.cache_data
def load_election_results():
    try:
        # Path to the Excel file
        excel_path = "DISTRICT6.xlsx"
        
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        return df
    except Exception as e:
        st.error(f"Error loading election results: {e}")
        return pd.DataFrame()

# Extract precinct information from the shapefile
@st.cache_data
def load_precinct_data():
    try:
        gdf = load_precinct_boundaries()
        election_df = load_election_results()
        
        if gdf is None:
            # Fallback to sample data if shapefile can't be loaded
            return [
                {"id": "123", "name": "Precinct 123", "total_addresses": 1253},
                {"id": "125", "name": "Precinct 125", "total_addresses": 2577},
                {"id": "130", "name": "Precinct 130", "total_addresses": 1615}
            ]
        
        # Extract precinct information
        precincts = []
        for _, row in gdf.iterrows():
            precinct_id = str(row.get('PRECINCT', ''))
            if precinct_id:
                # Try to get turnout data from election results
                turnout = None
                ballots_cast = None
                registered_voters = None
                
                if not election_df.empty:
                    precinct_data = election_df[election_df['Precinct'] == float(precinct_id)]
                    if not precinct_data.empty:
                        turnout = precinct_data['Voter Turnout'].values[0]
                        ballots_cast = precinct_data['Ballots Cast'].values[0]
                        registered_voters = precinct_data['Active Registered Voters'].values[0]
                
                precincts.append({
                    "id": precinct_id,
                    "name": f"Precinct {precinct_id}",
                    "total_addresses": 0,  # Will be updated when we process voter data
                    "turnout": turnout,
                    "ballots_cast": ballots_cast,
                    "registered_voters": registered_voters
                })
        
        return precincts
    except Exception as e:
        st.error(f"Error processing precinct data: {e}")
        return []

# Load census demographic data
@st.cache_data
def load_census_data():
    # This would typically fetch data from an API or read from files
    # For this example, we'll use hardcoded data from the census profiles
    
    census_data = {
        "33701": {
            "total_population": 9137,
            "median_household_income": 67098,
            "bachelors_degree_or_higher": "54.2%",
            "employment_rate": "60.3%",
            "total_housing_units": 6487,
            "without_health_insurance": "9.2%",
            "total_households": 4632
        },
        "33705": {
            "total_population": 27915,
            "median_household_income": 47783,
            "bachelors_degree_or_higher": "30.2%",
            "employment_rate": "56.3%",
            "total_housing_units": 14073,
            "without_health_insurance": "13.2%",
            "total_households": 11300
        }
    }
    
    return census_data

# Load addresses for a specific precinct
@st.cache_data
def load_precinct_addresses(precinct_id):
    try:
        # Get all voter data
        voter_data = load_voter_data()
        
        # Get precinct boundaries
        gdf = load_precinct_boundaries()
        
        if not voter_data or gdf is None:
            # Fallback to sample data
            return generate_sample_addresses(precinct_id)
        
        # Filter the precinct boundary
        precinct_boundary = gdf[gdf['PRECINCT'] == int(precinct_id)]
        
        if precinct_boundary.empty:
            return generate_sample_addresses(precinct_id)
        
        # Convert addresses to GeoDataFrame
        addresses = []
        for i, property_data in enumerate(voter_data):
            # Extract address components
            street_num = property_data.get('STR_NUM', '')
            street_name = property_data.get('STR_NAME', '')
            street_unit = property_data.get('STR_UNIT', '')
            zip_code = property_data.get('STR_ZIP', '')
            
            # Skip if missing essential address components
            if not street_num or not street_name:
                continue
            
            # Create full address
            address = f"{street_num} {street_name}"
            if street_unit:
                address += f" {street_unit}"
            
            # For this demo, we'll assign addresses to precincts based on a simple algorithm
            # In a real app, you would use point-in-polygon spatial operations
            # Here we're just using the last digit of the street number as a simple assignment
            if street_num % 10 == int(precinct_id) % 10:
                owner1 = property_data.get('OWNER1', '')
                owner2 = property_data.get('OWNER2', '')
                property_type = property_data.get('PROPERTY_USE', '').split(' ')[1] if property_data.get('PROPERTY_USE', '') else 'Unknown'
                owner_occupied = "Yes" if property_data.get('HX_YN', '') == "Yes" else "No"
                
                # Create address entry
                addresses.append({
                    "id": i + 1,
                    "precinct_id": precinct_id,
                    "owner1": owner1,
                    "owner2": owner2 if owner2 else "",
                    "address": address,
                    "city_zip": property_data.get('SITE_CITYZIP', ''),
                    "street_number": street_num,
                    "street_name": street_name,
                    "unit": street_unit if street_unit else "",
                    "zip_code": zip_code,
                    "property_type": property_type,
                    "owner_occupied": owner_occupied,
                    # Generate approximate coordinates for demo purposes
                    # In a real app, you would geocode these addresses
                    "latitude": 27.77 + (i % 10) * 0.001,
                    "longitude": -82.64 + (i % 5) * 0.001
                })
                
                # Limit to 50 addresses per precinct for demo performance
                if len(addresses) >= 50:
                    break
        
        return addresses
    except Exception as e:
        st.error(f"Error loading precinct addresses: {e}")
        return generate_sample_addresses(precinct_id)

# Generate sample addresses as fallback
def generate_sample_addresses(precinct_id):
    sample_addresses = []
    streets = ["MAIN ST", "OAK AVE", "PINE ST", "MAPLE DR", "CEDAR LN", "BEACH BLVD", "CENTRAL AVE"]
    property_types = ["Single Family", "Condominium", "Duplex", "Apartment", "Townhouse"]
    owner_occupied = ["Yes", "No"]
    
    # Base coordinates for St. Petersburg, FL
    base_lat = 27.77
    base_lng = -82.64
    
    # Generate sample addresses
    for i in range(min(20, int(precinct_id) * 2)):
        street = streets[i % len(streets)]
        street_num = 100 + i * 10
        
        # Create slight variations in coordinates
        lat = base_lat + (i % 10) * 0.001
        lng = base_lng + (i % 5) * 0.001
        
        sample_addresses.append({
            "id": i + 1,
            "precinct_id": precinct_id,
            "owner1": f"SMITH, JOHN {i}",
            "owner2": "SMITH, JANE" if i % 3 == 0 else "",
            "address": f"{street_num} {street}",
            "city_zip": "ST PETERSBURG, FL 33701",
            "street_number": street_num,
            "street_name": street,
            "unit": "" if i % 4 != 0 else f"#{i % 10}",
            "zip_code": "33701",
            "property_type": property_types[i % len(property_types)],
            "owner_occupied": owner_occupied[i % len(owner_occupied)],
            "latitude": lat,
            "longitude": lng
        })
    
    return sample_addresses

# Get canvassing statistics
def get_stats():
    # Return sample data for demo
    return {
        'total_interactions': 42,
        'total_addresses_contacted': 28,
        'total_addresses': 100,
        'coverage_percentage': 28.0,
        'response_breakdown': {
            "supportive": 19,
            "leaning": 5,
            "undecided": 8,
            "opposed": 7,
            "not-home": 3
        },
        'precinct_coverage': [
            {"id": "123", "name": "Precinct 123", "total_addresses": 1253, "addresses_contacted": 245},
            {"id": "125", "name": "Precinct 125", "total_addresses": 2577, "addresses_contacted": 512},
            {"id": "130", "name": "Precinct 130", "total_addresses": 1615, "addresses_contacted": 324}
        ]
    }

# Create a map with addresses and precinct boundaries
def create_map(addresses, center=None, precinct_id=None):
    # Default center if none provided
    if center is None:
        center = [27.77, -82.64]
    
    # Create map
    m = folium.Map(location=center, zoom_start=14, tiles="OpenStreetMap")
    
    # Add locate control
    LocateControl().add_to(m)
    
    # Try to add precinct boundary
    try:
        if precinct_id:
            gdf = load_precinct_boundaries()
            if gdf is not None:
                # Filter to the selected precinct
                precinct_boundary = gdf[gdf['PRECINCT'] == int(precinct_id)]
                
                if not precinct_boundary.empty:
                    # Convert to GeoJSON
                    geo_json = folium.GeoJson(
                        precinct_boundary,
                        style_function=lambda x: {
                            'fillColor': '#3186cc',
                            'color': '#000000',
                            'weight': 2,
                            'fillOpacity': 0.2
                        },
                        name=f"Precinct {precinct_id}"
                    )
                    geo_json.add_to(m)
    except Exception as e:
        st.warning(f"Could not display precinct boundary: {e}")
    
    # Create marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each address
    for address in addresses:
        if address.get('latitude') and address.get('longitude'):
            # Create popup content
            owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
            address_text = f"{address.get('address', '')}, {address.get('city_zip', '')}"
            property_info = f"{address.get('property_type', 'Unknown')} • {'Owner Occupied' if address.get('owner_occupied') == 'Yes' else 'Not Owner Occupied'}"
            
            popup_html = f"""
            <strong>{owner}</strong><br>
            {address_text}<br>
            <small>{property_info}</small>
            """
            
            # Add marker
            folium.Marker(
                location=[address['latitude'], address['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon="home", prefix="fa")
            ).add_to(marker_cluster)
    
    return m

# Get interaction notes for an address
def get_interaction_notes(address_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, volunteer_name, note_text, tags, created_at
    FROM interaction_notes
    WHERE address_id = ?
    ORDER BY created_at DESC
    ''', (address_id,))
    
    notes = []
    for row in cursor.fetchall():
        notes.append({
            "id": row[0],
            "volunteer_name": row[1],
            "note_text": row[2],
            "tags": row[3].split(",") if row[3] else [],
            "created_at": row[4]
        })
    
    return notes

# Save interaction note
def save_interaction_note(address_id, volunteer_name, note_text, tags):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert tags list to comma-separated string
    tags_str = ",".join(tags) if tags else ""
    
    cursor.execute('''
    INSERT INTO interaction_notes (address_id, volunteer_name, note_text, tags, created_at)
    VALUES (?, ?, ?, ?, datetime('now'))
    ''', (address_id, volunteer_name, note_text, tags_str))
    
    conn.commit()
    return cursor.lastrowid

# Initialize session state
if 'volunteer_name' not in st.session_state:
    st.session_state.volunteer_name = "Jane Doe"
if 'selected_precinct' not in st.session_state:
    st.session_state.selected_precinct = None
if 'addresses' not in st.session_state:
    st.session_state.addresses = []
if 'visited_addresses' not in st.session_state:
    st.session_state.visited_addresses = set()
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Home"
if 'selected_address_id' not in st.session_state:
    st.session_state.selected_address_id = None

# Initialize database
init_db()

# Sidebar for navigation
st.sidebar.title("District 6 Canvassing")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Map_icon.svg/1200px-Map_icon.svg.png", width=100)

# Navigation
tab = st.sidebar.radio("Navigation", ["Home", "Demographics", "Election History", "Stats", "Settings"])
st.session_state.current_tab = tab

# Volunteer info in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Volunteer:** {st.session_state.volunteer_name}")
if st.sidebar.button("Sync Data"):
    st.sidebar.success("Data synchronized successfully!")

# Main content area
if st.session_state.current_tab == "Home":
    st.title("District 6 Door Knocking Campaign")
    
    # Precinct selector
    precincts = load_precinct_data()
    precinct_options = ["Select a precinct"] + [f"Precinct {p['id']}" for p in precincts]
    selected_option = st.selectbox("Select Precinct:", precinct_options)
    
    if selected_option != "Select a precinct":
        # Extract precinct ID from selection
        precinct_id = selected_option.split()[1]
        
        # Load addresses if precinct changed
        if st.session_state.selected_precinct != precinct_id:
            st.session_state.selected_precinct = precinct_id
            st.session_state.addresses = load_precinct_addresses(precinct_id)
            st.session_state.visited_addresses = set()
            st.rerun()
        
        # Display map
        if st.session_state.addresses:
            # Find center of addresses
            lats = [a['latitude'] for a in st.session_state.addresses if 'latitude' in a]
            lngs = [a['longitude'] for a in st.session_state.addresses if 'longitude' in a]
            if lats and lngs:
                center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
                m = create_map(st.session_state.addresses, center, precinct_id)
                st.subheader("Precinct Map")
                folium_static(m, width=800, height=500)
            
            # Progress tracking
            total_addresses = len(st.session_state.addresses)
            visited_count = len(st.session_state.visited_addresses)
            remaining_count = total_addresses - visited_count
            percentage = (visited_count / total_addresses * 100) if total_addresses > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Progress", f"{visited_count}/{total_addresses} ({percentage:.1f}%)")
            with col2:
                st.metric("Remaining", remaining_count)
            
            st.progress(percentage / 100)
            
            # Address list
            st.subheader("Addresses to Visit")
            
            for i, address in enumerate(st.session_state.addresses):
                address_id = address.get('id', i)
                visited = address_id in st.session_state.visited_addresses
                
                # Create a card-like container for each address
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
                        address_text = f"{address.get('address', '')}, {address.get('city_zip', '')}"
                        property_info = f"{address.get('property_type', 'Unknown')} • {'Owner Occupied' if address.get('owner_occupied') == 'Yes' else 'Not Owner Occupied'}"
                        
                        st.markdown(f"**{owner}**")
                        st.text(address_text)
                        st.text(property_info)
                    
                    with col2:
                        if not visited:
                            if st.button("Contact", key=f"contact_{address_id}"):
                                st.session_state.selected_address_id = address_id
                                st.session_state.visited_addresses.add(address_id)
                                st.success("Interaction recorded successfully!")
                                
                                # Show interaction notes form
                                with st.expander("Add Interaction Notes", expanded=True):
                                    add_interaction_notes(address_id)
                                
                                st.rerun()
                            
                            if st.button("Not Home", key=f"nothome_{address_id}"):
                                st.session_state.visited_addresses.add(address_id)
                                
                                # Automatically add a "Not Home" note
                                save_interaction_note(
                                    address_id, 
                                    st.session_state.volunteer_name, 
                                    "Resident not home during canvassing visit.", 
                                    ["not-home"]
                                )
                                
                                st.success("Marked as Not Home")
                                st.rerun()
                            
                            if st.button("Skip", key=f"skip_{address_id}"):
                                st.session_state.visited_addresses.add(address_id)
                                st.success("Marked as Skipped")
                                st.rerun()
                        else:
                            st.success("Visited")
                            
                            # Show view notes button
                            if st.button("View Notes", key=f"viewnotes_{address_id}"):
                                st.session_state.selected_address_id = address_id
                                st.rerun()
                    
                    # Display notes if this address is selected
                    if st.session_state.selected_address_id == address_id:
                        with st.expander("Interaction Notes", expanded=True):
                            # Display existing notes
                            notes = get_interaction_notes(address_id)
                            if notes:
                                for note in notes:
                                    st.markdown(f"**{note['volunteer_name']}** - {note['created_at']}")
                                    st.markdown(note['note_text'])
                                    if note['tags']:
                                        st.markdown(" ".join([f"**#{tag}**" for tag in note['tags']]))
                                    st.markdown("---")
                            else:
                                st.info("No notes recorded yet.")
                            
                            # Add new note
                            add_interaction_notes(address_id)
                    
                    st.markdown("---")
    else:
        st.info("Please select a precinct to begin canvassing")

elif st.session_state.current_tab == "Demographics":
    st.title("Neighborhood Demographics")
    
    # Load census data
    census_data = load_census_data()
    
    # Create tabs for each ZIP code
    zip_tabs = st.tabs(["ZIP 33701", "ZIP 33705", "Compare"])
    
    with zip_tabs[0]:
        st.header("ZIP Code 33701")
        
        # Display demographic data
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Population", census_data["33701"]["total_population"])
            st.metric("Median Household Income", f"${census_data['33701']['median_household_income']:,}")
            st.metric("Bachelor's Degree or Higher", census_data["33701"]["bachelors_degree_or_higher"])
            st.metric("Employment Rate", census_data["33701"]["employment_rate"])
        
        with col2:
            st.metric("Total Housing Units", census_data["33701"]["total_housing_units"])
            st.metric("Without Health Insurance", census_data["33701"]["without_health_insurance"])
            st.metric("Total Households", census_data["33701"]["total_households"])
        
        # Add more detailed demographic information
        st.subheader("Key Demographics")
        st.markdown("""
        ZIP code 33701 covers downtown St. Petersburg and the surrounding areas. Key characteristics include:
        
        - Higher median income compared to the city average
        - Higher education levels with over half of residents having a bachelor's degree or higher
        - Mix of single-family homes and condominiums
        - Growing population of young professionals
        - Significant number of retirees and seasonal residents
        """)
        
        st.subheader("Canvassing Tips for 33701")
        st.markdown("""
        - Many residents in this area are well-educated professionals who may respond well to detailed policy discussions
        - Downtown condos may have security systems requiring advance coordination
        - Weekday evenings and weekend afternoons tend to have higher contact rates
        - Many residents are engaged in local issues, particularly downtown development and waterfront access
        """)
    
    with zip_tabs[1]:
        st.header("ZIP Code 33705")
        
        # Display demographic data
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Population", census_data["33705"]["total_population"])
            st.metric("Median Household Income", f"${census_data['33705']['median_household_income']:,}")
            st.metric("Bachelor's Degree or Higher", census_data["33705"]["bachelors_degree_or_higher"])
            st.metric("Employment Rate", census_data["33705"]["employment_rate"])
        
        with col2:
            st.metric("Total Housing Units", census_data["33705"]["total_housing_units"])
            st.metric("Without Health Insurance", census_data["33705"]["without_health_insurance"])
            st.metric("Total Households", census_data["33705"]["total_households"])
        
        # Add more detailed demographic information
        st.subheader("Key Demographics")
        st.markdown("""
        ZIP code 33705 covers south St. Petersburg. Key characteristics include:
        
        - More diverse population compared to 33701
        - Higher percentage of family households
        - Mix of older established neighborhoods and areas of new development
        - Higher percentage of long-term residents
        - More single-family homes compared to downtown
        """)
        
        st.subheader("Canvassing Tips for 33705")
        st.markdown("""
        - Focus on community-oriented messaging and local neighborhood issues
        - Weekend canvassing often yields better results as more families are home
        - Many residents have deep roots in the community and care about neighborhood stability
        - Local schools and community centers are important issues
        - Higher percentage of residents may need information about voter registration and polling locations
        """)
    
    with zip_tabs[2]:
        st.header("Demographic Comparison")
        
        # Create comparison charts
        comparison_data = {
            "ZIP Code": ["33701", "33705"],
            "Population": [census_data["33701"]["total_population"], census_data["33705"]["total_population"]],
            "Median Income": [census_data["33701"]["median_household_income"], census_data["33705"]["median_household_income"]],
            "Bachelor's Degree+": [float(census_data["33701"]["bachelors_degree_or_higher"].strip("%")), float(census_data["33705"]["bachelors_degree_or_higher"].strip("%"))],
            "Without Health Insurance": [float(census_data["33701"]["without_health_insurance"].strip("%")), float(census_data["33705"]["without_health_insurance"].strip("%"))]
        }
        
        # Population comparison
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.bar(comparison_data["ZIP Code"], comparison_data["Population"], color=['#3186cc', '#cc3131'])
        ax1.set_title("Population Comparison")
        ax1.set_ylabel("Population")
        for i, v in enumerate(comparison_data["Population"]):
            ax1.text(i, v + 500, f"{v:,}", ha='center')
        st.pyplot(fig1)
        
        # Income comparison
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(comparison_data["ZIP Code"], comparison_data["Median Income"], color=['#3186cc', '#cc3131'])
        ax2.set_title("Median Household Income Comparison")
        ax2.set_ylabel("Income ($)")
        for i, v in enumerate(comparison_data["Median Income"]):
            ax2.text(i, v + 2000, f"${v:,}", ha='center')
        st.pyplot(fig2)
        
        # Education comparison
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        ax3.bar(comparison_data["ZIP Code"], comparison_data["Bachelor's Degree+"], color=['#3186cc', '#cc3131'])
        ax3.set_title("Education Level Comparison (Bachelor's Degree or Higher)")
        ax3.set_ylabel("Percentage (%)")
        for i, v in enumerate(comparison_data["Bachelor's Degree+"]):
            ax3.text(i, v + 2, f"{v}%", ha='center')
        st.pyplot(fig3)
        
        st.subheader("Canvassing Strategy Implications")
        st.markdown("""
        Based on the demographic differences between these ZIP codes:
        
        1. **Messaging should be tailored** to each area's specific concerns and demographics
        2. **Canvassing times should vary** - evenings in 33701, weekends in 33705
        3. **Literature and materials** should reflect the different education levels and concerns
        4. **Volunteer training** should include awareness of demographic differences
        5. **Priority targeting** should consider both turnout history and demographic factors
        """)

elif st.session_state.current_tab == "Election History":
    st.title("Past Election Results")
    
    # Load election data
    election_df = load_election_results()
    
    if not election_df.empty:
        # Display overall statistics
        st.header("District 6 Voter Turnout")
        
        # Calculate district-wide statistics
        total_ballots = election_df['Ballots Cast'].sum()
        total_voters = election_df['Active Registered Voters'].sum()
        avg_turnout = election_df['Voter Turnout'].mean() * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Ballots Cast", f"{total_ballots:,}")
        with col2:
            st.metric("Registered Voters", f"{total_voters:,}")
        with col3:
            st.metric("Average Turnout", f"{avg_turnout:.1f}%")
        
        # Display precinct-level data
        st.subheader("Precinct-Level Turnout")
        
        # Create a bar chart of turnout by precinct
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by turnout for better visualization
        sorted_df = election_df.sort_values('Voter Turnout', ascending=False)
        
        # Create the bar chart
        bars = ax.bar(sorted_df['Precinct'].astype(str), sorted_df['Voter Turnout'] * 100)
        
        # Add labels and formatting
        ax.set_xlabel('Precinct')
        ax.set_ylabel('Voter Turnout (%)')
        ax.set_title('Voter Turnout by Precinct')
        ax.set_ylim(0, 100)
        
        # Add turnout percentage labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Display the chart
        st.pyplot(fig)
        
        # Display the raw data in a table
        st.subheader("Precinct Data Table")
        
        # Format the data for display
        display_df = election_df.copy()
        display_df['Voter Turnout'] = display_df['Voter Turnout'].apply(lambda x: f"{x*100:.1f}%")
        display_df = display_df.sort_values('Precinct')
        
        st.dataframe(display_df)
        
        # Strategic insights
        st.header("Strategic Insights")
        
        # High turnout precincts
        high_turnout = election_df.nlargest(3, 'Voter Turnout')
        high_turnout_precincts = high_turnout['Precinct'].astype(str).tolist()
        high_turnout_rates = [f"{x*100:.1f}%" for x in high_turnout['Voter Turnout'].tolist()]
        
        # Low turnout precincts
        low_turnout = election_df.nsmallest(3, 'Voter Turnout')
        low_turnout_precincts = low_turnout['Precinct'].astype(str).tolist()
        low_turnout_rates = [f"{x*100:.1f}%" for x in low_turnout['Voter Turnout'].tolist()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("High Turnout Precincts")
            for i in range(len(high_turnout_precincts)):
                st.markdown(f"**Precinct {high_turnout_precincts[i]}**: {high_turnout_rates[i]} turnout")
            
            st.markdown("""
            **Strategy for High Turnout Areas:**
            - Focus on persuasion rather than turnout
            - Emphasize policy positions and candidate qualifications
            - Allocate resources for targeted messaging
            - Consider these areas for volunteer recruitment
            """)
        
        with col2:
            st.subheader("Low Turnout Precincts")
            for i in range(len(low_turnout_precincts)):
                st.markdown(f"**Precinct {low_turnout_precincts[i]}**: {low_turnout_rates[i]} turnout")
            
            st.markdown("""
            **Strategy for Low Turnout Areas:**
            - Focus on voter education and turnout efforts
            - Provide information on voting locations and hours
            - Emphasize the importance of local elections
            - Consider offering transportation assistance
            - Conduct multiple canvassing passes
            """)
    else:
        st.error("Election data could not be loaded. Please check the DISTRICT6.xlsx file.")

elif st.session_state.current_tab == "Stats":
    st.title("Canvassing Statistics")
    
    # Get statistics
    stats = get_stats()
    
    # Display overall stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Doors Knocked", stats['total_interactions'])
    with col2:
        st.metric("Contacts Made", stats['total_addresses_contacted'])
    with col3:
        st.metric("Contact Rate", f"{stats['coverage_percentage']}%")
    
    # Response breakdown
    st.subheader("Response Breakdown")
    
    # Prepare data for chart
    response_labels = list(stats['response_breakdown'].keys())
    response_values = list(stats['response_breakdown'].values())
    
    if response_labels and response_values:
        # Create a pie chart
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#4CAF50', '#FF9800', '#2196F3', '#F44336', '#9E9E9E']
        ax.pie(response_values, labels=response_labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        st.pyplot(fig)
    else:
        st.info("No response data available yet")
    
    # Precinct coverage
    st.subheader("Precinct Coverage")
    
    if stats['precinct_coverage']:
        # Create a DataFrame for the table
        coverage_df = pd.DataFrame(stats['precinct_coverage'])
        coverage_df['Coverage'] = coverage_df.apply(
            lambda row: f"{(row['addresses_contacted'] / row['total_addresses'] * 100):.1f}%" 
            if row['total_addresses'] > 0 else "0.0%", 
            axis=1
        )
        
        # Display as a table
        st.dataframe(
            coverage_df[['id', 'name', 'addresses_contacted', 'total_addresses', 'Coverage']].rename(
                columns={'id': 'Precinct ID', 'name': 'Precinct Name', 'addresses_contacted': 'Doors Knocked', 'total_addresses': 'Total Addresses'}
            ),
            hide_index=True
        )
    else:
        st.info("No precinct coverage data available yet")
    
    # Interaction tags analysis
    st.subheader("Interaction Tags Analysis")
    
    # Sample tag data for demonstration
    tag_data = {
        "supportive": 15,
        "leaning": 8,
        "undecided": 12,
        "opposed": 5,
        "not-home": 18,
        "needs-info": 7,
        "volunteer-interest": 3,
        "yard-sign": 6,
        "donation": 2
    }
    
    # Create a horizontal bar chart for tags
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort tags by frequency
    sorted_tags = dict(sorted(tag_data.items(), key=lambda item: item[1], reverse=True))
    
    # Create the horizontal bar chart
    y_pos = range(len(sorted_tags))
    ax.barh(y_pos, sorted_tags.values(), align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_tags.keys())
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Frequency')
    ax.set_title('Interaction Tags Frequency')
    
    # Add value labels
    for i, v in enumerate(sorted_tags.values()):
        ax.text(v + 0.1, i, str(v), va='center')
    
    st.pyplot(fig)

elif st.session_state.current_tab == "Settings":
    st.title("Settings")
    
    # Volunteer information
    st.subheader("Volunteer Information")
    
    with st.form("volunteer_form"):
        name = st.text_input("Your Name", value=st.session_state.volunteer_name)
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        
        if st.form_submit_button("Save Settings"):
            st.session_state.volunteer_name = name
            st.success("Settings saved successfully!")
    
    # Interaction tags settings
    st.subheader("Interaction Tags")
    st.markdown("""
    Configure the quick tags available for categorizing voter interactions. These tags help with sorting and analyzing canvassing data.
    """)
    
    # Default tags
    default_tags = [
        "supportive", "leaning", "undecided", "opposed", "not-home",
        "needs-info", "volunteer-interest", "yard-sign", "donation"
    ]
    
    # Display current tags
    st.markdown("**Current Tags:**")
    tags_cols = st.columns(3)
    for i, tag in enumerate(default_tags):
        tags_cols[i % 3].markdown(f"- #{tag}")
    
    # Add custom tag
    st.markdown("**Add Custom Tag:**")
    with st.form("add_tag_form"):
        new_tag = st.text_input("New Tag Name (no spaces, use hyphens)")
        if st.form_submit_button("Add Tag"):
            if new_tag and new_tag not in default_tags:
                st.success(f"Tag #{new_tag} added successfully!")
            else:
                st.error("Please enter a valid tag name that doesn't already exist.")
    
    # Help and support
    st.subheader("Help & Support")
    st.markdown("""
    If you encounter any issues or have questions:
    - Contact your campaign coordinator
    - Email support at support@district6campaign.org
    - Call the campaign office at (727) 555-6789
    """)
    
    # About
    st.subheader("About")
    st.markdown("""
    **District 6 Canvassing App** v1.0
    
    This app helps campaign volunteers efficiently canvas District 6 by providing optimized routes, 
    tracking progress, and recording voter interactions.
    
    Thank you for volunteering! Your efforts make a huge difference in connecting with voters and 
    building support for our campaign.
    """)

# Helper function to add interaction notes
def add_interaction_notes(address_id):
    # Common tags for quick selection
    common_tags = [
        "supportive", "leaning", "undecided", "opposed", "not-home",
        "needs-info", "volunteer-interest", "yard-sign", "donation"
    ]
    
    # Create the form
    with st.form(key=f"note_form_{address_id}"):
        note_text = st.text_area("Notes", height=100, placeholder="Enter your interaction notes here...")
        
        # Tag selection
        st.write("Select tags:")
        tag_cols = st.columns(3)
        selected_tags = []
        
        for i, tag in enumerate(common_tags):
            if tag_cols[i % 3].checkbox(tag, key=f"tag_{address_id}_{tag}"):
                selected_tags.append(tag)
        
        # Custom tag
        custom_tag = st.text_input("Add custom tag (optional)")
        if custom_tag:
            selected_tags.append(custom_tag.lower().replace(" ", "-"))
        
        # Submit button
        if st.form_submit_button("Save Notes"):
            if note_text:
                save_interaction_note(address_id, st.session_state.volunteer_name, note_text, selected_tags)
                st.success("Notes saved successfully!")
                return True
            else:
                st.error("Please enter some notes before saving.")
                return False
    
    return False

# Footer
st.markdown("---")
st.markdown("© 2025 District 6 Campaign | Powered by Streamlit")
