import re
from typing import List, Dict, Tuple, Optional

from raya_core.cache import cache_get
from raya_core.custom_db import query_local_db
from raya_core.source_wiki import fetch_wikipedia_summary
from raya_core.source_news_topic import search_topic_news
from raya_core.source_arxiv import search_arxiv
from raya_core import qa_engine
from aggregator import aggregate


Candidate = Tuple[str, str, float, Optional[dict]]  # (source, text, confidence, meta)

# Normalize input query
def _normalize(q: str) -> str:
    q = (q or "").strip().lower()
    q = re.sub(r"[^\w\s]", "", q)
    q = re.sub(r"\s+", " ", q)
    return q

# Check cache (QA cache or global)
def _lookup_cache(q: str) -> Optional[Candidate]:
    q_norm = _normalize(q)

    # 1. Global/local cache first
    try:
        cached = cache_get(q_norm, "fact")
        if cached:
            if isinstance(cached, dict):
                return (
                    "cache",
                    cached.get("summary", cached.get("answer", "")),
                    0.95,
                    {"sources": cached.get("sources")}
                )
            elif isinstance(cached, str):
                return ("cache", cached, 0.95, None)
    except Exception as e:
        print("[ERROR] Global cache check failed:", e)

    # 2. QA engine fallback
    try:
        res = qa_engine.answer_question(q)
        if res and getattr(res, "answer", None):
            return ("qa-cache", res.answer, 0.85, {"sources": getattr(res, "sources", None)})
    except Exception as e:
        print("[ERROR] QA engine cache check failed:", e)

    return None


# Collect all candidate answers from sources
def _collect_candidates(user_text: str, db_file: str, intents: List[str]) -> List[Candidate]:
    candidates: List[Candidate] = []
    q = user_text

    # 1. Cache
    cache_cand = _lookup_cache(q)
    if cache_cand:
        candidates.append(cache_cand)

    # 2. Local DB
    try:
        local = query_local_db(db_file, q)
        if local:
            candidates.append(("custom_db", local, 0.9, None))
    except Exception as e:
        print("[ERROR] Local DB query failed:", e)

    # 3. Wikipedia
    try:
        wiki = fetch_wikipedia_summary(q)
        if wiki:
            print("[DEBUG] Wiki result:", wiki)
            candidates.append(("wikipedia", wiki, 0.7, None))
    except Exception as e:
        print("[ERROR] Wikipedia fetch failed:", e)

    # 4. News (triggered by intent or keywords)
    try:
        if "news" in intents or any(k in user_text.lower() for k in ("latest", "recent", "today", "breaking")):
            news_hits = search_topic_news(q, max_items=6)
            if news_hits:
                print("[DEBUG] News intent triggered.")
                candidates.append(("news", " • " + "\n • ".join(news_hits), 0.55, None))
    except Exception as e:
        print("[ERROR] News search failed:", e)

    # 5. ArXiv
    try:
        if "research" in intents or any(k in user_text.lower() for k in ("paper", "arxiv", "study", "research")):
            ax = search_arxiv(q, max_results=3)
            if ax:
                candidates.append(("arxiv", ax, 0.5, None))
    except Exception as e:
        print("[ERROR] ArXiv search failed:", e)

 # 6. QA engine
    try:
        qa_res = qa_engine.answer_question(q)
        if qa_res:
            # Safely extract fields, no hard dependency on .sources
            answer = getattr(qa_res, "answer", None) or getattr(qa_res, "text", None)
            if answer:
                print("[DEBUG] QA Engine returned:", answer)
                conf = getattr(qa_res, "confidence", 0.7)
                candidates.append((
                    "qa",
                    answer,
                    float(conf),
                    {
                        "title": getattr(qa_res, "source_title", None),
                        "url": getattr(qa_res, "source_url", None)
                    }
                ))
    except Exception as e:
        print("[ERROR] QA engine execution failed:", e)

    return candidates   # make sure this stays at the end of the function

# Select the best answer based on ranking strategy
def _score_and_select(candidates: List[Candidate], user_text: str) -> str:
    if not candidates:
        return None, []

    # If explicit NEWS intent, prefer news over QA/Wiki
    if any(src == "news" for src, _, _, _ in candidates):
        news_candidates = [c for c in candidates if c[0] == "news"]
        best = news_candidates[0]
        extras = [c for c in candidates if c is not best]
        return best, extras

    # Score each candidate: confidence * length of answer
    scored = []
    for src, ans, conf, meta in candidates:
        length_factor = min(len(ans) / 200.0, 3.0)  # cap length advantage
        score = (conf or 0.5) * (len(ans) / 100.0)
        scored.append((src, ans, conf, meta, score))
    scored.sort(key=lambda t: t[4], reverse=True)
    # Pick best by score
    best = scored[0]
    extras = scored [1:]

    return best, extras

    # Format output nicely
    src, ans, conf, meta, score = best
    if src == "cache":
        sources = meta.get("sources") if isinstance(meta, dict) else None
        if sources:
            return ans + f" — source: cache ({', '.join(sources)})"
        return ans + " — source: cache"
    elif src == "wikipedia":
        return ans + " — source: Wikipedia"
    elif src == "qa":
        title = meta.get("title") if isinstance(meta, dict) else None
        return ans + (f" — source: {title}" if title else " — source: QA")
    elif src in ("news", "arxiv"):
        return ans + f" — source: {src}"

    # Fallback
    return ans + f" — source: {src}"

# Entry point for the engine pipeline
def run_pipeline(user_text, db_file, intents):
    candidates = _collect_candidates(user_text, db_file, intents)
    best, extras = _score_and_select(candidates, user_text)

    # Map for aggregator: (src, text)
    if best:
        best_pair = (best[0], best[1])
        extras_pairs = [(src, ans) for src, ans, *_ in extras]
    else:
        best_pair, extras_pairs = None, []

    final = aggregate(best_pair, extras_pairs)
    metadata = {"candidates": [(c[0], c[2]) for c in candidates]}
    return final, metadata
