import os

from gen_ai_hub.proxy.langchain import ChatOpenAI
from gen_ai_hub.proxy.core import get_proxy_client
from google import genai
import openai

# Module-level cached clients
_proxy_client = None
_gpt = None
_gemini_client = None
_perplexity_client = None


def _get_proxy_client():
    global _proxy_client
    if _proxy_client is None:
        _proxy_client = get_proxy_client(resource_group="default")
    return _proxy_client


def get_gpt() -> ChatOpenAI:
    """GPT-5 via SAP AI Core proxy."""
    global _gpt
    if _gpt is None:
        _gpt = ChatOpenAI(
            proxy_model_name="gpt-5",
            proxy_client=_get_proxy_client(),
            temperature=0.7,
        )
    return _gpt


def get_gemini_client() -> genai.Client:
    """Gemini client for judge scoring."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _gemini_client


def get_perplexity_client() -> openai.OpenAI:
    """Perplexity via OpenAI-compatible API."""
    global _perplexity_client
    if _perplexity_client is None:
        _perplexity_client = openai.OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=os.getenv("PERPLEXITY_API_KEY"),
        )
    return _perplexity_client
