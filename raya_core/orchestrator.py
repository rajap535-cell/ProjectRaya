import re
from typing import Optional
from config import ENGINE_ORDER, WIKI_SENTENCES
from raya_core.cache import load_cache, save_cache

from .base import EngineResult
from .source_wiki import fetch_wikipedia_summary
from .local_sql import query_local_db
from source_news_topic import search_topic_news
from raya_core.engine import format_answer

# ✅ Import the real QA engine
from raya_core.qa_engine import answer_question


# Wrap QAResult -> EngineResult
def qa_wrapper(query: str) -> Optional[EngineResult]:
    qa_res = answer_question(query)
    if qa_res and (qa_res.answer or qa_res.snippet):
        ans = format_answer(qa_res)
        return EngineResult(
            source="qa",
            text=qa_res.answer or qa_res.snippet or "",
            confidence=qa_res.confidence,
            meta={
                "title": qa_res.source_title,
                "url": qa_res.source_url,
                "snippet": qa_res.snippet,
            },
        )
    return None


# Engines map
engines = {
    "qa": qa_wrapper,  # ✅ always use this
    "local": lambda q: query_local_db(q),
    "wikipedia": lambda q: fetch_wikipedia_summary(q, sentences=WIKI_SENTENCES),
    "news": lambda q: EngineResult(
        source="news",
        text="\n".join(search_topic_news(q)),
        confidence=0.75,
    ),
}

# Optional LLM
try:
    from raya_core.local_llm import ask_llm
    engines["llm"] = lambda q: ask_llm(q)
except ImportError:
    pass


# Load persistent cache
_CACHE = load_cache()


def _cache_key(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    return " ".join(q.split())


def ask_raya(query: str) -> EngineResult:
    """Route query through engines in order, with cache and fallback."""
    key = _cache_key(query)

    # 1. Check cache first
    if key in _CACHE:
        cached = _CACHE[key]
        return EngineResult(
            source=cached.get("source", "cache"),
            text=cached.get("text", ""),
            confidence=cached.get("confidence", 0.6),
            meta={**cached.get("meta", {}), "cache": True},
        )

    # 2. Run engines in order
    for name in ENGINE_ORDER:
        fn = engines.get(name)
        if not fn:
            continue
        try:
            res: Optional[EngineResult] = fn(query)
            if res and res.text:
                # write-through cache
                _CACHE[key] = {
                    "source": res.source,
                    "text": res.text,
                    "confidence": res.confidence,
                    "meta": res.meta or {},
                }
                save_cache(_CACHE)
                return res
        except Exception:
            continue

    # 3. Absolute fallback
    return EngineResult(
        source="fallback",
        text="RAYA SAY: Sorry, I couldn't find that right now.",
        confidence=0.2,
    )
