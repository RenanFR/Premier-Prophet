import os
import json
import sys
import requests
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# AWS credentials
aws_profile = 'agamatec'

# S3 bucket names
fixtures_bucket_name = 'fixtures-league-api-football'
statistics_bucket_name = 'fixtures-statistics-api-football'

# Initialize S3 client using named profile
session = boto3.Session(profile_name=aws_profile)
s3 = session.client('s3')

# API endpoint for statistics
statistics_api_url = 'https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics'

# API key
api_key = os.environ.get('RAPIDAPI_KEY')

# Function to check if file exists in S3


def check_file_exists(s3_bucket, s3_key):
    try:
        s3.head_object(Bucket=s3_bucket, Key=s3_key)
        return True
    except Exception as e:
        return False

# Function to fetch statistics and store in S3


def fetch_and_store_statistics(fixture):
    fixture_id = fixture['fixture']['id']
    fixture_date = datetime.strptime(
        fixture['fixture']['date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d%m%Y')
    home_team_name = fixture['teams']['home']['name']
    away_team_name = fixture['teams']['away']['name']
    home_team_goals = fixture['goals']['home']
    away_team_goals = fixture['goals']['away']
    fixture_status = fixture['fixture']['status']['short']
    fixture_season = fixture['league']['season']

    s3_file_prefix = f'{fixture_season}/'

    # Define S3 file name
    s3_file_name = f'{s3_file_prefix}{fixture_date}_{home_team_name}({home_team_goals})-vs-{away_team_name}({away_team_goals})-{fixture_id}.json'

    # Check if the file already exists in S3
    if check_file_exists(statistics_bucket_name, s3_file_name):
        print(
            f'Statistics file for fixture {fixture_id} already exists in S3. Skipping...')
        return

    # Check if the fixture is finished
    if fixture_status not in ['FT', 'AET', 'PEN']:
        print(f'Skipping fixture {fixture_id} as it is not finished.')
        return

    # Make API request for statistics
    try:
        response = requests.get(statistics_api_url, headers={'x-rapidapi-key': api_key},
                                params={'fixture': fixture_id})
        response.raise_for_status()  # Check for request errors

        # Store raw JSON response in S3
        s3.put_object(Body=response.text,
                      Bucket=statistics_bucket_name, Key=s3_file_name)

        print(
            f'Statistics for fixture {fixture_id} uploaded to S3 as {s3_file_name}')

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 429:
            print('API rate limit exceeded. Waiting for 60 seconds...')
            sys.exit()
        else:
            print(f'Error fetching statistics for fixture {fixture_id}: {err}')


if __name__ == "__main__":

    # Get the list of files in the fixtures bucket
    fixtures_files = s3.list_objects_v2(
        Bucket=fixtures_bucket_name)['Contents']

    # Process each JSON file in the fixtures bucket
    for fixture_file in fixtures_files:

        # Check if the season is 2015 or later
        season_year = int(fixture_file['Key'].split("_")[1])
        if season_year >= 2015:

            fixture_key = fixture_file['Key']
            fixture_content = s3.get_object(Bucket=fixtures_bucket_name, Key=fixture_key)[
                'Body'].read().decode('utf-8')
            fixtures_data = json.loads(fixture_content)

            # Extract fixtures from the data
            fixtures = fixtures_data.get('response', [])

            # Process each fixture
            for fixture in fixtures:
                fetch_and_store_statistics(fixture)
