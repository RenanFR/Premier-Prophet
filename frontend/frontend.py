# frontend.py
import streamlit as st
import pandas as pd
import requests

# Function to fetch fixtures from the backend API
def get_fixtures():
    response = requests.get('http://localhost:5000/api/fixtures')  # Update the URL accordingly
    data = response.json()
    return data.get('fixtures', [])

# Get fixtures from the backend
fixtures = get_fixtures()

# Convert the received JSON to a DataFrame
df = pd.DataFrame(fixtures)

# Remove the default Streamlit index column
st.set_page_config(page_title="Premier Prophet", page_icon="⚽️")

# Update headers to title case
df.columns = df.columns.str.replace('_', ' ').str.title()

# Extract the hour portion and create a new column
df['Kickoff Hour'] = pd.to_datetime(df['Date']).dt.strftime('%H:%M')

# Sort fixtures by date in ascending order
df = df.sort_values(by='Date')

# Display fixtures grouped by date with home team as the first column
grouped_fixtures = df.groupby('Date', sort=False)  # Set sort to False for custom sorting
for date, group in grouped_fixtures:
    formatted_date = pd.to_datetime(date).strftime('%d/%m/%Y')
    st.subheader(formatted_date)
    
    # Sort the group by kickoff hour
    group = group.sort_values(by='Kickoff Hour')
    
    # Create an HTML table with home and away team logos and kickoff hour
    table_html = "<table><tr><th>Home Team</th><th>Away Team</th><th>Kickoff Hour</th></tr>"
    
    for index, row in group.iterrows():
        home_team_logo = f"<img src='{row['Home Logo']}' alt='{row['Home Team']}' width='32'>"
        away_team_logo = f"<img src='{row['Away Logo']}' alt='{row['Away Team']}' width='32'>"
        table_html += f"<tr><td>{home_team_logo} {row['Home Team']}</td><td>{away_team_logo} {row['Away Team']}</td><td>{row['Kickoff Hour']}</td></tr>"
    
    table_html += "</table>"
    
    # Display the HTML table
    st.markdown(table_html, unsafe_allow_html=True)