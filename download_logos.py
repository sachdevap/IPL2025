import os
import requests
from data import IPL_TEAMS_INFO

def download_team_logos():
    # Create directory if it doesn't exist
    os.makedirs('static/team_logos', exist_ok=True)
    
    for team, info in IPL_TEAMS_INFO.items():
        logo_url = info['logo']
        # Create filename from team abbreviation
        filename = f"{info['abbreviation'].lower()}.png"
        filepath = os.path.join('static/team_logos', filename)
        
        try:
            # Download the logo
            response = requests.get(logo_url)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Save the logo
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded logo for {team}")
        except Exception as e:
            print(f"Error downloading logo for {team}: {e}")

if __name__ == "__main__":
    download_team_logos() 