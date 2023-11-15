# backend.py

from flask import Flask, jsonify
import pandas as pd
import os
import requests
import json

app = Flask(__name__)

# Function to fetch data from the API


def fetch_fixture_data():
    api_url = 'https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&season=2023'
    headers = {
        'x-rapidapi-key': 'd8aac0e59dmsh903ef91b3450d32p14e614jsn6d25591ff31d'}

    # Check if the data is already saved
    if os.path.exists('fixture_data.json'):
        with open('fixture_data.json', 'r') as file:
            # Use json.load to load the data as a dictionary
            data = json.load(file)
    else:
        # Fetch data from the API
        response = requests.get(api_url, headers=headers)
        data = response.json()

        # Save the data for future use
        with open('fixture_data.json', 'w') as file:
            json.dump(data, file)

    return data

# Helper function to parse a single match


def parse_single_match(match):
    return {
        'id': match['fixture']['id'],
        'date': pd.to_datetime(match['fixture']['date'], utc=True),
        'home_team': match['teams']['home']['name'],
        'away_team': match['teams']['away']['name'],
        'home_logo': match['teams']['home']['logo'],
        'away_logo': match['teams']['away']['logo']
    }

# Function to parse JSON and create Pandas DataFrame


def parse_json_to_dataframe(json_data):
    fixtures = json_data['response']

    # Use parse_single_match to parse each match
    fixture_list = [parse_single_match(fixture) for fixture in fixtures]

    # Create a DataFrame from the list
    df = pd.DataFrame(fixture_list)

    # Filter out fixtures that have already taken place
    now_utc = pd.to_datetime('now', utc=True)
    df = df[df['date'] > now_utc]

    return df


@app.route('/api/fixtures', methods=['GET'])
def get_fixtures():
    # Fetch fixture data from the API or local storage
    fixture_data = fetch_fixture_data()

    # Parse JSON to create Pandas DataFrame
    df = parse_json_to_dataframe(fixture_data)

    # Convert DataFrame to JSON
    fixtures_json = df.to_json(
        orient='records', date_format='iso', default_handler=str)

    # Parse the JSON string to remove escape characters
    unescaped_json = json.loads(fixtures_json)

    # Return the unescaped JSON response
    return jsonify({'fixtures': unescaped_json})

# Define an endpoint to get match details


@app.route('/api/match/<int:match_id>', methods=['GET'])
def get_match_details(match_id):
    fixtures = fetch_fixture_data()
    # Find the match with the given ID
    match = next(
        (fixture for fixture in fixtures['response'] if fixture['fixture']['id'] == match_id), None)

    if match:
        parsed_match = parse_single_match(match)
        return jsonify(parsed_match)
    else:
        return jsonify({'error': 'Match not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
