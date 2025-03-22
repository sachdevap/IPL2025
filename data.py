import pandas as pd
from datetime import datetime, timedelta
import json
import os
from pytz import timezone

# IPL Teams with their logos and colors
IPL_TEAMS_INFO = {
    "Chennai Super Kings": {
        "logo": "static/team_logos/csk.png",
        "primary_color": "#FFFF3C",
        "secondary_color": "#0081E9",
        "abbreviation": "CSK"
    },
    "Delhi Capitals": {
        "logo": "static/team_logos/dc.png",
        "primary_color": "#0078BC",
        "secondary_color": "#EF1B23",
        "abbreviation": "DC"
    },
    "Gujarat Titans": {
        "logo": "static/team_logos/gt.png",
        "primary_color": "#1B2133",
        "secondary_color": "#B9B9B9",
        "abbreviation": "GT"
    },
    "Kolkata Knight Riders": {
        "logo": "static/team_logos/kkr.png",
        "primary_color": "#3A225D",
        "secondary_color": "#F2C000",
        "abbreviation": "KKR"
    },
    "Lucknow Super Giants": {
        "logo": "static/team_logos/lsg.png",
        "primary_color": "#A72056",
        "secondary_color": "#FFDB3B",
        "abbreviation": "LSG"
    },
    "Mumbai Indians": {
        "logo": "static/team_logos/mi.png",
        "primary_color": "#004BA0",
        "secondary_color": "#D1AB3E",
        "abbreviation": "MI"
    },
    "Punjab Kings": {
        "logo": "static/team_logos/pbks.png",
        "primary_color": "#D11D1B",
        "secondary_color": "#FDB913",
        "abbreviation": "PBKS"
    },
    "Rajasthan Royals": {
        "logo": "static/team_logos/rr.png",
        "primary_color": "#EA1A85",
        "secondary_color": "#254AA5",
        "abbreviation": "RR"
    },
    "Royal Challengers Bangalore": {
        "logo": "static/team_logos/rcb.png",
        "primary_color": "#2B2A29",
        "secondary_color": "#EC1C24",
        "abbreviation": "RCB"
    },
    "Sunrisers Hyderabad": {
        "logo": "static/team_logos/srh.png",
        "primary_color": "#F26522",
        "secondary_color": "#000000",
        "abbreviation": "SRH"
    }
}

# List of IPL Teams
IPL_TEAMS = list(IPL_TEAMS_INFO.keys())

# Add IST timezone
IST = timezone('Asia/Kolkata')

