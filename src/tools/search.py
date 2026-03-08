import os

from langsmith import traceable
from tavily import TavilyClient

from src.llm import get_perplexity_client


@traceable(run_type="tool", name="tavily_search")
def tavily_search(query: str, max_results: int = 5) -> str:
    """Search using Tavily and return formatted results."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query, max_results=max_results)
    results = []
    for r in response.get("results", []):
        results.append(f"**{r['title']}**\n{r['url']}\n{r['content']}\n")
    return "\n".join(results) if results else "No results found."


@traceable(run_type="llm", name="perplexity_search")
def perplexity_search(query: str) -> str:
    """Search using Perplexity sonar-pro model."""
    client = get_perplexity_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": "You are a research assistant. Provide detailed, factual information."},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content


def search_topic(topic: str) -> str:
    """Run both search tools and combine results. Perplexity failure is non-fatal."""
    tavily_results = tavily_search(f"{topic} technical overview")

    try:
        perplexity_results = perplexity_search(
            f"Give a comprehensive technical overview of: {topic}"
        )
    except Exception as e:
        print(f"[Search] Perplexity unavailable ({e}), using Tavily only.")
        perplexity_results = ""

    combined = f"=== Tavily Search Results ===\n{tavily_results}"
    if perplexity_results:
        combined += f"\n\n=== Perplexity Research ===\n{perplexity_results}"
    return combined
