import streamlit as st
import feedparser
from datetime import datetime, timedelta
import html
import re

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
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .dashboard-header {
        background: linear-gradient(90deg, #1a2a4a 0%, #0d1929 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #FF4B4B;
    }

    .dashboard-header h1 {
        color: white;
        margin: 0;
        font-weight: 600;
        font-size: 1.5rem;
    }

    .metric-card {
        background-color: #262730;
        border-radius: 8px;
        padding: 1.25rem;
        border-left: 4px solid #FF4B4B;
        margin-bottom: 1rem;
        min-height: 120px;
    }

    .metric-card h4 {
        color: #FF4B4B;
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

    .news-card {
        background-color: #1A1A2E;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #FF4B4B;
        transition: all 0.2s ease;
    }

    .news-card:hover {
        background-color: #262730;
        transform: translateX(4px);
    }

    .news-card a {
        text-decoration: none;
        color: inherit;
        display: block;
    }

    .news-title {
        color: #FAFAFA;
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
        color: #FF4B4B;
        font-weight: 500;
    }

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

    .section-header {
        color: #FAFAFA;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #FF4B4B;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .section-timestamp {
        color: #666666;
        font-size: 0.75rem;
        font-weight: 400;
    }

    .placeholder-box {
        background-color: #262730;
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
        color: #FAFAFA;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }

    .placeholder-box p {
        margin: 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Analytics-focused RSS feeds (verified working)
ANALYTICS_FEEDS = {
    "MLB": [
        {"url": "https://blogs.fangraphs.com/feed/", "source": "FanGraphs"},
        {"url": "https://www.baseballprospectus.com/feed/", "source": "Baseball Prospectus"},
        {"url": "https://technology.mlblogs.com/feed", "source": "MLB Tech Blog"},
    ],
    "NFL": [
        {"url": "https://www.the33rdteam.com/feed/", "source": "The 33rd Team"},
        {"url": "https://www.sharpfootballanalysis.com/feed/", "source": "Sharp Football"},
        {"url": "https://www.fanduel.com/research/rss/recent", "source": "FanDuel Research"},
    ],
    "NBA": [
        {"url": "https://dunksandthrees.com/feed", "source": "Dunks & Threes"},
        {"url": "https://www.fanduel.com/research/rss/recent", "source": "FanDuel Research"},
        {"url": "https://www.espn.com/espn/rss/nba/news", "source": "ESPN NBA"},
    ],
    "College Football": [
        {"url": "https://www.saturdaytradition.com/feed/", "source": "Saturday Tradition"},
        {"url": "https://www.the33rdteam.com/feed/", "source": "The 33rd Team"},
        {"url": "https://www.espn.com/espn/rss/ncf/news", "source": "ESPN CFB"},
    ],
    "College Basketball": [
        {"url": "https://kenpom.com/blog/feed/", "source": "KenPom"},
        {"url": "https://www.espn.com/espn/rss/ncb/news", "source": "ESPN CBB"},
    ],
}

# Feature/Deep Dive feeds for longer-form analytics content
DEEP_DIVE_FEEDS = [
    {"url": "https://blogs.fangraphs.com/feed/", "source": "FanGraphs Features"},
    {"url": "https://www.baseballprospectus.com/feed/", "source": "Baseball Prospectus"},
    {"url": "https://www.the33rdteam.com/feed/", "source": "The 33rd Team"},
    {"url": "https://technology.mlblogs.com/feed", "source": "MLB Tech Blog"},
]

# Technology & Industry feeds (cross-sport)
TECH_FEEDS = [
    {"url": "https://technology.mlblogs.com/feed", "source": "MLB Tech Blog"},
]

# Analytics focus area categories
FOCUS_AREAS = {
    "All Topics": [],
    "Recruiting & Roster": ["recruit", "roster", "draft", "transfer", "portal", "prospect", "signing"],
    "Performance Metrics": ["metric", "stat", "EPA", "CPOE", "WAR", "xG", "expected", "efficiency", "rating", "advanced"],
    "Coaching Strategy": ["coach", "strategy", "scheme", "play-call", "decision", "fourth down", "clock", "timeout"],
    "Salary Cap/NIL": ["salary", "cap", "contract", "NIL", "money", "deal", "extension", "free agent"],
    "Technology & Tools": ["tracking", "wearable", "AI", "machine learning", "model", "algorithm", "technology", "data"],
}


def parse_date(date_str: str) -> datetime:
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None

    # Common RSS date formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RFC 822
        "%a, %d %b %Y %H:%M:%S %Z",      # RFC 822 with timezone name
        "%Y-%m-%dT%H:%M:%S%z",           # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",            # ISO 8601 UTC
        "%Y-%m-%d %H:%M:%S",             # Simple datetime
        "%Y-%m-%d",                       # Simple date
    ]

    # Clean up the date string
    date_str = re.sub(r'\s+', ' ', date_str.strip())

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # If parsing fails, return None (will include the article)
    return None


@st.cache_data(ttl=600)
def fetch_rss_feed(url: str, source: str, limit: int = 15, max_age_days: int = 60) -> list:
    """Fetch and parse RSS feed with caching, error handling, and date filtering."""
    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            return []

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        items = []

        for entry in feed.entries:
            if len(items) >= limit:
                break

            try:
                # Parse and filter by date
                pub_date_str = entry.get("published", "") or entry.get("updated", "")
                pub_date = parse_date(pub_date_str)

                # Skip articles older than max_age_days (if we can parse the date)
                if pub_date:
                    # Make both datetimes naive for comparison
                    if pub_date.tzinfo:
                        pub_date = pub_date.replace(tzinfo=None)
                    if pub_date < cutoff_date:
                        continue

                summary = entry.get("summary", "") or entry.get("description", "")
                summary = html.unescape(str(summary))
                # Remove HTML tags
                summary = re.sub(r'<[^>]+>', ' ', summary)
                summary = re.sub(r'\s+', ' ', summary).strip()

                if len(summary) > 200:
                    summary = summary[:200].rsplit(" ", 1)[0] + "..."

                items.append({
                    "title": str(entry.get("title", "No title")),
                    "link": str(entry.get("link", "#")),
                    "published": pub_date_str,
                    "pub_date": pub_date,
                    "summary": summary,
                    "source": source,
                })
            except Exception:
                continue

        # Sort by date (newest first)
        items.sort(key=lambda x: x.get("pub_date") or datetime.min, reverse=True)

        return items
    except Exception:
        return []


def categorize_article(title: str, summary: str) -> str:
    """Categorize an article based on keywords."""
    try:
        text = (str(title) + " " + str(summary)).lower()

        category_scores = {
            "Recruiting Analytics": ["recruit", "draft", "prospect", "transfer", "portal", "signing", "commit"],
            "Performance Metrics": ["metric", "stat", "EPA", "CPOE", "WAR", "efficiency", "rating", "advanced", "expected"],
            "Coaching Analytics": ["coach", "strategy", "scheme", "decision", "fourth down", "play-call", "game plan"],
            "Roster Optimization": ["roster", "lineup", "rotation", "depth", "minutes", "snap", "usage"],
            "Salary Cap/NIL": ["salary", "cap", "contract", "NIL", "money", "deal", "extension"],
        }

        best_category = "Performance Metrics"
        best_score = 0

        for category, keywords in category_scores.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > best_score:
                best_score = score
                best_category = category

        return best_category
    except Exception:
        return "Performance Metrics"


def filter_by_focus_area(items: list, focus_area: str) -> list:
    """Filter news items by analytics focus area."""
    try:
        if focus_area == "All Topics":
            return items

        keywords = FOCUS_AREAS.get(focus_area, [])
        if not keywords:
            return items

        filtered = []
        for item in items:
            text = (str(item.get("title", "")) + " " + str(item.get("summary", ""))).lower()
            if any(kw.lower() in text for kw in keywords):
                filtered.append(item)

        return filtered if filtered else items[:5]
    except Exception:
        return items


def render_news_card(item: dict, show_category: bool = True):
    """Render a clickable news card with source attribution."""
    try:
        category = categorize_article(item.get("title", ""), item.get("summary", ""))
        category_html = f'<span class="category-tag">{category}</span>' if show_category else ""

        st.markdown(f"""
        <div class="news-card">
            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer">
                {category_html}
                <div class="news-title">{item.get('title', 'No title')}</div>
                <div class="news-summary">{item.get('summary', '')}</div>
                <div class="news-meta">
                    <span class="news-source">{item.get('source', 'Unknown')}</span>
                    <span>{item.get('published', '')}</span>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass


def render_section_header(title: str):
    """Render a section header with timestamp."""
    timestamp = datetime.now().strftime("%I:%M %p")
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

    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Last loaded:**")
    st.markdown(f"{datetime.now().strftime('%I:%M:%S %p')}")


# Main content area
st.markdown("""
<div class="dashboard-header">
    <h1>Sports Analytics Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# Analytics News Feed Section
render_section_header(f"Analytics News Feed - {selected_sport}")

# Fetch news from sources for selected sport
all_news = []
sport_feeds = ANALYTICS_FEEDS.get(selected_sport, [])

with st.spinner(f"Loading {selected_sport} analytics news..."):
    for feed_info in sport_feeds:
        try:
            items = fetch_rss_feed(feed_info["url"], feed_info["source"])
            all_news.extend(items)
        except Exception:
            continue

# Filter by focus area
filtered_news = filter_by_focus_area(all_news, focus_area)

# Deduplicate by title
seen_titles = set()
unique_news = []
for item in filtered_news:
    title = item.get("title", "")
    if title and title not in seen_titles:
        seen_titles.add(title)
        unique_news.append(item)

if unique_news:
    col1, col2 = st.columns(2)
    for i, item in enumerate(unique_news[:10]):
        with col1 if i % 2 == 0 else col2:
            render_news_card(item)
else:
    st.info("No analytics news available for the selected filters. Try selecting 'All Topics' or a different sport.")

st.markdown("---")

# Industry Trends Section
render_section_header("Industry Trends")

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

# Deep Dives Section - Feature articles from analytics sources
render_section_header("Deep Dives")

# Fetch feature content from deep dive feeds
deep_dive_news = []
with st.spinner("Loading feature articles..."):
    for feed_info in DEEP_DIVE_FEEDS:
        try:
            items = fetch_rss_feed(feed_info["url"], feed_info["source"], limit=5)
            deep_dive_news.extend(items)
        except Exception:
            continue

# Filter for longer/feature content (longer summaries suggest deeper pieces)
feature_articles = [item for item in deep_dive_news if len(item.get("summary", "")) > 100]

dive_col1, dive_col2 = st.columns(2)

with dive_col1:
    st.markdown("#### Analytics-Driven Decisions")
    if feature_articles:
        for item in feature_articles[:3]:
            render_news_card(item, show_category=True)
    else:
        st.markdown("""
        <div class="placeholder-box">
            <p>Loading feature content...</p>
        </div>
        """, unsafe_allow_html=True)

with dive_col2:
    st.markdown("#### Latest Analytics Features")
    if len(feature_articles) > 3:
        for item in feature_articles[3:6]:
            render_news_card(item, show_category=True)
    else:
        st.markdown("""
        <div class="placeholder-box">
            <p>Loading feature content...</p>
        </div>
        """, unsafe_allow_html=True)
