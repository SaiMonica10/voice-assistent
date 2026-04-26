"""
tools/news.py — Live News Headlines for JARVIS

Uses NewsAPI.org (free tier: 100 requests/day).
Get your free key at: https://newsapi.org

Fallback: If no API key, uses DuckDuckGo News (always free).

Learning note:
This shows how to build resilient tools — always have a fallback
when third-party APIs are unavailable or rate-limited.
"""

import requests
import config
from tools.search import search_news as ddg_news   # DuckDuckGo fallback


NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


def get_top_headlines(
    category: str = "general",
    country: str = "in",
    max_articles: int = 5,
) -> str:
    """
    Fetch top news headlines.
    Uses NewsAPI if key is available, falls back to DuckDuckGo (always free).
    """

    # For Indian news, NewsAPI free tier often returns 0 results due to plan restrictions.
    # DuckDuckGo News is always free, real-time, and works globally — use it first.
    if not config.NEWS_API_KEY or country == "in":
        query = f"top {category} news India today" if country == "in" else f"top {category} news today"
        return ddg_news(query, max_results=max_articles)

    try:
        response = requests.get(
            NEWSAPI_URL,
            params={
                "apiKey":   config.NEWS_API_KEY,
                "category": category,
                "country":  country,
                "pageSize": max_articles,
            },
            timeout=5,
        )

        if response.status_code in (401, 426):
            return ddg_news(f"top {category} news today", max_results=max_articles)

        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        # If API returns nothing (common on free tier), fall back
        if not articles:
            return ddg_news(f"top {category} news today", max_results=max_articles)

        category_emoji = {
            "general": "🌍", "business": "💼", "technology": "💻",
            "sports": "⚽", "entertainment": "🎬", "health": "🏥", "science": "🔬",
        }
        emoji = category_emoji.get(category, "📰")

        formatted = f"{emoji} Top {category.capitalize()} Headlines:\n\n"
        for i, article in enumerate(articles, 1):
            title       = article.get("title", "No title")
            source      = article.get("source", {}).get("name", "Unknown")
            description = article.get("description", "") or ""
            url         = article.get("url", "")

            if len(description) > 120:
                description = description[:117] + "..."

            formatted += f"{i}. **{title}**\n"
            if description:
                formatted += f"   {description}\n"
            formatted += f"   Source: {source} | 🔗 {url}\n\n"

        return formatted

    except Exception as e:
        return ddg_news(f"top {category} news today", max_results=max_articles)
