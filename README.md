# AI Blog Writer

A multi-agent blog writing pipeline built with [LangGraph](https://github.com/langchain-ai/langgraph). Given a topic, it researches, outlines, writes, reviews, and scores a technical blog post — with optional human-in-the-loop checkpoints at each stage.

## Architecture

```
Research ──► Outline Review ──► Write ──► AI Review ──► Draft Review ──► Judge ──► Final Review ──► Save
   ▲              │                ▲                        │                                │
   └──── reject ──┘                └──────── reject ────────┘                                │
                                   └─────────────────────── reject ──────────────────────────┘
```

**Agents:**

| Agent | Model | Role |
|-------|-------|------|
| Researcher | GPT-5 (SAP AI Core) | Searches the web and produces a structured outline |
| Writer | GPT-5 (SAP AI Core) | Drafts the blog post from outline + research |
| Reviewer | GPT-5 (SAP AI Core) | Critiques the draft for accuracy, flow, and completeness |
| Judge | Gemini 2.5 Flash | Scores the final draft on a 4-dimension rubric (1-10) |

**Search tools:** Tavily + Perplexity (fallback-tolerant — Perplexity failure is non-fatal).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
```

Required environment variables (see `.env.example`):

- `LANGSMITH_API_KEY` — LangSmith tracing
- `TAVILY_API_KEY` — web search
- `PERPLEXITY_API_KEY` — deep research search
- `GEMINI_API_KEY` — judge scoring

## Usage

Interactive mode (human approves outline, draft, and final):

```bash
python -m src.main --topic "Introduction to WebAssembly"
```

Fully automated:

```bash
python -m src.main --topic "Introduction to WebAssembly" --auto-approve
```

Output is saved to `output/<slug>-<timestamp>.md`.
