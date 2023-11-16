from io import StringIO
import os
import pandas as pd

# AWS credentials
aws_profile = 'agamatec'

# S3 bucket name
data_frames_bucket_name = 'fixtures-stats-data-frames'

# Function to fetch and concatenate CSVs for a given year


def fetch_and_concat_csvs(year, processed_matches):
    consolidated_df = pd.DataFrame()

    # Get the list of files in the data_frames bucket for the specific year
    prefix = f'{year}/'
    csv_files = [obj['Key'] for obj in s3.list_objects_v2(
        Bucket=data_frames_bucket_name, Prefix=prefix)['Contents']]

    # Sort CSV files based on date
    csv_files.sort()

    for csv_file in csv_files:
        # Extract match date from the filename
        match_date = csv_file.split('_')[0]
        if match_date in processed_matches:
            print(f'Skipping match {match_date}, already processed.')
            continue

        # Read CSV content from S3
        csv_content = s3.get_object(Bucket=data_frames_bucket_name, Key=csv_file)[
            'Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))  # Use StringIO here

        # Add match date column
        season, match_date = match_date.split('/')
        df.insert(0, 'Season', season)
        df.insert(1, 'Match_Date', pd.to_datetime(
            match_date, format='%d%m%Y').strftime('%d%m%Y'))

        # Concatenate to the consolidated DataFrame
        consolidated_df = pd.concat([consolidated_df, df], ignore_index=True)

        print(f'Processed match {match_date}')

    return consolidated_df


if __name__ == "__main__":
    import boto3

    # Initialize S3 client using named profile
    session = boto3.Session(profile_name=aws_profile)
    s3 = session.client('s3')

    # Years to process
    start_year = 2015
    end_year = 2023

    # File paths
    intermediate_state_file = 'intermediate_state.csv'
    consolidated_csv_file = f'Premier_League_all_match_stats_{start_year}-{end_year}.csv'

    # Check if intermediate state file exists
    if os.path.exists(intermediate_state_file):
        processed_matches = pd.read_csv(intermediate_state_file)[
            'Match_Date'].tolist()
        print(f'Resuming from processed matches: {processed_matches}')
    else:
        processed_matches = []

    # Initialize consolidated_df outside the loop
    consolidated_df = pd.DataFrame()

    # Process each year
    for year in range(start_year, end_year + 1):
        consolidated_df = pd.concat([consolidated_df, fetch_and_concat_csvs(
            year, processed_matches)], ignore_index=True)

    # Save intermediate state
    processed_matches.extend(consolidated_df['Match_Date'].tolist())
    processed_matches = list(set(processed_matches))  # Remove duplicates
    pd.DataFrame({'Match_Date': processed_matches}).to_csv(
        intermediate_state_file, index=False)

    # Save the final consolidated CSV
    consolidated_df.to_csv(consolidated_csv_file, index=False)
    print(f'Consolidated CSV saved as {consolidated_csv_file}')
