from typing import TypedDict


class BlogState(TypedDict):
    topic: str
    search_results: str
    outline: str
    outline_approved: bool
    outline_feedback: str
    draft: str
    review_feedback: str
    revision_count: int
    draft_approved: bool
    draft_feedback: str
    judge_scores: str  # JSON string with scores + reasoning
    final_accepted: bool
    auto_approve: bool
    status: str
