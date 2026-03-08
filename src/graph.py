import os
import re
from datetime import datetime

from langgraph.graph import StateGraph, END

from src.state import BlogState
from src.agents.researcher import research_node
from src.agents.writer import write_node
from src.agents.reviewer import review_node
from src.agents.judge import judge_node

MAX_REVISIONS = 3


# --- Human review nodes ---


def human_review_outline(state: BlogState) -> dict:
    """Let the human approve or reject the outline."""
    if state.get("auto_approve"):
        print("[Human Review] Auto-approving outline.")
        return {"outline_approved": True}

    print("\n" + "=" * 60)
    print("OUTLINE FOR REVIEW")
    print("=" * 60)
    print(state["outline"])
    print("=" * 60)

    choice = input("\nApprove this outline? (y/n): ").strip().lower()
    if choice == "y":
        return {"outline_approved": True}

    feedback = input("Feedback for revision: ").strip()
    return {"outline_approved": False, "outline_feedback": feedback}


def human_review_draft(state: BlogState) -> dict:
    """Let the human approve or reject the draft."""
    if state.get("auto_approve"):
        print("[Human Review] Auto-approving draft.")
        return {"draft_approved": True}

    print("\n" + "=" * 60)
    print("DRAFT FOR REVIEW")
    print("=" * 60)
    print(state["draft"])
    print("=" * 60)
    print(f"\nReviewer feedback:\n{state.get('review_feedback', 'N/A')}")
    print("=" * 60)

    choice = input("\nApprove this draft? (y/n): ").strip().lower()
    if choice == "y":
        return {"draft_approved": True}

    feedback = input("Feedback for revision: ").strip()
    return {"draft_approved": False, "draft_feedback": feedback}


def human_review_final(state: BlogState) -> dict:
    """Let the human accept or reject the final scored draft."""
    if state.get("auto_approve"):
        print("[Human Review] Auto-accepting final draft.")
        return {"final_accepted": True}

    print("\n" + "=" * 60)
    print("FINAL REVIEW — Judge Scores")
    print("=" * 60)
    print(state.get("judge_scores", "No scores available"))
    print("=" * 60)

    choice = input("\nAccept and save this post? (y/n): ").strip().lower()
    if choice == "y":
        return {"final_accepted": True}

    feedback = input("Guidance for rewrite: ").strip()
    return {"final_accepted": False, "draft_feedback": feedback}


# --- Save node ---


def save_node(state: BlogState) -> dict:
    """Write the final draft to output/."""
    os.makedirs("output", exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", state["topic"].lower()).strip("-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"output/{slug}-{timestamp}.md"

    with open(filename, "w") as f:
        f.write(state["draft"])

    print(f"\n[Save] Blog post saved to {filename}")
    return {"status": f"saved:{filename}"}


# --- Routing functions ---


def route_after_outline_review(state: BlogState) -> str:
    if state.get("outline_approved"):
        return "write"
    return "research"


def route_after_draft_review(state: BlogState) -> str:
    if state.get("draft_approved"):
        return "judge"
    if state.get("revision_count", 0) >= MAX_REVISIONS:
        print(f"[Router] Max revisions ({MAX_REVISIONS}) reached, forwarding to judge.")
        return "judge"
    return "write"


def route_after_final_review(state: BlogState) -> str:
    if state.get("final_accepted"):
        return "save"
    return "write"


# --- Revision counter node ---


def increment_revision(state: BlogState) -> dict:
    """Track revision count before re-entering the write node."""
    count = state.get("revision_count", 0) + 1
    print(f"[Revision] Draft revision #{count}")
    return {"revision_count": count}


# --- Graph builder ---


def build_graph() -> StateGraph:
    """Assemble and compile the blog writer workflow."""
    graph = StateGraph(BlogState)

    # Add nodes
    graph.add_node("research", research_node)
    graph.add_node("human_review_outline", human_review_outline)
    graph.add_node("write", write_node)
    graph.add_node("review", review_node)
    graph.add_node("human_review_draft", human_review_draft)
    graph.add_node("judge", judge_node)
    graph.add_node("human_review_final", human_review_final)
    graph.add_node("save", save_node)

    # Linear edges
    graph.set_entry_point("research")
    graph.add_edge("research", "human_review_outline")
    graph.add_edge("write", "review")
    graph.add_edge("review", "human_review_draft")
    graph.add_edge("judge", "human_review_final")
    graph.add_edge("save", END)

    # Conditional edges
    graph.add_conditional_edges(
        "human_review_outline",
        route_after_outline_review,
        {"write": "write", "research": "research"},
    )
    graph.add_conditional_edges(
        "human_review_draft",
        route_after_draft_review,
        {"judge": "judge", "write": "write"},
    )
    graph.add_conditional_edges(
        "human_review_final",
        route_after_final_review,
        {"save": "save", "write": "write"},
    )

    return graph.compile()
