from src.llm import get_gpt
from src.state import BlogState


def review_node(state: BlogState) -> dict:
    """Review the draft for accuracy, flow, and completeness."""
    draft = state["draft"]
    topic = state["topic"]
    outline = state["outline"]

    prompt = f"""You are a technical blog reviewer. Review this blog post draft critically.

Topic: {topic}
Original Outline:
{outline}

Draft:
{draft}

Evaluate on:
1. Technical accuracy — are claims correct and well-supported?
2. Flow and readability — does it read naturally? Are transitions smooth?
3. Completeness — does it cover the outline topics adequately?
4. Code examples — are they correct, relevant, and well-explained?

Provide specific, actionable feedback. If the draft is strong, say so briefly and note
any minor improvements. If there are significant issues, list them clearly."""

    print("[Reviewer] Reviewing draft...")
    llm = get_gpt()
    response = llm.invoke(prompt)

    return {"review_feedback": response.content}
