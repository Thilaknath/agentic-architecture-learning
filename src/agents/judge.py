import json

from langsmith import traceable

from src.llm import get_gemini_client
from src.state import BlogState

JUDGE_RUBRIC = """Score this blog post on 4 dimensions (1-10 each):

1. **Accuracy** — Are technical claims correct? Are code examples valid?
2. **Clarity** — Is the writing clear, well-structured, and easy to follow?
3. **Completeness** — Does the post thoroughly cover the topic?
4. **Style** — Is the tone engaging? Is markdown formatting used well?

For each dimension, provide:
- A score (1-10)
- A one-sentence justification

Respond in this exact JSON format:
{
  "accuracy": {"score": N, "reason": "..."},
  "clarity": {"score": N, "reason": "..."},
  "completeness": {"score": N, "reason": "..."},
  "style": {"score": N, "reason": "..."},
  "overall": N,
  "summary": "One-paragraph overall assessment"
}
"""


@traceable(run_type="llm", name="gemini_judge")
def _call_gemini(prompt: str) -> str:
    """Call Gemini and return raw text. Traced as an LLM call."""
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def judge_node(state: BlogState) -> dict:
    """Score the draft using Gemini as an LLM judge."""
    draft = state["draft"]
    topic = state["topic"]

    prompt = f"""You are an expert technical content judge.

Topic: {topic}

Blog Post:
{draft}

{JUDGE_RUBRIC}

Return ONLY valid JSON, no other text."""

    print("[Judge] Scoring with Gemini...")
    raw = _call_gemini(prompt).strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    # Validate JSON
    try:
        scores = json.loads(raw)
        print(f"[Judge] Overall score: {scores.get('overall', 'N/A')}/10")
    except json.JSONDecodeError:
        scores = {"error": "Failed to parse judge response", "raw": raw}
        print("[Judge] Warning: could not parse scores as JSON")

    return {"judge_scores": json.dumps(scores, indent=2)}
