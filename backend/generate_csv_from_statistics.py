import boto3
import json
import pandas as pd

# AWS credentials
aws_profile = 'agamatec'

# S3 bucket names
statistics_bucket_name = 'fixtures-statistics-api-football'
data_frames_bucket_name = 'fixtures-stats-data-frames'

# Initialize S3 client using named profile
session = boto3.Session(profile_name=aws_profile)
s3 = session.client('s3')

# Function to check if file exists in S3


def check_file_exists(s3_bucket, s3_key):
    try:
        s3.head_object(Bucket=s3_bucket, Key=s3_key)
        return True
    except Exception as e:
        return False

# Function to convert statistics JSON to CSV


def convert_to_csv(fixture_key, statistics):
    home_team_stats = statistics['response'][0]['statistics']
    away_team_stats = statistics['response'][1]['statistics']

    # Extract goals from the filename
    match_goals = re.findall(r'\((.*?)\)', fixture_key)

    if match_goals:
        home_goals = int(match_goals[0])
        away_goals = int(match_goals[1])
    else:
        print(
            f'Error extracting goals from the filename for fixture {fixture_key}. Skipping...')
        return None

    data = {
        'Home_Team_Name': statistics['response'][0]['team']['name'],
        'Away_Team_Name': statistics['response'][1]['team']['name'],
        'Home_Goals': home_goals,
        'Away_Goals': away_goals
    }

    for stat in ['shots_on_goal', 'shots_off_goal', 'total_shots', 'blocked_shots', 'shots_insidebox',
                 'shots_outsidebox', 'fouls', 'corner_kicks', 'offsides', 'ball_possession',
                 'yellow_cards', 'red_cards', 'goalkeeper_saves', 'total_passes', 'passes_accurate', 'passes']:
        data.update({f'Home_{stat["type"].lower().replace(" ", "_")}': stat['value']
                    for stat in home_team_stats if stat['value'] is not None})
        data.update({f'Away_{stat["type"].lower().replace(" ", "_")}': stat['value']
                    for stat in away_team_stats if stat['value'] is not None})

    df = pd.DataFrame(data, index=[0])
    return df

# Function to fetch statistics and store as CSV


def fetch_and_store_csv(fixture_key):

    # Check if the CSV file already exists in S3
    csv_file_name = f'{fixture_key[:-5]}.csv'
    if check_file_exists(data_frames_bucket_name, csv_file_name):
        print(
            f'CSV file for fixture {fixture_key} already exists in S3. Skipping...')
        return

    # Read JSON content from S3
    fixture_content = s3.get_object(Bucket=statistics_bucket_name, Key=fixture_key)[
        'Body'].read().decode('utf-8')
    statistics = json.loads(fixture_content)

    # Check if statistics are not empty
    if not statistics or not statistics['response']:
        print(f'Skipping fixture {fixture_key} as statistics are empty.')
        return

    # Convert statistics to CSV
    df = convert_to_csv(fixture_key, statistics)

    if df is not None:
        # Store CSV in S3
        csv_content = df.to_csv(index=False)
        s3.put_object(Body=csv_content,
                      Bucket=data_frames_bucket_name, Key=csv_file_name)

        print(
            f'CSV for fixture {fixture_key} uploaded to S3 as {csv_file_name}')


if __name__ == "__main__":
    import re

    # Get the list of files in the statistics bucket
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=statistics_bucket_name)

    # Process each JSON file in the statistics bucket
    for page in pages:
        for statistics_file in page['Contents']:
            fixture_key = statistics_file['Key']
            season_year = int(fixture_key.split("/")[0])
            if season_year >= 2017:
                fetch_and_store_csv(fixture_key)
