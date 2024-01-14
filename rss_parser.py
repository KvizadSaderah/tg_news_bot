import feedparser
import json
import logging

logger = logging.getLogger(__name__)

def parse_rss(url):
    try:
        feed = feedparser.parse(url)
        logger.info(f"Количество записей в ленте: {len(feed.entries)}")
        if len(feed.entries) == 0:
            logger.info(f"Содержимое feed.entries: {feed.entries}")
        news_items = []
        for entry in feed.entries:
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published
            })
        return news_items
    except Exception as e:
        logger.error(f"Ошибка при обработке RSS-канала {url}: {e}")
        return []


def load_rss_sources(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Ошибка при загрузке RSS источников: {e}")
        return []

def get_all_news(sources):
    all_news = []
    if not isinstance(sources, dict):
        logger.error(f"Ожидался словарь, получен {type(sources)}")
        return all_news

    for name, url in sources.items():
        logger.info(f"Обработка RSS-канала: {name} ({url})")
        news_items = parse_rss(url)
        logger.info(f"Получено {len(news_items)} новостей от {name}")
        all_news.extend(news_items)
    return all_news

