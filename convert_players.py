import pandas as pd
import json

def convert_players_to_json():
    # Read the CSV file
    df = pd.read_csv('playersAuction.csv')
    
    # Create a dictionary to store players by team
    players_by_team = {}
    
    # Map team abbreviations to full names
    team_mapping = {
        'RCB': 'Royal Challengers Bangalore',
        'MI': 'Mumbai Indians',
        'CSK': 'Chennai Super Kings',
        'KKR': 'Kolkata Knight Riders',
        'DC': 'Delhi Capitals',
        'PBKS': 'Punjab Kings',
        'RR': 'Rajasthan Royals',
        'SRH': 'Sunrisers Hyderabad',
        'LSG': 'Lucknow Super Giants',
        'GT': 'Gujarat Titans'
    }
    
    # Process each row
    for _, row in df.iterrows():
        player_name = row['Players']
        team_abbr = row['Team']
        player_type = row['Type']
        
        # Get full team name
        team_name = team_mapping.get(team_abbr)
        if not team_name:
            continue  # Skip if team not found
        
        # Initialize team in dictionary if not exists
        if team_name not in players_by_team:
            players_by_team[team_name] = {
                'batsmen': [],
                'bowlers': [],
                'all_rounders': []
            }
        
        # Add player to appropriate category
        if player_type == 'BAT':
            players_by_team[team_name]['batsmen'].append(player_name)
        elif player_type == 'BOWL':
            players_by_team[team_name]['bowlers'].append(player_name)
        elif player_type == 'AR':
            players_by_team[team_name]['all_rounders'].append(player_name)
    
    # Save to JSON file
    with open('team_players.json', 'w') as f:
        json.dump(players_by_team, f, indent=4)

if __name__ == "__main__":
    convert_players_to_json() 