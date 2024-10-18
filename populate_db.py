import apsw
import requests


def get_top_articles():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    articles = []

    if response.status_code == 200:
        for article_id in response.json()[:10]:
            article = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{article_id}.json"
            )

            article_data = article.json()

            if "url" not in article_data:
                continue
            article_url = article_data["url"].lstrip("https://").lstrip("http://")
            scraped_article = requests.get(f"https://r.jina.ai/{article_url}")

            article_data["markdown"] = scraped_article.text

            articles.append(article_data)
    return articles


def populate_db():
    connection = apsw.Connection("top_hn_articles.db")

    connection.execute(
        "CREATE TABLE IF NOT EXISTS top_articles (id INTEGER PRIMARY KEY, title TEXT, url TEXT, score INTEGER, time TIMESTAMP, markdown TEXT)"
    )

    top_articles = get_top_articles()

    for article in top_articles:
        connection.execute(
            "INSERT INTO top_articles (id, title, url, score, time, markdown) VALUES (?, ?, ?, ?, ?, ?)",
            (
                article["id"],
                article["title"],
                article["url"],
                article["score"],
                article["time"],
                article["markdown"],
            ),
        )
