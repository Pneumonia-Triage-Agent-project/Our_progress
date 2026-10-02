

import os
from langchain_tavily import TavilySearch

# Check for the Tavily API key
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError(
        "TAVILY_API_KEY environment variable is not set."
    )

# Initialize the updated Tavily search tool
web_search = TavilySearch(
    max_results=5,
    search_depth="advanced"
)


def search_medical_information(query: str) -> str:
    """
    Search the web for medical information and return
    results with titles, URLs, and content.
    """
    try:
        results = web_search.invoke({"query": query})

        if not results:
            return "No relevant information found."

        formatted_results = []

        for index, result in enumerate(results, start=1):
            title = result.get("title", "No title available")
            url = result.get("url", "No URL available")
            content = result.get("content", "No content available")

            formatted_results.append(
                f"""
Source {index}
Title: {title}
URL: {url}
Content: {content}
"""
            )

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Web search failed: {str(e)}"