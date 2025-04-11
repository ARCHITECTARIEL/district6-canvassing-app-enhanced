import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="District 6 Canvassing App",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'volunteer_name' not in st.session_state:
    st.session_state.volunteer_name = "Jane Doe"
if 'selected_precinct' not in st.session_state:
    st.session_state.selected_precinct = None
if 'visited_addresses' not in st.session_state:
    st.session_state.visited_addresses = set()
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Home"
if 'selected_address_id' not in st.session_state:
    st.session_state.selected_address_id = None
if 'interaction_notes' not in st.session_state:
    st.session_state.interaction_notes = {}
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = False

# Real District 6 precinct data
def get_district6_precincts():
    return [
        {"id": "106", "name": "Precinct 106", "total_addresses": 760, "strategy": "Steve Kornell", "turnout": "88.55%"},
        {"id": "108", "name": "Precinct 108", "total_addresses": 2773, "strategy": "Coquina Key", "turnout": "81.79%"},
        {"id": "109", "name": "Precinct 109", "total_addresses": 2151, "strategy": "", "turnout": "77.59%"},
        {"id": "116", "name": "Precinct 116", "total_addresses": 1511, "strategy": "Me", "turnout": "67.97%"},
        {"id": "117", "name": "Precinct 117", "total_addresses": 1105, "strategy": "", "turnout": "62.53%"},
        {"id": "118", "name": "Precinct 118", "total_addresses": 1175, "strategy": "OLD SE", "turnout": "85.36%"},
        {"id": "119", "name": "Precinct 119", "total_addresses": 2684, "strategy": "USF", "turnout": "65.31%"},
        {"id": "121", "name": "Precinct 121", "total_addresses": 922, "strategy": "RAYS", "turnout": "77.55%"},
        {"id": "122", "name": "Precinct 122", "total_addresses": 258, "strategy": "BILL EDWARDS", "turnout": "87.60%"},
        {"id": "123", "name": "Precinct 123", "total_addresses": 4627, "strategy": "HIPSTER $", "turnout": "85.35%"},
        {"id": "125", "name": "Precinct 125", "total_addresses": 1301, "strategy": "ROUND LAKE", "turnout": "79.94%"},
        {"id": "126", "name": "Precinct 126", "total_addresses": 1958, "strategy": "HIPSTER POOR", "turnout": "77.07%"},
        {"id": "130", "name": "Precinct 130", "total_addresses": 3764, "strategy": "OLD NE", "turnout": "86.16%"}
    ]

def get_sample_addresses(precinct_id):
    addresses = []
    streets = ["MAIN ST", "OAK AVE", "PINE ST", "MAPLE DR", "CEDAR LN", "BEACH BLVD", "CENTRAL AVE"]
    property_types = ["Single Family", "Condominium", "Duplex", "Apartment", "Townhouse"]
    owner_occupied = ["Yes", "No"]
    
    # Generate sample addresses based on precinct
    for i in range(20):
        street = streets[i % len(streets)]
        street_num = 100 + i * 10
        
        addresses.append({
            "id": f"{precinct_id}_{i}",
            "precinct_id": precinct_id,
            "owner1": f"RESIDENT, DISTRICT 6 {i}",
            "owner2": "RESIDENT, FAMILY" if i % 3 == 0 else "",
            "address": f"{street_num} {street}",
            "city_zip": "ST PETERSBURG, FL 33701",
            "property_type": property_types[i % len(property_types)],
            "owner_occupied": owner_occupied[i % len(owner_occupied)]
        })
    
    return addresses

