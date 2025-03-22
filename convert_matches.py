import pandas as pd
import json
from datetime import datetime, timedelta

def convert_matches_to_json():
    # Read the CSV file
    df = pd.read_csv('matches.csv')
    
    # Convert to dictionary format with prediction cutoff
    matches = {}
    for _, row in df.iterrows():
        # Parse the date and time
        match_datetime = datetime.strptime(f"{row['Date']} {row['Time']}", "%Y-%m-%d %H:%M")
        
        # Calculate prediction cutoff (5 minutes before match)
        prediction_cutoff = match_datetime - timedelta(minutes=5)
        
        match_id = row['Match ID']
        matches[match_id] = {
            'team1': row['Team 1'],
            'team2': row['Team 2'],
            'date': match_datetime.strftime("%Y-%m-%d"),
            'time': match_datetime.strftime("%H:%M"),
            'prediction_cutoff': prediction_cutoff.strftime("%Y-%m-%d %H:%M"),
            'venue': row['Venue'],
            'is_playoff': bool(row.get('Is Playoff', False)),
            'result': None  # Will be populated when match is completed
        }
    
    # Save to JSON file
    with open('matches.json', 'w') as f:
        json.dump(matches, f, indent=4)

if __name__ == "__main__":
    convert_matches_to_json() 