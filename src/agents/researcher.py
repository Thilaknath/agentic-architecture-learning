from src.llm import get_gpt
from src.state import BlogState
from src.tools.search import search_topic


def research_node(state: BlogState) -> dict:
    """Search the topic and generate a structured outline."""
    topic = state["topic"]
    feedback = state.get("outline_feedback", "")

    print(f"\n[Research] Searching for: {topic}")
    search_results = search_topic(topic)

    prompt = f"""You are a technical blog researcher. Based on the search results below,
create a structured outline for a technical blog post about: {topic}

The outline should include:
- A compelling title
- 4-6 main sections with bullet points for key ideas
- Suggested code examples or diagrams where appropriate
- A conclusion section

Search Results:
{search_results}
"""
    if feedback:
        prompt += f"\n\nPrevious feedback to address:\n{feedback}"

    print("[Research] Generating outline...")
    llm = get_gpt()
    response = llm.invoke(prompt)

    return {
        "search_results": search_results,
        "outline": response.content,
        "outline_approved": False,
        "outline_feedback": "",
    }
