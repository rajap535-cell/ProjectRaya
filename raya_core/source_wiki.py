# source_wiki.py
def fetch_wikipedia_summary(query: str) -> str | None:
    try:
        import wikipedia
        wikipedia.set_lang("en")

        def safe_summary(title: str) -> str | None:
            try:
                return wikipedia.summary(title, sentences=3, auto_suggest=False, redirect=True)
            except wikipedia.DisambiguationError:
                return None
            except Exception:
                return None

        # 1. Direct try (no auto_suggest → avoid Lady Gaga issue)
        try:
            return wikipedia.summary(query, sentences=3, auto_suggest=False, redirect=True)
        except wikipedia.DisambiguationError as e:
            candidates = e.options[:8]
        except Exception:
            candidates = wikipedia.search(query, results=8)

        if not candidates:
            return None

        # 2. Preference filter
        prefs = [
            "India", "Indian", "politician", "country", "planet", 
            "science", "astronomy", "Prime Minister", "freedom fighter", "author", "religion"
        ]
        first = None
        for title in candidates:
            s = safe_summary(title)
            if not s:
                continue
            # If preferred keywords match → return immediately
            if any(p.lower() in s.lower() or p.lower() in title.lower() for p in prefs):
                return s
            if not first:
                first = s

        # 3. Return first valid summary as fallback
        return first
    except Exception:
        return None
