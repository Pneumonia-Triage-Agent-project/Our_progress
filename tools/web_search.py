from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()


# Load Tavily API key
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# Web search tool
@tool
def pneumonia_web_search(query: str) -> str:
    """
    Research pneumonia-related information online.

    Search the web for reliable information about pneumonia
    and return a simple research summary with relevant sources.

    The information should be explained in plain English
    without unnecessary medical terminology.
    """

    # Make sure the search stays focused on pneumonia
    search_query = f"pneumonia {query}"

    # Search the web using Tavily
    response = tavily_client.search(
        query=search_query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    # Get search results
    results = response.get("results", [])

    # If nothing was found
    if not results:
        return "No relevant pneumonia search results were found."

    # Create the final report
    report = []

    report.append("PNEUMONIA WEB RESEARCH")
    report.append("=" * 40)

    # Tavily's overall research answer
    answer = response.get("answer")

    if answer:
        report.append("\nResearch Summary:")
        report.append(answer)

    # Add the individual sources
    report.append("\n\nVERIFIED SOURCES")
    report.append("=" * 40)

    for i, result in enumerate(results, start=1):

        title = result.get(
            "title",
            "Unknown source"
        )

        content = result.get(
            "content",
            "No relevant information available."
        )

        url = result.get(
            "url",
            "No URL available."
        )

        report.append(f"\nSource {i}: {title}")
        report.append(f"Relevant information: {content}")
        report.append(f"URL: {url}")

    # Return everything as one string
    return "\n".join(report)