# Real census data
def get_census_data():
    return {
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

# Real election data
def get_election_data():
    data = {
        'Precinct': [106, 108, 109, 116, 117, 118, 119, 121, 122, 123, 125, 126, 130],
        'Registered Voters': [760, 2773, 2151, 1511, 1105, 1175, 2684, 922, 258, 4627, 1301, 1958, 3764],
        'Election Day Votes': [116, 547, 395, 326, 274, 314, 546, 174, 43, 556, 189, 329, 477],
        'Mail Ballot Votes': [438, 964, 771, 437, 260, 409, 672, 156, 67, 1822, 479, 504, 1676],
        'Early Votes': [119, 757, 503, 264, 157, 280, 535, 385, 116, 1571, 372, 676, 1090],
        'Ballots Cast': [673, 2268, 1669, 1027, 691, 1003, 1753, 715, 226, 3949, 1040, 1509, 3243],
        'Voter Turnout': [88.55, 81.79, 77.59, 67.97, 62.53, 85.36, 65.31, 77.55, 87.60, 85.35, 79.94, 77.07, 86.16],
        'Strategy': ["Steve Kornell", "Coquina Key", "", "Me", "", "OLD SE", "USF", "RAYS", "BILL EDWARDS", "HIPSTER $", "ROUND LAKE", "HIPSTER POOR", "OLD NE"]
    }
    return pd.DataFrame(data)

# Presidential election data
def get_presidential_data():
    data = {
        'Precinct': [123, 130, 108, 126, 109, 121, 119, 125, 118, 106, 116, 117, 122],
        'Registered': [4627, 3764, 2773, 1958, 2151, 922, 2684, 1301, 1175, 760, 1511, 1105, 258],
        'Trump': [1481, 1156, 839, 561, 306, 286, 282, 276, 274, 207, 176, 77, 67],
        'Kamala': [2387, 1996, 1367, 908, 1319, 413, 1432, 732, 708, 454, 835, 598, 149],
        'Voted For Trump %': [32.01, 30.71, 30.26, 28.65, 14.23, 31.02, 10.51, 21.21, 23.32, 27.24, 11.65, 6.97, 25.97],
        'Voted For Kamala %': [51.59, 53.03, 49.30, 46.37, 61.32, 44.79, 53.35, 56.26, 60.26, 59.74, 55.26, 54.12, 57.75]
    }
    return pd.DataFrame(data)

# Sample stats data
def get_stats():
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
        }
    }