class GameData:
    def __init__(self):
        """Initialize game data"""
        self.data_file = "data/game_data.json"  # Contains user data, predictions, points
        self.matches_file = "data/matches.json"  # Contains match schedules and results
        self.team_players_file = "data/team_players.json"  # Contains team rosters
        self.load_data()

    def load_data(self):
        """Load game data from files"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Load game data (user info, predictions, points)
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.players = data.get('players', {})
                self.predictions = data.get('predictions', {})
        else:
            self.players = {}
            self.predictions = {}
        
        # Load matches data
        if os.path.exists(self.matches_file):
            with open(self.matches_file, 'r') as f:
                self.matches = json.load(f)
        else:
            self.matches = {}
            
        # Load team players data
        if os.path.exists(self.team_players_file):
            with open(self.team_players_file, 'r') as f:
                self.team_players = json.load(f)
        else:
            self.team_players = {}

    def save_data(self):
        """Save data to JSON files"""
        # Save game data (user info, predictions, points)
        game_data = {
            'players': self.players,
            'predictions': self.predictions
        }
        with open(self.data_file, 'w') as f:
            json.dump(game_data, f, indent=4)
        
        # Save matches data
        with open(self.matches_file, 'w') as f:
            json.dump(self.matches, f, indent=4)

    def add_match(self, match_id: str, team1: str, team2: str, date: str, is_playoff: bool = False) -> bool:
        """Add a new match"""
        if match_id in self.matches:
            return False
        
        self.matches[match_id] = {
            'team1': team1,
            'team2': team2,
            'date': date,
            'is_playoff': is_playoff,
            'status': 'scheduled',  # scheduled, in_progress, completed
            'result': {}
        }
        self.save_data()
        return True

    def get_match(self, match_id: str) -> dict:
        """Get match details"""
        return self.matches.get(match_id, {})

    def get_matches_list(self) -> pd.DataFrame:
        """Get list of all matches as a DataFrame"""
        if not self.matches:
            return pd.DataFrame(columns=['Match ID', 'Team 1', 'Team 2', 'Date', 'Time', 'Venue', 'Is Playoff', 'Status'])
        
        data = []
        for match_id, match_data in self.matches.items():
            data.append({
                'Match ID': match_id,
                'Team 1': match_data['team1'],
                'Team 2': match_data['team2'],
                'Date': match_data['date'],
                'Time': f"{match_data.get('time', '')} IST",
                'Venue': match_data.get('venue', ''),
                'Is Playoff': 'Yes' if match_data.get('is_playoff', False) else 'No',
                'Status': 'Completed' if match_data.get('result') else 'Scheduled'
            })
        
        df = pd.DataFrame(data)
        return df.sort_values(['Date', 'Time']).reset_index(drop=True)

    def add_player(self, username: str, team: str) -> bool:
        """Add a new player with their chosen team"""
        if username in self.players:
            return False
        
        self.players[username] = {
            'team': team,
            'points': 0,
            'perfect_predictions': 0,
            'loyalty_bonus_count': 0,
            'has_switched_team': False,  # Track if player has used their team switch
            'original_team': team  # Track original team for history
        }
        self.save_data()
        return True

    def get_team_supporters(self, team: str) -> list:
        """Get list of users supporting a particular team"""
        return [username for username, data in self.players.items() if data['team'] == team]

    def get_team_stats(self) -> pd.DataFrame:
        """Get statistics about team selection"""
        if not self.players:
            return pd.DataFrame(columns=['Team', 'Supporters Count', 'Total Points'])
        
        team_stats = {}
        for team in IPL_TEAMS:
            supporters = self.get_team_supporters(team)
            team_stats[team] = {
                'Supporters Count': len(supporters),
                'Total Points': sum(self.players[user]['points'] for user in supporters)
            }
        
        df = pd.DataFrame.from_dict(team_stats, orient='index').reset_index()
        df.columns = ['Team', 'Supporters Count', 'Total Points']
        return df.sort_values('Supporters Count', ascending=False).reset_index(drop=True)

    def add_prediction(self, match_id, username, prediction):
        """Add a prediction for a match"""
        if match_id not in self.matches:
            return False
        
        match = self.matches[match_id]
        
        # Check if match has a result
        if match.get('result'):
            return False
        
        # Check if prediction is within cutoff time
        current_time = datetime.now(IST)
        cutoff_time = IST.localize(datetime.strptime(match['prediction_cutoff'], "%Y-%m-%d %H:%M"))
        if current_time >= cutoff_time:
            return False
        
        # Initialize predictions for match if not exists
        if match_id not in self.predictions:
            self.predictions[match_id] = {}
        
        # Add prediction
        self.predictions[match_id][username] = prediction
        self.save_data()
        return True

    def get_user_prediction(self, match_id: str, username: str) -> dict:
        """Get user's prediction for a match"""
        return self.predictions.get(match_id, {}).get(username, {})

    def calculate_points(self, match_id: str, result: dict):
        """Calculate points for all predictions of a match"""
        match = self.get_match(match_id)
        if not match or match['status'] == 'completed':
            return False
        
        is_playoff = match['is_playoff']
        multiplier = 2 if is_playoff else 1

        for username, prediction in self.predictions.get(match_id, {}).items():
            points = 0
            perfect_prediction = True
            
            # Match winner points
            if prediction['winner'] == result['winner']:
                points += 10 * multiplier
                # Check for loyalty bonus
                if self.players[username]['team'] == result['winner']:
                    points += 5 * multiplier
                    self.players[username]['loyalty_bonus_count'] += 1
            else:
                perfect_prediction = False
            
            # Top scorer points
            if prediction['top_scorer'] == result['top_scorer']:
                points += 5 * multiplier
            else:
                perfect_prediction = False
            
            # Top wicket taker points
            if prediction['top_wicket_taker'] == result['top_wicket_taker']:
                points += 5 * multiplier
            else:
                perfect_prediction = False
            
            # Perfect prediction bonus
            if perfect_prediction:
                points += 10 * multiplier
                self.players[username]['perfect_predictions'] += 1
            
            self.players[username]['points'] += points
        
        # Update match status and result
        self.matches[match_id]['status'] = 'completed'
        self.matches[match_id]['result'] = result
        self.save_data()
        return True

    def get_leaderboard(self) -> pd.DataFrame:
        """Get current leaderboard as a pandas DataFrame"""
        if not self.players:  # If no players, return empty DataFrame with correct columns
            return pd.DataFrame(columns=['Username', 'Team', 'Points', 'Perfect Predictions', 'Loyalty Bonuses'])
        
        data = []
        for username, player_data in self.players.items():
            data.append({
                'Username': username,
                'Team': player_data['team'],
                'Points': player_data.get('points', 0),  # Use get() with default value
                'Perfect Predictions': player_data.get('perfect_predictions', 0),
                'Loyalty Bonuses': player_data.get('loyalty_bonus_count', 0)
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Points', ascending=False).reset_index(drop=True)

    def get_available_teams(self) -> list:
        """Get list of teams that haven't been chosen yet"""
        chosen_teams = [player_data['team'] for player_data in self.players.values()]
        return [team for team in IPL_TEAMS if team not in chosen_teams]

    def switch_team(self, username: str, new_team: str) -> bool:
        """Switch a player's team (allowed only once)"""
        if username not in self.players:
            return False, "Player not found"
        
        player = self.players[username]
        if player['has_switched_team']:
            return False, "You have already used your one-time team switch"
        
        if player['team'] == new_team:
            return False, "You are already supporting this team"
        
        # Update player's team
        player['has_switched_team'] = True
        player['team'] = new_team
        self.save_data()
        return True, "Team switched successfully"

    def get_player_info(self, username: str) -> dict:
        """Get detailed player information"""
        player = self.players.get(username, {})
        if player:
            return {
                'current_team': player['team'],
                'original_team': player['original_team'],
                'has_switched_team': player['has_switched_team'],
                'points': player['points'],
                'perfect_predictions': player['perfect_predictions'],
                'loyalty_bonus_count': player['loyalty_bonus_count']
            }
        return {}

    def get_team_players(self, team_name):
        """Get players list for a team"""
        if team_name in self.team_players:
            return self.team_players[team_name]
        return {'batsmen': [], 'bowlers': [], 'all_rounders': []} 