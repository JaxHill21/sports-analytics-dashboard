# Sports Analytics Dashboard

A Streamlit-based dashboard for aggregating and displaying sports analytics news and industry insights across major sports leagues.

## Features

- **Multi-Sport Coverage**: NFL, NBA, MLB, College Football, and College Basketball
- **Analytics Focus Filters**: Filter news by topic area including Recruiting & Roster, Performance Metrics, Coaching Strategy, Salary Cap/NIL, and Technology & Tools
- **RSS Feed Aggregation**: Pulls from analytics-focused sources like FanGraphs and ESPN
- **Auto-Categorization**: Articles are automatically categorized based on content analysis
- **Dark Theme**: Clean, modern dark interface optimized for readability
- **Cached Data**: 10-minute cache to minimize API calls and improve performance

## Project Structure

```
sports-analytics-dashboard/
├── .streamlit/
│   └── config.toml      # Streamlit configuration and theme
├── app.py               # Main application file
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Run Locally

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sports-analytics-dashboard
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

5. Open your browser to `http://localhost:8501`

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click "New app" and connect your GitHub account

4. Select:
   - Repository: `<your-username>/sports-analytics-dashboard`
   - Branch: `main`
   - Main file path: `app.py`

5. Click "Deploy"

The app will be live at `https://<your-app-name>.streamlit.app`

## Dependencies

- streamlit==1.31.0
- feedparser==6.0.10
- requests==2.31.0
- pandas==2.1.0
- plotly==5.18.0

## Configuration

Theme and server settings are configured in `.streamlit/config.toml`. The default theme uses a dark color scheme with red accents.
