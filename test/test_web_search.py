
from tools.web_search_tool import web_search

query = "Community-acquired pneumonia diagnosis and treatment guidelines"

try:
    results = web_search.invoke({
        "query": query
    })

    print("\nMEDICAL WEB SEARCH RESULTS\n")

    if isinstance(results, str):
        print(results)

    elif isinstance(results, list):
        for index, result in enumerate(results, start=1):
            print(f"\nSource {index}")

            if isinstance(result, dict):
                print(f"Title: {result.get('title', 'No title')}")
                print(f"URL: {result.get('url', 'No URL')}")
                print(f"Content: {result.get('content', 'No content')}")
            else:
                print(f"Content: {result}")

            print("-" * 60)

    else:
        print(results)

except Exception as e:
    print(f"Web search failed: {e}")