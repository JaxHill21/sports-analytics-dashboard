import streamlit as st
import feedparser
from datetime import datetime
import time
import html

# Page configuration
st.set_page_config(
    page_title="Sports Analytics Dashboard",
    page_icon="SA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header styling - more subdued navy blue */
    .dashboard-header {
        background: linear-gradient(90deg, #1a2a4a 0%, #0d1929 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #CC0000;
    }

    .dashboard-header h1 {
        color: white;
        margin: 0;
        font-weight: 600;
        font-size: 1.5rem;
    }

    /* Card styling */
    .metric-card {
        background-color: #2B2B2B;
        border-radius: 8px;
        padding: 1.25rem;
        border-left: 4px solid #CC0000;
        margin-bottom: 1rem;
        min-height: 120px;
    }

    .metric-card h4 {
        color: #CC0000;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .metric-card p {
        color: #888888;
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.4;
    }

    /* News card styling - clickable */
    .news-card {
        background-color: #1A1A1A;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #CC0000;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .news-card:hover {
        background-color: #2B2B2B;
        transform: translateX(4px);
    }

    .news-card a {
        text-decoration: none;
        color: inherit;
        display: block;
    }

    .news-title {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }

    .news-summary {
        color: #AAAAAA;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }

    .news-meta {
        color: #888888;
        font-size: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .news-source {
        color: #CC0000;
        font-weight: 500;
    }

    /* Category tag styling */
    .category-tag {
        display: inline-block;
        background-color: #333333;
        color: #CCCCCC;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-right: 0.5rem;
        text-transform: uppercase;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1A1A1A;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF;
    }

    /* Section headers */
    .section-header {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #CC0000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .section-timestamp {
        color: #666666;
        font-size: 0.75rem;
        font-weight: 400;
    }

    /* Placeholder styling */
    .placeholder-box {
        background-color: #2B2B2B;
        border: 1px solid #444444;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        color: #888888;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .placeholder-box h3 {
        color: #FFFFFF;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }

    .placeholder-box p {
        margin: 0;
        font-size: 0.85rem;
    }

    /* News feed container */
    .news-feed-container {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 0.5rem;
    }

    /* Scrollbar styling */
    .news-feed-container::-webkit-scrollbar {
        width: 6px;
    }

    .news-feed-container::-webkit-scrollbar-track {
        background: #1A1A1A;
    }

    .news-feed-container::-webkit-scrollbar-thumb {
        background: #444444;
        border-radius: 3px;
    }

    .news-feed-container::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }

    /* Filter section styling */
    .filter-section {
        margin-bottom: 1rem;
    }

    .filter-label {
        color: #AAAAAA;
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Analytics-focused RSS feeds organized by sport and category
ANALYTICS_FEEDS = {
    "NFL": {
        "general": [
            {"url": "https://www.footballoutsiders.com/rss.xml", "source": "Football Outsiders"},
            {"url": "https://fivethirtyeight.com/tag/nfl/feed/", "source": "FiveThirtyEight NFL"},
        ],
        "fangraphs": None,  # FanGraphs is baseball-focused
    },
    "NBA": {
        "general": [
            {"url": "https://fivethirtyeight.com/tag/nba/feed/", "source": "FiveThirtyEight NBA"},
            {"url": "https://cleaningtheglass.com/feed/", "source": "Cleaning The Glass"},
        ],
    },
    "MLB": {
        "general": [
            {"url": "https://blogs.fangraphs.com/feed/", "source": "FanGraphs"},
            {"url": "https://fivethirtyeight.com/tag/mlb/feed/", "source": "FiveThirtyEight MLB"},
        ],
    },
    "College Football": {
        "general": [
            {"url": "https://fivethirtyeight.com/tag/college-football/feed/", "source": "FiveThirtyEight CFB"},
            {"url": "https://www.footballoutsiders.com/rss.xml", "source": "Football Outsiders"},
        ],
    },
    "College Basketball": {
        "general": [
            {"url": "https://fivethirtyeight.com/tag/college-basketball/feed/", "source": "FiveThirtyEight CBB"},
            {"url": "https://kenpom.com/blog/feed/", "source": "KenPom Blog"},
        ],
    },
}

# Analytics focus area categories and keywords for filtering
FOCUS_AREAS = {
    "All Topics": [],
    "Recruiting & Roster": ["recruit", "roster", "draft", "transfer", "portal", "prospect", "signing"],
    "Performance Metrics": ["metric", "stat", "EPA", "CPOE", "WAR", "xG", "expected", "efficiency", "rating", "advanced"],
    "Coaching Strategy": ["coach", "strategy", "scheme", "play-call", "decision", "fourth down", "clock", "timeout"],
    "Salary Cap/NIL": ["salary", "cap", "contract", "NIL", "money", "deal", "extension", "free agent"],
    "Technology & Tools": ["tracking", "wearable", "AI", "machine learning", "model", "algorithm", "technology", "data"],
}

# Initialize session state
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if "feed_cache" not in st.session_state:
    st.session_state.feed_cache = {}
if "section_timestamps" not in st.session_state:
    st.session_state.section_timestamps = {}


def fetch_rss_feed(url: str, source: str, limit: int = 15) -> list:
    """Fetch and parse RSS feed, returning list of news items with source."""
    cache_key = f"{url}_{source}"

    # Check cache (5 minute expiry)
    if cache_key in st.session_state.feed_cache:
        cached_time, cached_data = st.session_state.feed_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < 300:
            return cached_data

    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            # Clean and truncate summary
            summary = entry.get("summary", "") or entry.get("description", "")
            # Remove HTML tags
            summary = html.unescape(summary)
            summary = summary.replace("<p>", "").replace("</p>", " ")
            summary = summary.replace("<br>", " ").replace("<br/>", " ")
            # Take first ~200 chars for 2-sentence summary
            if len(summary) > 200:
                summary = summary[:200].rsplit(" ", 1)[0] + "..."

            items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", "#"),
                "published": entry.get("published", ""),
                "summary": summary,
                "source": source,
            })

        # Cache the results
        st.session_state.feed_cache[cache_key] = (datetime.now(), items)
        return items
    except Exception:
        return []


def categorize_article(title: str, summary: str) -> str:
    """Categorize an article based on keywords in title and summary."""
    text = (title + " " + summary).lower()

    category_scores = {
        "Recruiting Analytics": ["recruit", "draft", "prospect", "transfer", "portal", "signing", "commit"],
        "Performance Metrics": ["metric", "stat", "EPA", "CPOE", "WAR", "efficiency", "rating", "advanced", "expected"],
        "Coaching Analytics": ["coach", "strategy", "scheme", "decision", "fourth down", "play-call", "game plan"],
        "Roster Optimization": ["roster", "lineup", "rotation", "depth", "minutes", "snap", "usage"],
        "Salary Cap/NIL": ["salary", "cap", "contract", "NIL", "money", "deal", "extension"],
    }

    best_category = "Performance Metrics"  # Default
    best_score = 0

    for category, keywords in category_scores.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def filter_by_focus_area(items: list, focus_area: str) -> list:
    """Filter news items by analytics focus area."""
    if focus_area == "All Topics":
        return items

    keywords = FOCUS_AREAS.get(focus_area, [])
    if not keywords:
        return items

    filtered = []
    for item in items:
        text = (item["title"] + " " + item["summary"]).lower()
        if any(kw.lower() in text for kw in keywords):
            filtered.append(item)

    return filtered if filtered else items[:5]  # Return at least some items


def render_news_card(item: dict, show_category: bool = True):
    """Render a clickable news card with source attribution."""
    category = categorize_article(item["title"], item["summary"])
    category_html = f'<span class="category-tag">{category}</span>' if show_category else ""

    st.markdown(f"""
    <div class="news-card">
        <a href="{item['link']}" target="_blank" rel="noopener noreferrer">
            {category_html}
            <div class="news-title">{item['title']}</div>
            <div class="news-summary">{item['summary']}</div>
            <div class="news-meta">
                <span class="news-source">{item['source']}</span>
                <span>{item['published']}</span>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)


def get_section_timestamp(section_name: str) -> str:
    """Get or create timestamp for a section."""
    if section_name not in st.session_state.section_timestamps:
        st.session_state.section_timestamps[section_name] = datetime.now()
    return st.session_state.section_timestamps[section_name].strftime("%I:%M %p")


def render_section_header(title: str, section_key: str):
    """Render a section header with timestamp."""
    timestamp = get_section_timestamp(section_key)
    st.markdown(f"""
    <div class="section-header">
        <span>{title}</span>
        <span class="section-timestamp">Last updated: {timestamp}</span>
    </div>
    """, unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.markdown("## Sports Filter")
    st.markdown("---")

    selected_sport = st.radio(
        "Select Sport",
        options=list(ANALYTICS_FEEDS.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("## Analytics Focus Area")

    focus_area = st.radio(
        "Filter by Topic",
        options=list(FOCUS_AREAS.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Refresh controls
    st.markdown("### Settings")
    auto_refresh = st.toggle("Auto-refresh (5 min)", value=True)

    if st.button("Refresh Now", use_container_width=True):
        st.session_state.last_refresh = datetime.now()
        st.session_state.feed_cache = {}
        st.session_state.section_timestamps = {}
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Last updated:**")
    st.markdown(f"{st.session_state.last_refresh.strftime('%I:%M:%S %p')}")


# Main content area
st.markdown("""
<div class="dashboard-header">
    <h1>Sports Analytics Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# Analytics News Feed Section
render_section_header(f"Analytics News Feed - {selected_sport}", "news_feed")

# Fetch news from all sources for selected sport
all_news = []
sport_feeds = ANALYTICS_FEEDS.get(selected_sport, {}).get("general", [])

with st.spinner(f"Loading {selected_sport} analytics news..."):
    for feed_info in sport_feeds:
        items = fetch_rss_feed(feed_info["url"], feed_info["source"])
        all_news.extend(items)

# Filter by focus area
filtered_news = filter_by_focus_area(all_news, focus_area)

# Sort by date (most recent first) and deduplicate by title
seen_titles = set()
unique_news = []
for item in filtered_news:
    if item["title"] not in seen_titles:
        seen_titles.add(item["title"])
        unique_news.append(item)

if unique_news:
    # Group by category
    categories = {}
    for item in unique_news:
        cat = categorize_article(item["title"], item["summary"])
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    # Display in tabs by category
    if len(categories) > 1:
        tabs = st.tabs(list(categories.keys()))
        for tab, (cat_name, cat_items) in zip(tabs, categories.items()):
            with tab:
                st.markdown('<div class="news-feed-container">', unsafe_allow_html=True)
                for item in cat_items[:8]:
                    render_news_card(item, show_category=False)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Single category or no categorization
        col1, col2 = st.columns(2)
        for i, item in enumerate(unique_news[:10]):
            with col1 if i % 2 == 0 else col2:
                render_news_card(item)
else:
    st.info("No analytics news available for the selected filters. Try selecting 'All Topics' or a different sport.")

st.markdown("---")

# Industry Trends Section
render_section_header("Industry Trends", "industry_trends")

trend_cols = st.columns(4)

with trend_cols[0]:
    st.markdown("""
    <div class="metric-card">
        <h4>Latest Research Papers</h4>
        <p>Recent analytics publications from MIT Sloan Sports Analytics Conference, academic journals, and team research departments</p>
    </div>
    """, unsafe_allow_html=True)

with trend_cols[1]:
    st.markdown("""
    <div class="metric-card">
        <h4>Methodology Updates</h4>
        <p>New metrics being adopted: EPA, CPOE, Win Shares, xG, RAPTOR, catch probability, and other advanced statistics</p>
    </div>
    """, unsafe_allow_html=True)

with trend_cols[2]:
    st.markdown("""
    <div class="metric-card">
        <h4>Technology Adoption</h4>
        <p>Player tracking systems, wearable tech, computer vision, and AI/ML tools being deployed across leagues</p>
    </div>
    """, unsafe_allow_html=True)

with trend_cols[3]:
    st.markdown("""
    <div class="metric-card">
        <h4>Hiring Activity</h4>
        <p>Latest analytics department hires, new roles created, and career opportunities across professional teams</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Deep Dives Section
render_section_header("Deep Dives", "deep_dives")

dive_col1, dive_col2 = st.columns(2)

with dive_col1:
    st.markdown("""
    <div class="placeholder-box">
        <h3>Analytics-Driven Decisions</h3>
        <p>Recent team moves explained through analytics: trades, draft picks, free agent signings, and strategic pivots backed by data</p>
    </div>
    """, unsafe_allow_html=True)

with dive_col2:
    st.markdown("""
    <div class="placeholder-box">
        <h3>Case Studies</h3>
        <p>Successful analytics implementations: how teams leveraged data to gain competitive advantages and transform their organizations</p>
    </div>
    """, unsafe_allow_html=True)

# Auto-refresh logic (5 minutes = 300 seconds)
if auto_refresh:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh >= 300:
        st.session_state.last_refresh = datetime.now()
        st.session_state.feed_cache = {}
        st.session_state.section_timestamps = {}
        st.rerun()
    else:
        remaining = int(300 - time_since_refresh)
        mins, secs = divmod(remaining, 60)
        st.sidebar.markdown(f"**Next refresh:** {mins}m {secs}s")
        time.sleep(1)
        st.rerun()
