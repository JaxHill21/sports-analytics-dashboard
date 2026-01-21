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
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .news-source {
        color: #FF4B4B;
        font-weight: 500;
    }

    .news-date {
        color: #888888;
    }

    .recent-badge {
        display: inline-block;
        background-color: #FF4B4B;
        color: white;
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-left: 0.5rem;
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

    .no-content-msg {
        background-color: #262730;
        border-radius: 6px;
        padding: 1rem;
        color: #888888;
        text-align: center;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SPORT-SPECIFIC FEED MAPPING (Explicit - no cross-sport contamination)
# =============================================================================
ANALYTICS_FEEDS = {
    "MLB": [
        {"url": "https://blogs.fangraphs.com/feed/", "source": "FanGraphs"},
        {"url": "https://www.baseballprospectus.com/feed/", "source": "Baseball Prospectus"},
        {"url": "https://technology.mlblogs.com/feed", "source": "MLB Tech Blog"},
    ],
    "NFL": [
        {"url": "https://www.the33rdteam.com/feed/", "source": "The 33rd Team"},
        {"url": "https://www.sharpfootballanalysis.com/feed/", "source": "Sharp Football"},
    ],
    "NBA": [
        {"url": "https://dunksandthrees.com/feed", "source": "Dunks & Threes"},
    ],
    "College Football": [
        {"url": "https://www.saturdaytradition.com/feed/", "source": "Saturday Tradition"},
    ],
    "College Basketball": [
        {"url": "https://kenpom.com/blog/feed/", "source": "KenPom"},
    ],
}

# Deep Dive feeds mapped by sport (explicit mapping)
DEEP_DIVE_FEEDS = {
    "MLB": [
        {"url": "https://blogs.fangraphs.com/feed/", "source": "FanGraphs"},
        {"url": "https://www.baseballprospectus.com/feed/", "source": "Baseball Prospectus"},
    ],
    "NFL": [
        {"url": "https://www.the33rdteam.com/feed/", "source": "The 33rd Team"},
        {"url": "https://www.sharpfootballanalysis.com/feed/", "source": "Sharp Football"},
    ],
    "NBA": [
        {"url": "https://dunksandthrees.com/feed", "source": "Dunks & Threes"},
    ],
    "College Football": [
        {"url": "https://www.saturdaytradition.com/feed/", "source": "Saturday Tradition"},
    ],
    "College Basketball": [
        {"url": "https://kenpom.com/blog/feed/", "source": "KenPom"},
    ],
}

# Analytics focus area categories
FOCUS_AREAS = {
    "All Topics": [],
    "Recruiting & Roster": ["recruit", "roster", "draft", "transfer", "portal", "prospect", "signing"],
    "Performance Metrics": ["metric", "stat", "EPA", "CPOE", "WAR", "xG", "expected", "efficiency", "rating", "advanced"],
    "Coaching Strategy": ["coach", "strategy", "scheme", "play-call", "decision", "fourth down", "clock", "timeout"],
    "Salary Cap/NIL": ["salary", "cap", "contract", "NIL", "money", "deal", "extension", "free agent"],
    "Technology & Tools": ["tracking", "wearable", "AI", "machine learning", "model", "algorithm", "technology", "data"],
}

# =============================================================================
# DATE FILTERING: Only show articles from last 30 days (after Dec 21, 2025)
# =============================================================================
MAX_AGE_DAYS = 30
RECENT_THRESHOLD_DAYS = 7


def parse_date(date_str: str) -> datetime:
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None

    # Common RSS date formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RFC 822
        "%a, %d %b %Y %H:%M:%S %Z",      # RFC 822 with timezone name
        "%a, %d %b %Y %H:%M:%S GMT",     # RFC 822 GMT
        "%Y-%m-%dT%H:%M:%S%z",           # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",            # ISO 8601 UTC
        "%Y-%m-%dT%H:%M:%S.%fZ",         # ISO 8601 with microseconds
        "%Y-%m-%d %H:%M:%S",             # Simple datetime
        "%Y-%m-%d",                       # Simple date
    ]

    # Clean up the date string
    date_str = re.sub(r'\s+', ' ', date_str.strip())
    # Handle +0000 timezone format
    date_str = re.sub(r'\+0000$', '+00:00', date_str)

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # Make timezone-naive for comparison
            if parsed.tzinfo:
                parsed = parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            continue

    return None


def format_date_display(pub_date: datetime) -> str:
    """Format date for display on cards."""
    if not pub_date:
        return "Unknown date"

    now = datetime.now()
    diff = now - pub_date

    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            return "Just now"
        elif hours == 1:
            return "1 hour ago"
        else:
            return f"{hours} hours ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return pub_date.strftime("%b %d, %Y")


def is_recent(pub_date: datetime) -> bool:
    """Check if article is less than 7 days old."""
    if not pub_date:
        return False
    return (datetime.now() - pub_date).days < RECENT_THRESHOLD_DAYS


@st.cache_data(ttl=600)
def fetch_rss_feed(url: str, source: str, limit: int = 15) -> list:
    """Fetch and parse RSS feed with caching, error handling, and 30-day filtering."""
    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            return []

        cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
        items = []

        for entry in feed.entries:
            if len(items) >= limit:
                break

            try:
                # Parse publication date
                pub_date_str = entry.get("published", "") or entry.get("updated", "")
                pub_date = parse_date(pub_date_str)

                # CRITICAL: Skip articles older than 30 days
                if pub_date and pub_date < cutoff_date:
                    continue

                # If we can't parse the date, skip the article (be strict)
                if not pub_date:
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
                    "date_display": format_date_display(pub_date),
                    "is_recent": is_recent(pub_date),
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
    """Render a clickable news card with source, date, and RECENT badge."""
    try:
        category = categorize_article(item.get("title", ""), item.get("summary", ""))
        category_html = f'<span class="category-tag">{category}</span>' if show_category else ""

        # Add RECENT badge if article is less than 7 days old
        recent_badge = '<span class="recent-badge">RECENT</span>' if item.get("is_recent") else ""

        date_display = item.get("date_display", "Unknown date")

        st.markdown(f"""
        <div class="news-card">
            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer">
                {category_html}
                <div class="news-title">{item.get('title', 'No title')}{recent_badge}</div>
                <div class="news-summary">{item.get('summary', '')}</div>
                <div class="news-meta">
                    <span class="news-source">{item.get('source', 'Unknown')}</span>
                    <span class="news-date">{date_display}</span>
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


def render_no_content_message(source_name: str):
    """Render message when no recent articles from a source."""
    st.markdown(f"""
    <div class="no-content-msg">
        No recent updates from {source_name} (last 30 days)
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SIDEBAR
# =============================================================================
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
    st.markdown("---")
    st.markdown(f"*Showing articles from last {MAX_AGE_DAYS} days*")


# =============================================================================
# MAIN CONTENT
# =============================================================================
st.markdown("""
<div class="dashboard-header">
    <h1>Sports Analytics Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# Analytics News Feed Section
render_section_header(f"Analytics News Feed - {selected_sport}")

# Fetch news from ONLY the selected sport's feeds (no cross-contamination)
all_news = []
sport_feeds = ANALYTICS_FEEDS.get(selected_sport, [])
sources_with_no_content = []

with st.spinner(f"Loading {selected_sport} analytics news..."):
    for feed_info in sport_feeds:
        try:
            items = fetch_rss_feed(feed_info["url"], feed_info["source"])
            if items:
                all_news.extend(items)
            else:
                sources_with_no_content.append(feed_info["source"])
        except Exception:
            sources_with_no_content.append(feed_info["source"])

# Filter by focus area
filtered_news = filter_by_focus_area(all_news, focus_area)

# Deduplicate by title and sort by date
seen_titles = set()
unique_news = []
for item in filtered_news:
    title = item.get("title", "")
    if title and title not in seen_titles:
        seen_titles.add(title)
        unique_news.append(item)

# Sort newest first
unique_news.sort(key=lambda x: x.get("pub_date") or datetime.min, reverse=True)

if unique_news:
    col1, col2 = st.columns(2)
    for i, item in enumerate(unique_news[:10]):
        with col1 if i % 2 == 0 else col2:
            render_news_card(item)
else:
    st.info(f"No recent analytics news available for {selected_sport} (last {MAX_AGE_DAYS} days). Try selecting 'All Topics' or check back later.")

# Show sources with no recent content
if sources_with_no_content:
    with st.expander("Sources with no recent updates"):
        for source in sources_with_no_content:
            st.markdown(f"- {source}")

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

# =============================================================================
# DEEP DIVES SECTION - RESPECTS SPORT FILTER (CRITICAL FIX)
# =============================================================================
render_section_header(f"Deep Dives - {selected_sport}")

# Fetch feature content ONLY from the selected sport's feeds
deep_dive_feeds = DEEP_DIVE_FEEDS.get(selected_sport, [])
deep_dive_news = []

with st.spinner(f"Loading {selected_sport} feature articles..."):
    for feed_info in deep_dive_feeds:
        try:
            items = fetch_rss_feed(feed_info["url"], feed_info["source"], limit=8)
            deep_dive_news.extend(items)
        except Exception:
            continue

# Filter for longer/feature content and sort by date
feature_articles = [item for item in deep_dive_news if len(item.get("summary", "")) > 80]
feature_articles.sort(key=lambda x: x.get("pub_date") or datetime.min, reverse=True)

# Deduplicate
seen_feature_titles = set()
unique_features = []
for item in feature_articles:
    title = item.get("title", "")
    if title and title not in seen_feature_titles:
        seen_feature_titles.add(title)
        unique_features.append(item)

dive_col1, dive_col2 = st.columns(2)

with dive_col1:
    st.markdown(f"#### Latest {selected_sport} Analytics")
    if unique_features:
        for item in unique_features[:3]:
            render_news_card(item, show_category=True)
    else:
        st.markdown(f"""
        <div class="no-content-msg">
            No recent feature articles for {selected_sport}
        </div>
        """, unsafe_allow_html=True)

with dive_col2:
    st.markdown(f"#### More {selected_sport} Features")
    if len(unique_features) > 3:
        for item in unique_features[3:6]:
            render_news_card(item, show_category=True)
    else:
        st.markdown(f"""
        <div class="no-content-msg">
            Check back for more {selected_sport} content
        </div>
        """, unsafe_allow_html=True)
