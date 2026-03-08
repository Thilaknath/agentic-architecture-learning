import json

from dotenv import load_dotenv

from src.graph import build_graph
from src.eval.topics import EVAL_TOPICS


def run_eval():
    """Run the blog pipeline on all eval topics with auto-approve, collect scores."""
    load_dotenv()
    graph = build_graph()
    results = []

    for i, topic in enumerate(EVAL_TOPICS, 1):
        print(f"\n{'='*60}")
        print(f"[Eval {i}/{len(EVAL_TOPICS)}] {topic}")
        print("=" * 60)

        initial_state = {
            "topic": topic,
            "search_results": "",
            "outline": "",
            "outline_approved": False,
            "outline_feedback": "",
            "draft": "",
            "review_feedback": "",
            "revision_count": 0,
            "draft_approved": False,
            "draft_feedback": "",
            "judge_scores": "",
            "final_accepted": False,
            "auto_approve": True,
            "status": "",
        }

        try:
            result = graph.invoke(initial_state)
            scores = json.loads(result.get("judge_scores", "{}"))
            results.append({"topic": topic, "scores": scores, "status": result.get("status", "")})
        except Exception as e:
            print(f"[Eval] Error on '{topic}': {e}")
            results.append({"topic": topic, "scores": {}, "status": f"error: {e}"})

    # Print summary table
    print("\n\n" + "=" * 90)
    print("EVAL RESULTS")
    print("=" * 90)
    print(f"{'Topic':<50} {'Acc':>4} {'Clr':>4} {'Cmp':>4} {'Sty':>4} {'All':>4}")
    print("-" * 90)

    overall_scores = []
    for r in results:
        s = r["scores"]
        acc = s.get("accuracy", {}).get("score", "-")
        clr = s.get("clarity", {}).get("score", "-")
        cmp = s.get("completeness", {}).get("score", "-")
        sty = s.get("style", {}).get("score", "-")
        ovr = s.get("overall", "-")
        if isinstance(ovr, (int, float)):
            overall_scores.append(ovr)
        print(f"{r['topic']:<50} {acc:>4} {clr:>4} {cmp:>4} {sty:>4} {ovr:>4}")

    print("-" * 90)
    if overall_scores:
        avg = sum(overall_scores) / len(overall_scores)
        print(f"{'Average':<50} {'':>4} {'':>4} {'':>4} {'':>4} {avg:>4.1f}")
    print("=" * 90)


if __name__ == "__main__":
    run_eval()
