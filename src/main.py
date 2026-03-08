import argparse
import json

from dotenv import load_dotenv

from src.graph import build_graph


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="AI Blog Writer Agent")
    parser.add_argument("--topic", required=True, help="Blog post topic")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip human review checkpoints",
    )
    args = parser.parse_args()

    initial_state = {
        "topic": args.topic,
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
        "auto_approve": args.auto_approve,
        "status": "",
    }

    print(f"Starting blog generation for: {args.topic}")
    print(f"Auto-approve: {args.auto_approve}\n")

    graph = build_graph()
    result = graph.invoke(initial_state)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Topic: {result['topic']}")
    print(f"Status: {result.get('status', 'unknown')}")
    if result.get("judge_scores"):
        try:
            scores = json.loads(result["judge_scores"])
            print(f"Overall score: {scores.get('overall', 'N/A')}/10")
            for dim in ("accuracy", "clarity", "completeness", "style"):
                if dim in scores:
                    print(f"  {dim}: {scores[dim]['score']}/10 — {scores[dim]['reason']}")
        except (json.JSONDecodeError, KeyError):
            print(f"Scores: {result['judge_scores']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
