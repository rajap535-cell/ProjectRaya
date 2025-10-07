#source_news.py
from bs4 import BeautifulSoup
import requests
import feedparser

def get_bbc_headlines():
    url = "https://www.bbc.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = [tag.get_text(strip=True) for tag in soup.find_all('h2') if tag.get_text(strip=True)]
    return headlines[:10]

def get_cnn_headlines():
    url = "http://edition.cnn.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = []
        for span in soup.find_all("span", class_="container__headline-text"):
            text = span.get_text(strip=True)
            if text and 4 <= len(text.split()) <= 12 and text[0].isupper() and "," not in text:
                headlines.append(text)
        return headlines[:10]
    except:
        return None

def get_ndtv_headlines():
    url = "https://feeds.feedburner.com/ndtvnews-top-stories"
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries[:10]]

def get_aljazeera_headlines():
    url = "https://aljazeera.com/xml/rss/all.xml"
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries[:10]]
