# qa_engine.py - Improved: prefer cache, careful wikipedia selection, robust fallbacks
import os, re, json, difflib, feedparser, requests, wikipedia
from dataclasses import dataclass
from typing import Optional
# try to import search_online from engine (may be relative)
try:
    from engine import search_online
except Exception:
    # best-effort fallback: simple DuckDuckGo inline
    def search_online(q):
        try:
            url = f"https://api.duckduckgo.com/?q={q}&format=json&no_redirect=1&no_html=1"
            r = requests.get(url, timeout=6)
            data = r.json()
            return data.get("AbstractText") or data.get("Heading") or None
        except Exception:
            return None

wikipedia.set_lang("en")
DEBUG = os.getenv("RAYA_DEBUG", "0") == "1"

CACHE_FILE = os.path.join(os.path.dirname(__file__), "final_raya_cache.json")
QA_CACHE = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            RAW_K = data.get("knowledge", data)
            QA_CACHE = {k.lower().strip(): v for k, v in RAW_K.items()}
    except Exception:
        QA_CACHE = {}

@dataclass
class QAResult:
    answer: Optional[str]
    source_type: str

def normalize_query(q):
    q = (q or "").lower().strip()
    q = re.sub(r'^(what is|who is|define|tell me about|explain|how old is)\s+', '', q)
    q = re.sub(r'^(a|an|the)\s+', '', q)
    return q.strip()

def search_cache(query):
    q = query.lower().strip()
    if q in QA_CACHE:
        entry = QA_CACHE[q]
        return entry.get("summary") or entry.get("answer")
    keys = list(QA_CACHE.keys())
    match = difflib.get_close_matches(q, keys, n=1, cutoff=0.7)
    if match:
        entry = QA_CACHE[match[0]]
        return entry.get("summary") or entry.get("answer")
    return None

def fetch_topic_news(topic, max_results=10):
    feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ]
    all_entries, results = [], []
    for feed_url in feeds:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries:
                all_entries.append(entry)
                if topic and topic.lower() in getattr(entry, "title", "").lower():
                    results.append(f"- {entry.title}")
        except Exception:
            continue
    if not results:
        results.extend(f"- {getattr(e,'title','')}" for e in all_entries[:max_results])
    return results[:max_results]

def wiki_best_summary(query, max_pages=3):
    try:
        titles = wikipedia.search(query, results=max_pages)
    except Exception:
        titles = []
    for t in titles:
        if t and (t.lower() == query.lower() or query.lower() in t.lower()):
            try:
                return wikipedia.summary(t, sentences=3, auto_suggest=False), t
            except Exception:
                continue
    if titles:
        for t in titles:
            try:
                return wikipedia.summary(t, sentences=3, auto_suggest=False), t
            except Exception:
                continue
    try:
        return wikipedia.summary(query, sentences=3, auto_suggest=False), None
    except Exception:
        return None, None

def answer_question(question: str):
    qnorm = normalize_query(question)
    if "news" in qnorm:
        topic = qnorm.replace("news", "").strip()
        headlines = fetch_topic_news(topic)
        if headlines:
            return QAResult("\n".join(headlines), "news")
        return QAResult(f"Sorry, I couldn't find recent news about {topic}.", "news")
    cache_ans = search_cache(qnorm)
    if cache_ans:
        if DEBUG: print("[QA] from cache")
        return QAResult(cache_ans, "cache")
    summary, title = wiki_best_summary(question, max_pages=5)
    if summary:
        if DEBUG: print("[QA] from wiki", title)
        return QAResult(summary, "wiki")
    try:
        web = search_online(question)
    except Exception:
        web = None
    if web:
        if DEBUG: print("[QA] from web")
        return QAResult(web, "online")
    try:
        from .fallback import graceful_fallback
        fb = graceful_fallback(question)
    except Exception:
        fb = None
    return QAResult(fb or "Sorry, I couldn't find an answer.", "fallback")

def get_answer_string(res: QAResult) -> str:
    dbg = f" [source:{res.source_type}]" if DEBUG else ""
    return f"RAYA SAY: {res.answer}{dbg}"
