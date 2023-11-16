import requests
import boto3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# API Key for api-football
api_key = os.environ.get('RAPIDAPI_KEY')

# Named profile in AWS credentials file
aws_profile = 'agamatec'

# API endpoint
api_url = 'https://api-football-v1.p.rapidapi.com/v3/fixtures'

# Premier League ID
league_id = 39

# S3 bucket name
bucket_name = 'fixtures-league-api-football'

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

# Function to fetch fixtures and store in S3 as JSON


def fetch_and_store_fixtures(start_season, end_season):
    for season in range(start_season, end_season + 1):
        # Define S3 file name
        s3_file_name = f'fixtures_{season}_{league_id}.json'

        # Check if the file already exists in S3
        if check_file_exists(bucket_name, s3_file_name):
            print(
                f'Data for season {season} already exists in S3 as {s3_file_name}. Skipping...')
        else:
            # Make API request
            response = requests.get(api_url, headers={'x-rapidapi-key': api_key},
                                    params={'league': league_id, 'season': season})

            if response.status_code == 200:
                # Store raw JSON response in S3
                s3.put_object(Body=response.text,
                              Bucket=bucket_name, Key=s3_file_name)

                print(
                    f'Data for season {season} uploaded to S3 as {s3_file_name}')
            else:
                print(
                    f'Error fetching data for season {season}: {response.status_code}')


if __name__ == "__main__":
    start_season = 2010
    end_season = 2023

    fetch_and_store_fixtures(start_season, end_season)
