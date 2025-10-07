import json
import os

KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "final_raya_cache.json")

def load_knowledge_cache():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

from source_wiki import fetch_wikipedia_summary

def graceful_fallback(user_text: str) -> str:
    # try wikipedia first
    wiki_ans = fetch_wikipedia_summary(user_text)
    if wiki_ans:
        return f"RAYA: {wiki_ans}"

    # fallback to static knowledge
    knowledge = load_knowledge_cache()
    q = user_text.strip().lower()
    if q in knowledge:
        return f"RAYA: {knowledge[q]}"
    else:
        return f"RAYA: Sorry, I couldn’t find anything on '{user_text}'. Try rephrasing."
