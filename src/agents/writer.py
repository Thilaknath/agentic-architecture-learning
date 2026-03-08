from src.llm import get_gpt
from src.state import BlogState


def write_node(state: BlogState) -> dict:
    """Generate a blog post from the outline and search results."""
    topic = state["topic"]
    outline = state["outline"]
    search_results = state["search_results"]
    review_feedback = state.get("review_feedback", "")
    draft_feedback = state.get("draft_feedback", "")

    prompt = f"""You are a technical blog writer. Write a comprehensive, engaging blog post
based on the outline and research below.

Topic: {topic}

Outline:
{outline}

Research:
{search_results}

Requirements:
- Write in a clear, professional yet approachable tone
- Include code examples where relevant (use markdown code blocks)
- Target audience: developers with intermediate experience
- Length: 1500-2500 words
- Use markdown formatting (headers, lists, code blocks)
"""
    if review_feedback:
        prompt += f"\n\nReviewer feedback to address:\n{review_feedback}"
    if draft_feedback:
        prompt += f"\n\nHuman feedback to address:\n{draft_feedback}"

    print("[Writer] Generating blog post...")
    llm = get_gpt()
    response = llm.invoke(prompt)

    return {
        "draft": response.content,
        "review_feedback": "",
        "draft_approved": False,
        "draft_feedback": "",
    }
