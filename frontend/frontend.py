import streamlit as st
import pandas as pd
import requests

# Set page configuration (call this only once and as the first Streamlit command)
st.set_page_config(page_title="Premier Prophet", page_icon="⚽️")

# Function to fetch fixtures from the backend API

@st.cache_data
def get_fixtures():
    response = requests.get('http://localhost:5000/api/fixtures')
    data = response.json()
    return data.get('fixtures', [])

# Function to fetch match details from the backend API

@st.cache_data
def get_match_details(match_id):
    response = requests.get(f'http://localhost:5000/api/match/{match_id}')
    data = response.json()
    return data


# Get fixtures from the backend
fixtures = get_fixtures()

# Convert the received JSON to a DataFrame
df = pd.DataFrame(fixtures)

# Extract the hour portion and create a new column
df['kickoff_hour'] = pd.to_datetime(df['date']).dt.strftime('%H:%M')

df['kick_off_date'] = pd.to_datetime(df['date']).dt.date

# Sort fixtures by date in ascending order
df = df.sort_values(by='kick_off_date')

# Check if a match is selected
match_id = st.experimental_get_query_params().get('match_id', [None])[0]

# Display fixtures grouped by date with home team as the first column
if match_id is None:
    grouped_fixtures = df.groupby('kick_off_date', sort=False)
    for date, group in grouped_fixtures:
        formatted_date = pd.to_datetime(date).strftime('%d/%m/%Y')
        st.subheader(formatted_date)

        # Sort the group by kickoff hour
        group = group.sort_values(by='kickoff_hour')

        # Create an HTML table with home and away team logos and kickoff hour
        table_html = "<table><tr><th>Home Team</th><th>Away Team</th><th>Kickoff Hour</th></tr>"

        for index, row in group.iterrows():
            home_team_logo = f"<a href='http://localhost:8501/?match_id={row['id']}'><img src='{row['home_logo']}' alt='{row['home_team']}' width='32'></a>"
            away_team_logo = f"<a href='http://localhost:8501/?match_id={row['id']}'><img src='{row['away_logo']}' alt='{row['away_team']}' width='32'></a>"
            table_html += f"<tr><td>{home_team_logo} {row['home_team']}</td><td>{away_team_logo} {row['away_team']}</td><td>{row['kickoff_hour']}</td></tr>"

        table_html += "</table>"

        # Display the HTML table
        st.markdown(table_html, unsafe_allow_html=True)

# If a match is selected, show match details
if match_id is not None:
    # Get match details from the backend
    match_details = get_match_details(match_id)

    # Remove the fixture table if a match is selected
    st.empty()

    # Display match details in the header
    st.title(
        f"Match Details: {match_details['home_team']} vs {match_details['away_team']}")
    st.subheader(
        f"Kickoff Hour: {pd.to_datetime(match_details['date']).strftime('%H:%M')}")

    # Display predicted stats table (you'll need to fetch these from the model endpoint)
    st.subheader("Predicted Stats")
    st.table(pd.DataFrame(
        {"Stat": ["Corners", "Fouls"], "Prediction": ["5", "10"]}))
