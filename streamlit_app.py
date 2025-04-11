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

# Sample data - hardcoded to avoid file loading issues
def get_sample_precincts():
    return [
        {"id": "123", "name": "Precinct 123", "total_addresses": 1253},
        {"id": "125", "name": "Precinct 125", "total_addresses": 2577},
        {"id": "130", "name": "Precinct 130", "total_addresses": 1615},
        {"id": "131", "name": "Precinct 131", "total_addresses": 1842},
        {"id": "133", "name": "Precinct 133", "total_addresses": 2103}
    ]

def get_sample_addresses(precinct_id):
    addresses = []
    streets = ["MAIN ST", "OAK AVE", "PINE ST", "MAPLE DR", "CEDAR LN", "BEACH BLVD", "CENTRAL AVE"]
    property_types = ["Single Family", "Condominium", "Duplex", "Apartment", "Townhouse"]
    owner_occupied = ["Yes", "No"]
    
    # Generate sample addresses
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

# Sample census data
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

# Sample election data
def get_election_data():
    data = {
        'Precinct': [123, 125, 130, 131, 133],
        'Ballots Cast': [856, 1245, 932, 1021, 1156],
        'Active Registered Voters': [1253, 2577, 1615, 1842, 2103],
        'Voter Turnout': [0.68, 0.48, 0.58, 0.55, 0.55]
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
    precincts = get_sample_precincts()
    precinct_options = ["Select a precinct"] + [f"Precinct {p['id']}" for p in precincts]
    selected_option = st.selectbox("Select Precinct:", precinct_options)
    
    if selected_option != "Select a precinct":
        # Extract precinct ID from selection
        precinct_id = selected_option.split()[1]
        
        # Load addresses if precinct changed
        if st.session_state.selected_precinct != precinct_id:
            st.session_state.selected_precinct = precinct_id
            st.session_state.addresses = get_sample_addresses(precinct_id)
            st.rerun()
        
        # Display addresses
        if 'addresses' in st.session_state:
            st.subheader("Addresses to Visit")
            
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
            "ZIP Code": ["33701", "33705"],
            "Population": [census_data["33701"]["total_population"], census_data["33705"]["total_population"]],
            "Median Income": [census_data["33701"]["median_household_income"], census_data["33705"]["median_household_income"]],
            "Bachelor's Degree+": [float(census_data["33701"]["bachelors_degree_or_higher"].strip("%")), float(census_data["33705"]["bachelors_degree_or_higher"].strip("%"))],
            "Without Health Insurance": [float(census_data["33701"]["without_health_insurance"].strip("%")), float(census_data["33705"]["without_health_insurance"].strip("%"))]
        }
        
        # Population comparison
        st.subheader("Population Comparison")
        pop_df = pd.DataFrame({
            "ZIP Code": comparison_data["ZIP Code"],
            "Population": comparison_data["Population"]
        })
        st.bar_chart(pop_df.set_index("ZIP Code"))
        
        # Income comparison
        st.subheader("Median Household Income Comparison")
        income_df = pd.DataFrame({
            "ZIP Code": comparison_data["ZIP Code"],
            "Median Income": comparison_data["Median Income"]
        })
        st.bar_chart(income_df.set_index("ZIP Code"))
        
        # Education comparison
        st.subheader("Education Level Comparison (Bachelor's Degree or Higher)")
        edu_df = pd.DataFrame({
            "ZIP Code": comparison_data["ZIP Code"],
            "Bachelor's Degree+": comparison_data["Bachelor's Degree+"]
        })
        st.bar_chart(edu_df.set_index("ZIP Code"))
        
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
    election_df = get_election_data()
    
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
    
    # Create a bar chart of turnout by precinct using Streamlit's native charting
    sorted_df = election_df.sort_values('Voter Turnout', ascending=False).copy()
    sorted_df['Turnout Percentage'] = sorted_df['Voter Turnout'] * 100
    sorted_df['Precinct'] = sorted_df['Precinct'].astype(str)
    
    st.bar_chart(sorted_df.set_index('Precinct')['Turnout Percentage'])
    
    # Display the raw data in a table
    st.subheader("Precinct Data Table")
    
    # Format the data for display
    display_df = election_df.copy()
    display_df['Voter Turnout'] = display_df['Voter Turnout'].apply(lambda x: f"{x*100:.1f}%")
    
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
    
    # Create a horizontal bar chart for tags using Streamlit's native charting
    # Sort tags by frequency
    sorted_tags = dict(sorted(tag_data.items(), key=lambda item: item[1], reverse=True))
    tag_df = pd.DataFrame({
        'Tag': list(sorted_tags.keys()),
        'Count': list(sorted_tags.values())
    })
    
    st.bar_chart(tag_df.set_index('Tag'))

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

# Footer
st.markdown("---")
st.markdown("© 2025 District 6 Campaign | Powered by Streamlit")
