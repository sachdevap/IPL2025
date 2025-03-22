import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from data import GameData, IPL_TEAMS, IPL_TEAMS_INFO
from auth import init_auth, login_required, show_login_page
import base64
import os
from pytz import timezone
import json

# Add IST timezone
IST = timezone('Asia/Kolkata')

def get_image_base64(image_path):
    """Convert local image to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Initialize session state
if 'game_data' not in st.session_state:
    st.session_state.game_data = GameData()

# Initialize authentication
init_auth()

# Page config
st.set_page_config(
    page_title="IPL 2025 Prediction League",
    page_icon="🏏",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 1200px;
    }
    .team-logo {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin: 10px;
    }
    .team-logo-small {
        width: 30px;
        height: 30px;
        object-fit: contain;
        vertical-align: middle;
        margin-right: 5px;
    }
    .team-card {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        transition: transform 0.2s;
        background-color: black;
        color: white;
    }
    .team-card:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }
    .team-card h4 {
        color: white;
        margin: 10px 0;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .match-card {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        background-color: black;
        color: white;
    }
    .match-card img {
        max-width: 80px;
        margin: 10px;
    }
    .vs-text {
        font-size: 24px;
        margin: 0 20px;
        font-weight: bold;
        color: white;
    }
    .dialog-backdrop {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    }
    .dialog-content {
        background: white;
        padding: 20px;
        border-radius: 10px;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1001;
    }
    </style>
    """, unsafe_allow_html=True)

def display_team_logo(team_name, size="small"):
    """Helper function to display team logo with name"""
    logo_path = IPL_TEAMS_INFO[team_name]["logo"]
    css_class = "team-logo" if size == "large" else "team-logo-small"
    try:
        logo_base64 = get_image_base64(logo_path)
        return f'<img src="data:image/png;base64,{logo_base64}" class="{css_class}" /> {team_name}'
    except:
        return team_name  # Fallback to just the team name if image loading fails

# Title and description
st.title("🏏 IPL 2025 Prediction League")

# Authentication status
if 'token' in st.session_state:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        del st.session_state.token
        del st.session_state.username
        st.rerun()

# Navigation
available_pages = ["Home", "Leaderboard"]
if 'token' in st.session_state:
    available_pages.extend(["Join Game", "Make Prediction"])
    if st.session_state.auth_manager.get_user(st.session_state.username)["role"] == "admin":
        available_pages.extend(["Manage Matches", "Enter Results"])

page = st.sidebar.radio("Navigation", available_pages)

