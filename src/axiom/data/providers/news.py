"""Financial and macroeconomic news provider using verified RSS feeds."""
import urllib.parse
from typing import List
import feedparser
from axiom.data.schemas import NewsArticle
from axiom.data.cache import DiskCache

class NewsProvider:
    def __init__(self, cache_ttl_hours: float = 2.0):
        self.cache = DiskCache(default_ttl_hours=cache_ttl_hours)

    def get_news(self, query: str, limit: int = 10) -> List[NewsArticle]:
        cache_key = f"news_{query}_{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            return [NewsArticle.model_validate(x) for x in cached]

        encoded_q = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en"

        articles = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                published = entry.get("published", "")
                summary = entry.get("summary", "")
                
                # Extract publisher if formatted like "Title - Publisher"
                pub_name = "Financial Media"
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0]
                    pub_name = parts[1]

                articles.append(NewsArticle(
                    title=title,
                    source_name=pub_name,
                    url=link,
                    published_date=published,
                    summary=summary[:200]
                ))
        except Exception:
            pass

        if articles:
            self.cache.set(cache_key, [a.model_dump() for a in articles])

        return articles
