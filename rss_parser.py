import feedparser
import json

def parse_rss(url):
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return news_items

def load_rss_sources(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка при загрузке RSS источников: {e}")
        return []  # Этот return должен быть на том же уровне отступа, что и try/except

def get_all_news(sources):
    all_news = []
    for url in sources:
        news_items = parse_rss(url)
        all_news.extend(news_items)  # Этот отступ должен быть на одном уровне с предыдущей строкой
    return all_news

