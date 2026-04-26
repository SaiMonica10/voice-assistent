"""
tools/search.py — Web Search Tool for JARVIS

Uses DuckDuckGo search — completely FREE, no API key needed.

Learning note:
This is a "tool" that the LLM (Gemini) can call. When you ask JARVIS
"search for the latest Python tutorials", Gemini detects the intent,
calls this function, and returns formatted results back to the user.

This pattern is called "Function Calling" or "Tool Use" — one of the
most important concepts in modern LLM application development.
"""

from ddgs import DDGS


def web_search(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo and return formatted results.

    Args:
        query: The search query string.
        max_results: Number of results to return (default: 3).

    Returns:
        A formatted string with search results, or an error message.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for '{query}'."

        # Format results nicely for the LLM to parse and summarize
        formatted = f"Web search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result.get('title', 'No title')}**\n"
            formatted += f"   {result.get('body', 'No description')}\n"
            formatted += f"   🔗 {result.get('href', 'No URL')}\n\n"

        return formatted

    except Exception as e:
        return f"Search failed: {str(e)}. Please check your internet connection."


def search_news(query: str, max_results: int = 5) -> str:
    """
    Search for news articles using DuckDuckGo News.

    Args:
        query: News topic to search for.
        max_results: Number of articles to return.

    Returns:
        Formatted news results string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))

        if not results:
            return f"No news found for '{query}'."

        formatted = f"Latest news about '{query}':\n\n"
        for i, article in enumerate(results, 1):
            formatted += f"{i}. **{article.get('title', 'No title')}**\n"
            formatted += f"   {article.get('body', 'No description')}\n"
            formatted += f"   Source: {article.get('source', 'Unknown')} | "
            formatted += f"🔗 {article.get('url', 'No URL')}\n\n"

        return formatted

    except Exception as e:
        return f"News search failed: {str(e)}"
