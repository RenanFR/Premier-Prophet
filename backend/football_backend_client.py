import pandas as pd
import requests

def fetch_upcoming_fixtures():
    api_url = 'http://localhost:5000/api/fixtures'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        fixtures_data = response.json().get('fixtures', [])
        if fixtures_data:
            upcoming_fixtures = pd.DataFrame({
                'Home_Team_Name': [fixture['home_team'] for fixture in fixtures_data],
                'Away_Team_Name': [fixture['away_team'] for fixture in fixtures_data],
            })
            return upcoming_fixtures
        else:
            print('No upcoming fixtures found.')
    else:
        print(f'Failed to fetch upcoming fixtures. Status code: {response.status_code}')