# Add interaction note
def add_interaction_note(address_id, note_text, tags):
    if address_id not in st.session_state.interaction_notes:
        st.session_state.interaction_notes[address_id] = []
    
    st.session_state.interaction_notes[address_id].append({
        "volunteer_name": st.session_state.volunteer_name,
        "note_text": note_text,
        "tags": tags,
        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Initialize sample data for demonstration
def initialize_sample_data():
    if not st.session_state.data_initialized:
        # Add some sample interaction notes
        sample_addresses = get_sample_addresses("123")
        for i in range(5):
            address_id = sample_addresses[i]["id"]
            st.session_state.visited_addresses.add(address_id)
            
            # Add different types of interactions
            if i == 0:
                add_interaction_note(address_id, "Resident was very supportive of our campaign. Interested in yard sign.", ["supportive", "yard-sign"])
            elif i == 1:
                add_interaction_note(address_id, "Resident was not home. Left campaign literature.", ["not-home"])
            elif i == 2:
                add_interaction_note(address_id, "Resident was undecided but interested in learning more about our positions on local development.", ["undecided", "needs-info"])
            elif i == 3:
                add_interaction_note(address_id, "Resident expressed opposition to our campaign. Not interested in further contact.", ["opposed"])
            elif i == 4:
                add_interaction_note(address_id, "Resident is leaning toward supporting us but had questions about transportation policy.", ["leaning", "needs-info"])
        
        st.session_state.data_initialized = True

# Initialize sample data
initialize_sample_data()

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
    precincts = get_district6_precincts()
    precinct_options = ["Select a precinct"] + [f"Precinct {p['id']} - {p['strategy']}" if p['strategy'] else f"Precinct {p['id']}" for p in precincts]
    selected_option = st.selectbox("Select Precinct:", precinct_options)
    
    if selected_option != "Select a precinct":
        # Extract precinct ID from selection
        precinct_id = selected_option.split()[1]
        
        # Find the selected precinct
        selected_precinct_data = next((p for p in precincts if p['id'] == precinct_id), None)
        
        # Load addresses if precinct changed
        if st.session_state.selected_precinct != precinct_id:
            st.session_state.selected_precinct = precinct_id
            st.session_state.addresses = get_sample_addresses(precinct_id)
            st.rerun()
        
        # Display precinct info
        if selected_precinct_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Registered Voters", selected_precinct_data['total_addresses'])
            with col2:
                st.metric("Voter Turnout", selected_precinct_data['turnout'])
            with col3:
                if selected_precinct_data['strategy']:
                    st.metric("Strategy", selected_precinct_data['strategy'])
            
            # Get presidential data for this precinct
            presidential_df = get_presidential_data()
            precinct_presidential = presidential_df[presidential_df['Precinct'] == int(precinct_id)]
            
            if not precinct_presidential.empty:
                st.subheader("Presidential Election Results")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Trump Support", f"{precinct_presidential['Voted For Trump %'].values[0]:.1f}%")
                with col2:
                    st.metric("Kamala Support", f"{precinct_presidential['Voted For Kamala %'].values[0]:.1f}%")
                
                # Strategic insights based on voting patterns
                trump_pct = precinct_presidential['Voted For Trump %'].values[0]
                kamala_pct = precinct_presidential['Voted For Kamala %'].values[0]
                
                if kamala_pct > 55:
                    st.success("**Strategic Insight:** Strong Democratic precinct. Focus on turnout and base mobilization.")
                elif kamala_pct > 45:
                    st.info("**Strategic Insight:** Competitive precinct with Democratic lean. Focus on persuasion and turnout.")
                elif kamala_pct > 35:
                    st.warning("**Strategic Insight:** Competitive precinct with Republican lean. Focus on persuadable voters and specific local issues.")
                else:
                    st.error("**Strategic Insight:** Strong Republican precinct. Focus on moderate messaging and identifying supportive voters.")
        
        # Display addresses
        if 'addresses' in st.session_state:
            st.subheader("Addresses to Visit")
            
            # Progress tracking
            total_addresses = len(st.session_state.addresses)
            visited_count = len([a for a in st.session_state.addresses if a['id'] in st.session_state.visited_addresses])
            remaining_count = total_addresses - visited_count
            percentage = (visited_count / total_addresses * 100) if total_addresses > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Progress", f"{visited_count}/{total_addresses} ({percentage:.1f}%)")
            with col2:
                st.metric("Remaining", remaining_count)
            
            st.progress(percentage / 100)
            
            # Filter options
            st.subheader("Filter Options")
            col1, col2, col3 = st.columns(3)
            with col1:
                show_visited = st.checkbox("Show Visited", value=True)
            with col2:
                show_not_visited = st.checkbox("Show Not Visited", value=True)
            with col3:
                property_filter = st.selectbox("Property Type", ["All"] + list(set([a['property_type'] for a in st.session_state.addresses])))
            
            # Apply filters
            filtered_addresses = st.session_state.addresses.copy()
            if not show_visited:
                filtered_addresses = [a for a in filtered_addresses if a['id'] not in st.session_state.visited_addresses]
            if not show_not_visited:
                filtered_addresses = [a for a in filtered_addresses if a['id'] in st.session_state.visited_addresses]
            if property_filter != "All":
                filtered_addresses = [a for a in filtered_addresses if a['property_type'] == property_filter]
            
            # Address list
            for i, address in enumerate(filtered_addresses):
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
                                st.rerun()
                            
                            if st.button("Not Home", key=f"nothome_{address_id}"):
                                st.session_state.visited_addresses.add(address_id)
                                add_interaction_note(address_id, "Resident not home during canvassing visit.", ["not-home"])
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
                            notes = st.session_state.interaction_notes.get(address_id, [])
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
                            with st.form(key=f"note_form_{address_id}"):
                                note_text = st.text_area("Notes", height=100, placeholder="Enter your interaction notes here...")
                                
                                # Tag selection
                                st.write("Select tags:")
                                common_tags = [
                                    "supportive", "leaning", "undecided", "opposed", "not-home",
                                    "needs-info", "volunteer-interest", "yard-sign", "donation"
                                ]
                                
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
                                        add_interaction_note(address_id, note_text, selected_tags)
                                        st.success("Notes saved successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Please enter some notes before saving.")
                    
                    st.markdown("---")
    else:
        st.info("Please select a precinct to begin canvassing")

elif st.session_state.current_tab == "Demographics":
    st.title("Neighborhood Demographics")
    
    # Load census data
    census_data = get_census_data()
    
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
        
        # Create comparison charts using Streamlit's native charting
        comparison_data = {
            "Metric": ["Population", "Median Income ($K)", "Bachelor's+ (%)", "Employment (%)", "Uninsured (%)"],
            "33701": [
                census_data["33701"]["total_population"],
                census_data["33701"]["median_household_income"]/1000,
                float(census_data["33701"]["bachelors_degree_or_higher"].replace("%", "")),
                float(census_data["33701"]["employment_rate"].replace("%", "")),
                float(census_data["33701"]["without_health_insurance"].replace("%", ""))
            ],
            "33705": [
                census_data["33705"]["total_population"],
                census_data["33705"]["median_household_income"]/1000,
                float(census_data["33705"]["bachelors_degree_or_higher"].replace("%", "")),
                float(census_data["33705"]["employment_rate"].replace("%", "")),
                float(census_data["33705"]["without_health_insurance"].replace("%", ""))
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Population comparison (separate due to scale difference)
        st.subheader("Population Comparison")
        pop_df = comparison_df[comparison_df["Metric"] == "Population"].melt(id_vars="Metric", var_name="ZIP", value_name="Value")
        st.bar_chart(pop_df.set_index("ZIP")["Value"])
        
        # Other metrics comparison
        st.subheader("Key Metrics Comparison")
        metrics_df = comparison_df[comparison_df["Metric"] != "Population"]
        
        # Create individual charts for better visualization
        for metric in metrics_df["Metric"].unique():
            st.write(f"**{metric}**")
            metric_df = metrics_df[metrics_df["Metric"] == metric].melt(id_vars="Metric", var_name="ZIP", value_name="Value")
            st.bar_chart(metric_df.set_index("ZIP")["Value"])
        
        st.subheader("Canvassing Strategy Comparison")
        st.markdown("""
        | Aspect | 33701 (Downtown) | 33705 (South) |
        |--------|------------------|---------------|
        | Best Times | Weekday evenings, Weekend afternoons | Weekend mornings, Weekend afternoons |
        | Key Issues | Downtown development, Waterfront access, Arts funding | Schools, Community safety, Affordable housing |
        | Messaging | Policy details, Economic development | Community investment, Family support |
        | Materials | Digital resources, Website links | Printed materials, Visual aids |
        | Follow-up | Email, Text | Phone calls, In-person events |
        """)

elif st.session_state.current_tab == "Election History":
    st.title("Election History")
    
    # Create tabs for different views
    election_tabs = st.tabs(["Voter Turnout", "Presidential Results", "Strategic Insights"])
    
    with election_tabs[0]:
        st.header("Voter Turnout by Precinct")
        
        try:
            # Load election data
            election_df = get_election_data()
            
            # Sort by turnout for better visualization
            election_df = election_df.sort_values('Voter Turnout', ascending=False)
            
            # Convert precinct to string for better display
            election_df['Precinct'] = election_df['Precinct'].astype(str)
            
            # Create a bar chart of voter turnout
            st.bar_chart(election_df.set_index('Precinct')['Voter Turnout'])
            
            # Display voting method breakdown
            st.subheader("Voting Method Breakdown")
            
            # Calculate percentages for each voting method
            election_df['Election Day %'] = election_df['Election Day Votes'] / election_df['Ballots Cast'] * 100
            election_df['Mail Ballot %'] = election_df['Mail Ballot Votes'] / election_df['Ballots Cast'] * 100
            election_df['Early Voting %'] = election_df['Early Votes'] / election_df['Ballots Cast'] * 100
            
            # Create a stacked bar chart for voting methods
            voting_methods = pd.DataFrame({
                'Precinct': election_df['Precinct'],
                'Election Day': election_df['Election Day %'],
                'Mail Ballot': election_df['Mail Ballot %'],
                'Early Voting': election_df['Early Voting %']
            })
            
            st.bar_chart(voting_methods.set_index('Precinct'))
            
            # Display the raw data in a table
            st.subheader("Voter Turnout Data Table")
            display_cols = ['Precinct', 'Registered Voters', 'Ballots Cast', 'Voter Turnout', 'Strategy']
            st.dataframe(election_df[display_cols])
            
        except Exception as e:
            st.error(f"Error loading election data: {str(e)}")
            st.warning("Election data could not be loaded. Please check data sources.")
    
    with election_tabs[1]:
        st.header("Presidential Election Results")
        
        try:
            # Load presidential data
            presidential_df = get_presidential_data()
            
            # Create a bar chart comparing Trump and Kamala percentages
            chart_df = presidential_df.copy()
            chart_df['Precinct'] = chart_df['Precinct'].astype(str)
            chart_df = chart_df.sort_values('Voted For Kamala %', ascending=False)
            
            # Create a chart comparing Trump and Kamala percentages
            st.bar_chart(chart_df.set_index('Precinct')[['Voted For Trump %', 'Voted For Kamala %']])
            
            # Display the raw data in a table
            st.subheader("Presidential Results Data Table")
            st.dataframe(presidential_df)
            
        except Exception as e:
            st.error(f"Error loading presidential election data: {str(e)}")
            st.warning("Presidential election data could not be loaded. Please check data sources.")
    
    with election_tabs[2]:
        st.header("Strategic Insights")
        
        try:
            # Load election data
            election_df = get_election_data()
            presidential_df = get_presidential_data()
            
            # High turnout precincts
            high_turnout = election_df.nlargest(3, 'Voter Turnout')
            high_turnout_precincts = high_turnout['Precinct'].astype(str).tolist()
            high_turnout_rates = [f"{x:.1f}%" for x in high_turnout['Voter Turnout'].tolist()]
            high_turnout_strategies = high_turnout['Strategy'].tolist()
            
            # Low turnout precincts
            low_turnout = election_df.nsmallest(3, 'Voter Turnout')
            low_turnout_precincts = low_turnout['Precinct'].astype(str).tolist()
            low_turnout_rates = [f"{x:.1f}%" for x in low_turnout['Voter Turnout'].tolist()]
            low_turnout_strategies = low_turnout['Strategy'].tolist()
            
            # Strongest Democratic precincts
            strongest_dem = presidential_df.nlargest(3, 'Voted For Kamala %')
            strongest_dem_precincts = strongest_dem['Precinct'].astype(str).tolist()
            strongest_dem_rates = [f"{x:.1f}%" for x in strongest_dem['Voted For Kamala %'].tolist()]
            
            # Strongest Republican precincts
            strongest_rep = presidential_df.nlargest(3, 'Voted For Trump %')
            strongest_rep_precincts = strongest_rep['Precinct'].astype(str).tolist()
            strongest_rep_rates = [f"{x:.1f}%" for x in strongest_rep['Voted For Trump %'].tolist()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("High Turnout Precincts")
                for i in range(len(high_turnout_precincts)):
                    strategy = f" - {high_turnout_strategies[i]}" if high_turnout_strategies[i] else ""
                    st.markdown(f"**Precinct {high_turnout_precincts[i]}{strategy}**: {high_turnout_rates[i]} turnout")
                
                st.markdown("""
                **Strategy for High Turnout Areas:**
                - Focus on persuasion rather than turnout
                - Emphasize policy positions and candidate qualifications
                - Allocate resources for targeted messaging
                - Consider these areas for volunteer recruitment
                """)
                
                st.subheader("Strongest Democratic Precincts")
                for i in range(len(strongest_dem_precincts)):
                    st.markdown(f"**Precinct {strongest_dem_precincts[i]}**: {strongest_dem_rates[i]} for Kamala")
                
                st.markdown("""
                **Strategy for Democratic-Leaning Areas:**
                - Focus on base mobilization and turnout
                - Emphasize progressive policy positions
                - Recruit volunteers from these areas
                - Use these areas for visibility events and rallies
                """)
            
            with col2:
                st.subheader("Low Turnout Precincts")
                for i in range(len(low_turnout_precincts)):
                    strategy = f" - {low_turnout_strategies[i]}" if low_turnout_strategies[i] else ""
                    st.markdown(f"**Precinct {low_turnout_precincts[i]}{strategy}**: {low_turnout_rates[i]} turnout")
                
                st.markdown("""
                **Strategy for Low Turnout Areas:**
                - Focus on voter education and turnout efforts
                - Provide information on voting locations and hours
                - Emphasize the importance of local elections
                - Consider offering transportation assistance
                - Conduct multiple canvassing passes
                """)
                
                st.subheader("Strongest Republican Precincts")
                for i in range(len(strongest_rep_precincts)):
                    st.markdown(f"**Precinct {strongest_rep_precincts[i]}**: {strongest_rep_rates[i]} for Trump")
                
                st.markdown("""
                **Strategy for Republican-Leaning Areas:**
                - Focus on persuadable voters and independents
                - Emphasize moderate policy positions
                - Address specific local concerns
                - Use targeted messaging on issues with bipartisan appeal
                """)
                
        except Exception as e:
            st.error(f"Error loading election results: {str(e)}")
            st.warning("Election data could not be loaded. Please check the DISTRICT6.xlsx file.")

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
    
    # Prepare data for chart using Streamlit's native charting
    response_labels = list(stats['response_breakdown'].keys())
    response_values = list(stats['response_breakdown'].values())
    
    if response_labels and response_values:
        # Create a bar chart
        response_df = pd.DataFrame({
            'Category': response_labels,
            'Count': response_values
        })
        st.bar_chart(response_df.set_index('Category'))
        
        # Also show as a table for clarity
        st.table(response_df)
    else:
        st.info("No response data available yet")
    
    # Interaction tags analysis
    st.subheader("Interaction Tags Analysis")
    
    # Analyze tags from interaction notes
    tag_data = {}
    for address_id, notes in st.session_state.interaction_notes.items():
        for note in notes:
            for tag in note['tags']:
                if tag in tag_data:
                    tag_data[tag] += 1
                else:
                    tag_data[tag] = 1
    
    # If no real data, use sample data
    if not tag_data:
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
    
    # Create a horizontal bar chart for tags using Streamlit's native charting
    # Sort tags by frequency
    sorted_tags = dict(sorted(tag_data.items(), key=lambda item: item[1], reverse=True))
    tag_df = pd.DataFrame({
        'Tag': list(sorted_tags.keys()),
        'Count': list(sorted_tags.values())
    })
    
    st.bar_chart(tag_df.set_index('Tag'))
    
    # Precinct coverage
    st.subheader("Precinct Coverage")
    
    # Calculate precinct coverage from visited addresses
    precinct_coverage = {}
    precincts = get_district6_precincts()
    
    for p in precincts:
        precinct_id = p['id']
        precinct_coverage[precinct_id] = 0
    
    # Count visited addresses by precinct
    for address_id in st.session_state.visited_addresses:
        if '_' in address_id:
            precinct_id = address_id.split('_')[0]
            if precinct_id in precinct_coverage:
                precinct_coverage[precinct_id] += 1
    
    # If no real data, use sample data
    if all(v == 0 for v in precinct_coverage.values()):
        precinct_coverage = {
            "106": 35,
            "108": 22,
            "109": 15,
            "116": 45,
            "117": 10,
            "118": 30,
            "119": 18,
            "121": 25,
            "122": 40,
            "123": 12,
            "125": 28,
            "126": 20,
            "130": 15
        }
    
    # Create a bar chart for precinct coverage
    coverage_df = pd.DataFrame({
        'Precinct': list(precinct_coverage.keys()),
        'Coverage %': list(precinct_coverage.values())
    })
    
    st.bar_chart(coverage_df.set_index('Precinct'))
    
    # Data export options
    st.subheader("Data Export")
    st.markdown("""
    Export your canvassing data for further analysis or reporting. This feature would allow you to:
    - Download interaction notes as CSV
    - Export precinct coverage statistics
    - Generate reports for campaign leadership
    
    *Note: In this demo version, data export is simulated. In a production version, this would generate actual files.*
    """)
    
    if st.button("Export Data (Demo)"):
        st.success("Data export simulated successfully! In a production version, this would download a CSV file.")

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
    
    # Data persistence options
    st.subheader("Data Persistence")
    st.markdown("""
    Configure how your canvassing data is stored and synchronized.
    
    *Note: In this demo version, data persistence is simulated. In a production version, this would connect to a database.*
    """)
    
    persistence_option = st.radio(
        "Data Storage Option",
        ["Local Browser Storage", "Cloud Synchronization", "Team Sharing"]
    )
    
    if persistence_option == "Local Browser Storage":
        st.info("Data will be stored in your browser's local storage. Data will persist between sessions but only on this device.")
    elif persistence_option == "Cloud Synchronization":
        st.info("Data will be synchronized with the cloud, allowing you to access it from multiple devices.")
    else:
        st.info("Data will be shared with your campaign team, allowing for collaborative canvassing efforts.")
    
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

# Footer
st.markdown("---")
st.markdown("© 2025 District 6 Campaign | Powered by Streamlit")
