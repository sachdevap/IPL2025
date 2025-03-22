# IPL 2025 Prediction League 🏏

A Streamlit web application for managing an IPL prediction game where players compete by predicting match outcomes and tracking their scores.

## Features

- Team selection system with first-come-first-served basis
- Match prediction system for all IPL 2025 matches
- Point calculation based on correct predictions
- Special scoring for playoff matches
- Real-time leaderboard with visualizations
- Persistent data storage

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd IPL2025
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application locally:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Create an account on [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository
3. Deploy the app by selecting the repository and branch
4. The app will be automatically deployed and available at a public URL

## Game Rules

### Setup
- Each player picks one IPL team (no duplicates allowed)
- Players must submit predictions before each match

### Predictions Include
- Match winner
- Highest run-scorer
- Highest wicket-taker

### Scoring System
- Correct match winner: 10 points
- Correct highest run-scorer: 5 points
- Correct highest wicket-taker: 5 points
- Team loyalty bonus: 5 extra points
- Perfect prediction bonus: 10 points
- All points are doubled for playoff matches

## Data Storage

The application stores all game data in JSON files in the `data` directory:
- `players.json`: Player information and scores
- `predictions.json`: Match predictions
- `matches.json`: Match results

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.