if page == "Home":
    # Display team logos in a grid
    st.markdown("### IPL Teams")
    cols = st.columns(5)
    for idx, team in enumerate(IPL_TEAMS):
        with cols[idx % 5]:
            logo_base64 = get_image_base64(IPL_TEAMS_INFO[team]['logo'])
            st.markdown(
                f"""
                <div class="team-card" style="border-color: {IPL_TEAMS_INFO[team]['primary_color']}">
                    <img src="data:image/png;base64,{logo_base64}" class="team-logo" />
                    <h4>{team}</h4>
                    <p style="color: {IPL_TEAMS_INFO[team]['primary_color']}">{IPL_TEAMS_INFO[team]['abbreviation']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    st.markdown("""
    Welcome to the IPL 2025 WhatsApp Paper Game! Compete with friends to predict match outcomes
    and become the IPL Prediction Champion.
    """)
    
    st.header("How to Play")
    st.markdown("""
    ### Game Rules:
    1. **Team Selection**: Pick one IPL team at the start (first-come, first-served)
    2. **Predictions**: Before each match, predict:
        - Match winner
        - Highest run-scorer
        - Highest wicket-taker
    3. **Scoring System**:
        - Correct match winner: 10 points
        - Correct highest run-scorer: 5 points
        - Correct highest wicket-taker: 5 points
        - Team loyalty bonus: 5 extra points
        - Perfect prediction bonus: 10 points
    4. **Special Events**:
        - Playoff matches: All points are doubled
        - Trade window: One team switch allowed mid-season
    """)

    # Display current stats
    st.subheader("Current Game Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Players", len(st.session_state.game_data.players))
        total_predictions = sum(len(preds) for preds in st.session_state.game_data.predictions.values())
        st.metric("Total Predictions", total_predictions)
    
    with col2:
        st.metric("Matches Scheduled", len(st.session_state.game_data.matches))
        completed_matches = sum(1 for match in st.session_state.game_data.matches.values() if match.get('result'))
        st.metric("Matches Completed", completed_matches)

    # Show login form if not logged in
    if 'token' not in st.session_state:
        st.markdown("---")
        st.subheader("Login")
        show_login_page()

elif page == "Manage Matches":
    @login_required(role="admin")
    def show_manage_matches():
        st.header("Manage Matches")
        
        # Add new match
        st.subheader("Add New Match")
        with st.form("add_match"):
            col1, col2, col3 = st.columns(3)
            with col1:
                match_id = st.text_input("Match ID (e.g., M1)")
                team1 = st.selectbox("Team 1", IPL_TEAMS)
                venue = st.text_input("Venue")
            with col2:
                date = st.date_input("Match Date")
                team2 = st.selectbox("Team 2", [team for team in IPL_TEAMS if team != team1])
                time = st.time_input("Match Time (IST)", value=datetime.strptime("14:00", "%H:%M"))
            with col3:
                is_playoff = st.checkbox("Playoff Match")
            
            submitted = st.form_submit_button("Add Match")
            if submitted and all([match_id, team1, team2, date, time, venue]):
                # Create match datetime in IST
                naive_datetime = datetime.combine(date, time)
                match_datetime = IST.localize(naive_datetime)
                # Calculate prediction cutoff (5 minutes before match)
                prediction_cutoff = match_datetime - timedelta(minutes=5)
                
                # Create match data
                match_data = {
                    'team1': team1,
                    'team2': team2,
                    'date': match_datetime.strftime("%Y-%m-%d"),
                    'time': match_datetime.strftime("%H:%M"),
                    'prediction_cutoff': prediction_cutoff.strftime("%Y-%m-%d %H:%M"),
                    'venue': venue,
                    'is_playoff': is_playoff,
                    'result': None
                }
                
                # Add match to game data
                if match_id not in st.session_state.game_data.matches:
                    st.session_state.game_data.matches[match_id] = match_data
                    st.session_state.game_data.save_data()
                    st.success("Match added successfully!")
                else:
                    st.error("Match ID already exists!")
        
        # Show matches list and edit functionality
        st.subheader("All Matches")
        matches_df = pd.DataFrame.from_dict(st.session_state.game_data.matches, orient='index')
        if not matches_df.empty:
            matches_df = matches_df.reset_index()
            matches_df.columns = ['Match ID'] + list(matches_df.columns[1:])
            matches_df['Status'] = matches_df['result'].apply(lambda x: 'Completed' if x else 'Scheduled')
            
            # Display matches in a dataframe
            st.dataframe(matches_df[['Match ID', 'team1', 'team2', 'date', 'time', 'venue', 'is_playoff', 'Status']], use_container_width=True)
            
            # Edit match section
            st.subheader("Edit Match")
            edit_match_id = st.selectbox("Select Match to Edit", matches_df['Match ID'].tolist())
            
            if edit_match_id:
                match_data = st.session_state.game_data.matches[edit_match_id]
                with st.form("edit_match"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        edit_team1 = st.selectbox("Team 1", IPL_TEAMS, index=IPL_TEAMS.index(match_data['team1']))
                        edit_venue = st.text_input("Venue", value=match_data['venue'])
                    
                    with col2:
                        edit_date = st.date_input("Match Date", value=datetime.strptime(match_data['date'], "%Y-%m-%d"))
                        edit_team2 = st.selectbox("Team 2", [team for team in IPL_TEAMS if team != edit_team1], 
                                                index=[i for i, team in enumerate([t for t in IPL_TEAMS if t != edit_team1]) 
                                                      if team == match_data['team2']][0])
                        edit_time = st.time_input("Match Time (IST)", 
                                                value=datetime.strptime(match_data['time'], "%H:%M"))
                    
                    with col3:
                        edit_is_playoff = st.checkbox("Playoff Match", value=match_data['is_playoff'])
                        
                        # Add result input if match is completed
                        if match_data.get('result'):
                            st.write("Match Result:")
                            winner = st.selectbox("Winner", [edit_team1, edit_team2], 
                                                index=[0 if match_data['result']['winner'] == edit_team1 else 1])
                            top_scorer = st.text_input("Top Scorer", value=match_data['result'].get('top_scorer', ''))
                            top_wicket_taker = st.text_input("Top Wicket Taker", 
                                                           value=match_data['result'].get('top_wicket_taker', ''))
                    
                    update_submitted = st.form_submit_button("Update Match")
                    if update_submitted:
                        # Create match datetime in IST
                        naive_datetime = datetime.combine(edit_date, edit_time)
                        match_datetime = IST.localize(naive_datetime)
                        # Calculate prediction cutoff (5 minutes before match)
                        prediction_cutoff = match_datetime - timedelta(minutes=5)
                        
                        # Update match data
                        updated_match_data = {
                            'team1': edit_team1,
                            'team2': edit_team2,
                            'date': match_datetime.strftime("%Y-%m-%d"),
                            'time': match_datetime.strftime("%H:%M"),
                            'prediction_cutoff': prediction_cutoff.strftime("%Y-%m-%d %H:%M"),
                            'venue': edit_venue,
                            'is_playoff': edit_is_playoff,
                            'result': match_data.get('result')
                        }
                        
                        # Update result if it exists
                        if match_data.get('result'):
                            updated_match_data['result'] = {
                                'winner': winner,
                                'top_scorer': top_scorer,
                                'top_wicket_taker': top_wicket_taker
                            }
                        
                        # Update match in game data
                        st.session_state.game_data.matches[edit_match_id] = updated_match_data
                        st.session_state.game_data.save_data()
                        st.success("Match updated successfully!")
                        st.rerun()
        else:
            st.info("No matches added yet.")

    show_manage_matches()

elif page == "Make Prediction":
    @login_required()
    def show_make_prediction():
        st.header("Make Your Prediction")
        
        current_user = st.session_state.username
        if current_user not in st.session_state.game_data.players:
            st.warning("Please join the game first!")
            return
        
        # Show available matches
        matches_df = st.session_state.game_data.get_matches_list()
        scheduled_matches = matches_df[matches_df['Status'] == 'Scheduled']
        
        if scheduled_matches.empty:
            st.info("No scheduled matches available for prediction.")
            return
        
        st.subheader("Available Matches")
        st.dataframe(scheduled_matches, use_container_width=True)
        
        # Show match details with team logos
        match_id = st.selectbox("Select Match", scheduled_matches['Match ID'].tolist())
        match = st.session_state.game_data.get_match(match_id)
        if match:
            team1_logo = get_image_base64(IPL_TEAMS_INFO[match['team1']]['logo'])
            team2_logo = get_image_base64(IPL_TEAMS_INFO[match['team2']]['logo'])
            st.markdown(f"""
            <div class="match-card">
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{team1_logo}" class="team-logo" />
                        <h4>{match['team1']}</h4>
                    </div>
                    <span class="vs-text">VS</span>
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{team2_logo}" class="team-logo" />
                        <h4>{match['team2']}</h4>
                    </div>
                </div>
                <p style="text-align: center;">Match Date: {match['date']} {match.get('time', '')} IST</p>
                <p style="text-align: center; color: red;">Predictions close at: {match['prediction_cutoff']} IST</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show existing prediction if any
        existing_prediction = st.session_state.game_data.get_user_prediction(match_id, current_user)
        if existing_prediction:
            st.warning(f"""
            ⚠️ You have already made a prediction for this match:
            - Winner: {existing_prediction['winner']}
            - Top Scorer: {existing_prediction['top_scorer']}
            - Top Wicket Taker: {existing_prediction['top_wicket_taker']}
            
            Only one prediction is allowed per match.
            """)
            return  # Exit the function early if prediction exists
        
        # Move these selections outside the form
        winner = st.selectbox("Predict Winner:", ["-Select Winner-", match['team1'], match['team2']], key="winner_select")
        
        # Add team selection for player lists
        selected_team = st.selectbox("Select Team for Players:", ["-Select Team-", match['team1'], match['team2']], key="team_select")
        
        # Initialize variables for player options
        top_scorer_options = ["-Select Top Scorer-"]
        top_wicket_options = ["-Select Top Wicket Taker-"]
        
        if selected_team != "-Select Team-":
            # Load team_players.json directly
            with open('data/team_players.json', 'r') as f:
                team_players_data = json.load(f)
            
            # Get players for selected team
            team_data = team_players_data.get(selected_team, {})
            
            # Add all players with their roles to both dropdowns
            # Add batsmen
            batsmen = team_data.get('batsmen', [])
            for player in batsmen:
                player_with_role = f"{player} (Batsman) - {selected_team}"
                top_scorer_options.append(player_with_role)
                top_wicket_options.append(player_with_role)
            
            # Add bowlers
            bowlers = team_data.get('bowlers', [])
            for player in bowlers:
                player_with_role = f"{player} (Bowler) - {selected_team}"
                top_scorer_options.append(player_with_role)
                top_wicket_options.append(player_with_role)
            
            # Add all-rounders
            all_rounders = team_data.get('all_rounders', [])
            for player in all_rounders:
                player_with_role = f"{player} (All-rounder) - {selected_team}"
                top_scorer_options.append(player_with_role)
                top_wicket_options.append(player_with_role)
        
        top_scorer = st.selectbox("Predict Highest Run-scorer:", top_scorer_options, key="scorer_select")
        top_wicket_taker = st.selectbox("Predict Highest Wicket-taker:", top_wicket_options, key="wicket_select")
        
        # Extract just the player name without role and team
        selected_top_scorer = top_scorer.split(" (")[0] if top_scorer != "-Select Top Scorer-" else ""
        selected_top_wicket_taker = top_wicket_taker.split(" (")[0] if top_wicket_taker != "-Select Top Wicket Taker-" else ""
        
        # Show existing prediction if any
        existing_prediction = st.session_state.game_data.get_user_prediction(match_id, current_user)
        if existing_prediction:
            st.info(f"Your current prediction: Winner - {existing_prediction['winner']}, "
                   f"Top Scorer - {existing_prediction['top_scorer']}, "
                   f"Top Wicket Taker - {existing_prediction['top_wicket_taker']}")
        
        # Put only the submit button in the form
        with st.form("make_prediction"):
            submitted = st.form_submit_button("Submit Prediction")
            if submitted:
                if winner == "-Select Winner-" or selected_top_scorer == "" or selected_top_wicket_taker == "":
                    st.error("Please make all selections before submitting.")
                else:
                    prediction = {
                        'winner': winner,
                        'top_scorer': selected_top_scorer,
                        'top_wicket_taker': selected_top_wicket_taker
                    }
                    if st.session_state.game_data.add_prediction(match_id, current_user, prediction):
                        st.success("Prediction submitted successfully!")
                    else:
                        st.error("Failed to submit prediction. Match might be in progress or completed.")
    
    show_make_prediction()

elif page == "Enter Results":
    @login_required(role="admin")
    def show_enter_results():
        st.header("Enter Match Results")
        
        # Show matches list
        matches_df = st.session_state.game_data.get_matches_list()
        scheduled_matches = matches_df[matches_df['Status'] == 'Scheduled']
        
        if scheduled_matches.empty:
            st.info("No scheduled matches available to enter results.")
            return
        
        st.subheader("Available Matches")
        st.dataframe(scheduled_matches, use_container_width=True)
        
        with st.form("enter_results"):
            match_id = st.selectbox("Select Match", scheduled_matches['Match ID'].tolist())
            
            # Show match details
            match = st.session_state.game_data.get_match(match_id)
            if match:
                st.write(f"**{match['team1']} vs {match['team2']}** on {match['date']}")
                winner = st.selectbox("Match Winner:", [match['team1'], match['team2']])
                
                # Get players for both teams
                team1_players = st.session_state.game_data.get_team_players(match['team1'])
                team2_players = st.session_state.game_data.get_team_players(match['team2'])
                
                # Combine all players for top scorer selection
                all_batsmen = (
                    [(p, match['team1']) for p in team1_players['batsmen']] +
                    [(p, match['team1']) for p in team1_players['all_rounders']] +
                    [(p, match['team2']) for p in team2_players['batsmen']] +
                    [(p, match['team2']) for p in team2_players['all_rounders']]
                )
                
                # Combine all players for top wicket taker selection
                all_bowlers = (
                    [(p, match['team1']) for p in team1_players['bowlers']] +
                    [(p, match['team1']) for p in team1_players['all_rounders']] +
                    [(p, match['team2']) for p in team2_players['bowlers']] +
                    [(p, match['team2']) for p in team2_players['all_rounders']]
                )
                
                # Create formatted options for selectbox
                top_scorer_options = [f"{player} ({team})" for player, team in all_batsmen]
                top_wicket_options = [f"{player} ({team})" for player, team in all_bowlers]
                
                top_scorer = st.selectbox("Highest Run-scorer:", top_scorer_options)
                top_wicket_taker = st.selectbox("Highest Wicket-taker:", top_wicket_options)
                
                # Extract just the player name without team
                top_scorer = top_scorer.split(" (")[0] if top_scorer else ""
                top_wicket_taker = top_wicket_taker.split(" (")[0] if top_wicket_taker else ""
                
                submitted = st.form_submit_button("Submit Results")
                if submitted and all([winner, top_scorer, top_wicket_taker]):
                    result = {
                        'winner': winner,
                        'top_scorer': top_scorer,
                        'top_wicket_taker': top_wicket_taker
                    }
                    if st.session_state.game_data.calculate_points(match_id, result):
                        st.success("Results submitted and points calculated!")
                    else:
                        st.error("Failed to submit results. Match might already be completed.")
    
    show_enter_results()

elif page == "Join Game":
    @login_required()
    def show_join_game():
        st.header("Join Game / Manage Team")
        
        current_user = st.session_state.username
        if current_user in st.session_state.game_data.players:
            player_data = st.session_state.game_data.players[current_user]
            current_team = player_data['team']
            
            # Show current team info with logo
            current_team_logo = get_image_base64(IPL_TEAMS_INFO[current_team]['logo'])
            st.markdown(f"""
            <div class="team-card" style="border-color: {IPL_TEAMS_INFO[current_team]['primary_color']}">
                <h3>Your Current Team</h3>
                <img src="data:image/png;base64,{current_team_logo}" class="team-logo" />
                <h4>{current_team}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if player_data.get('has_switched_team', False):
                original_team = player_data.get('original_team', '')
                st.markdown(f"""
                <p>Original team: {display_team_logo(original_team)}</p>
                """, unsafe_allow_html=True)
            
            # Show team statistics
            st.subheader("Your Team Statistics")
            team_stats = st.session_state.game_data.get_team_stats()
            team_row = team_stats[team_stats['Team'] == current_team].iloc[0]
            st.write(f"Total {current_team} supporters: {team_row['Supporters Count']}")
            st.write(f"Team's total points: {team_row['Total Points']}")
            
            # Show other supporters
            supporters = st.session_state.game_data.get_team_supporters(current_team)
            if len(supporters) > 1:  # More supporters besides current user
                other_supporters = [s for s in supporters if s != current_user]
                st.write("Other supporters of your team:", ", ".join(other_supporters))
            
            # Team Switch Option
            st.markdown("---")
            if not player_data.get('has_switched_team', False):
                st.subheader("Switch Team")
                st.warning("⚠️ You can only switch teams once during the season. Choose wisely!")
                
                with st.form("switch_team"):
                    # Show current team statistics
                    st.write("Current team statistics:")
                    st.dataframe(team_stats, use_container_width=True)
                    
                    # Select new team
                    new_team = st.selectbox(
                        "Select your new team:",
                        [team for team in IPL_TEAMS if team != current_team]
                    )
                    
                    # Show current supporters of selected team
                    new_team_supporters = st.session_state.game_data.get_team_supporters(new_team)
                    if new_team_supporters:
                        st.write(f"Current supporters of {new_team}:", ", ".join(new_team_supporters))
                    
                    # Confirmation checkbox
                    confirm = st.checkbox("I understand this is a one-time switch and cannot be undone")
                    
                    submitted = st.form_submit_button("Switch Team")
                    if submitted:
                        if not confirm:
                            st.error("Please confirm that you understand this is a one-time switch")
                        else:
                            success, message = st.session_state.game_data.switch_team(current_user, new_team)
                            if success:
                                st.success(f"Successfully switched to {new_team}!")
                                st.rerun()
                            else:
                                st.error(message)
            else:
                st.info("You have already used your one-time team switch.")
            return
        
        # New user joining
        with st.form("join_game"):
            st.write("Choose your favorite team:")
            
            # Show current team statistics
            team_stats = st.session_state.game_data.get_team_stats()
            # Add team logos to team statistics
            team_stats['Team'] = team_stats['Team'].apply(
                lambda x: f'<div style="display: flex; align-items: center;">{display_team_logo(x)}</div>'
            )
            st.markdown(team_stats.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            team = st.selectbox("Select your team:", IPL_TEAMS)
            
            # Show current supporters of selected team
            supporters = st.session_state.game_data.get_team_supporters(team)
            if supporters:
                st.write(f"Current supporters of {team}:", ", ".join(supporters))
            
            submitted = st.form_submit_button("Join Game")
            if submitted and team:
                if st.session_state.game_data.add_player(current_user, team):
                    st.success(f"Welcome {current_user}! You've successfully joined with {team}")
                else:
                    st.error("Failed to join the game. Please try again.")
    
    show_join_game()

elif page == "Leaderboard":
    st.header("Leaderboard")
    
    # First show Team Statistics
    st.subheader("Team Statistics")
    team_stats = st.session_state.game_data.get_team_stats()
    # Add team logos to team statistics
    team_stats['Team'] = team_stats['Team'].apply(
        lambda x: f'<div style="display: flex; align-items: center;">{display_team_logo(x)}</div>'
    )
    st.markdown(team_stats.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Add a separator
    st.markdown("---")
    
    # Then show Player Leaderboard
    st.subheader("Player Leaderboard")
    leaderboard = st.session_state.game_data.get_leaderboard()
    
    # Add team logos to leaderboard
    if not leaderboard.empty:
        leaderboard['Team'] = leaderboard['Team'].apply(
            lambda x: f'<div style="display: flex; align-items: center;">{display_team_logo(x)}</div>'
        )
        st.markdown(leaderboard.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Create visualization with team colors
    if not leaderboard.empty:
        # Create a copy of the dataframe for plotting
        plot_df = leaderboard.copy()
        # Extract team names from HTML content
        plot_df['Team'] = plot_df['Team'].apply(lambda x: x.split('</div>')[0].split('>')[-1])
        
        fig = px.bar(
            plot_df,
            x='Username',
            y='Points',
            color='Team',
            title='Player Points Distribution',
            labels={'Points': 'Total Points', 'Username': 'Player'},
            hover_data=['Perfect Predictions', 'Loyalty Bonuses'],
            color_discrete_map={
                team: IPL_TEAMS_INFO[team]['primary_color']
                for team in IPL_TEAMS
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for IPL fans | © 2025") 