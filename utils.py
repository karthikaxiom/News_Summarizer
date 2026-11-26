import os
from collections import Counter

import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
from textblob import TextBlob


def get_news_articles(query):
    """
    Fetch up to 10 news articles using NewsAPI.
    Store NEWS_API_KEY in the deployment's environment/secrets.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NEWS_API_KEY is not configured. Add it to your Hugging Face Space "
            "Settings > Variables and secrets."
        )

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "apiKey": api_key, "pageSize": 10, "language": "en"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise RuntimeError(data.get("message", "NewsAPI returned an error."))

        articles = []
        for item in data.get("articles", [])[:10]:
            articles.append({
                "title": item.get("title") or "Untitled article",
                "summary": item.get("description") or "No summary available",
                "url": item.get("url") or "",
            })
        return articles

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Unable to fetch news from NewsAPI: {exc}") from exc


def analyze_sentiment(text):
    """Classify text as Positive, Negative, or Neutral using TextBlob."""
    polarity = TextBlob(text or "").sentiment.polarity
    if polarity > 0:
        return "Positive"
    if polarity < 0:
        return "Negative"
    return "Neutral"


def compare_sentiments(articles, company_name):
    """Compare article sentiment and produce brief rule-based insights."""
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    sentiment_groups = {"Positive": [], "Negative": [], "Neutral": []}

    for article in articles:
        sentiment = analyze_sentiment(article.get("summary", ""))
        sentiment_counts[sentiment] += 1
        sentiment_groups[sentiment].append(article)

    dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)

    insights = []
    if sentiment_counts["Positive"] > sentiment_counts["Negative"]:
        insights.append(
            f"{company_name}'s news coverage is mostly positive, reflecting stronger positive than negative reporting."
        )
    elif sentiment_counts["Negative"] > sentiment_counts["Positive"]:
        insights.append(
            f"{company_name} has more negative than positive news coverage, indicating potential challenges or concerns."
        )
    else:
        insights.append(
            f"{company_name}'s news coverage has equal positive and negative article counts."
        )

    if sentiment_groups["Positive"] and sentiment_groups["Negative"]:
        positive_title = sentiment_groups["Positive"][0]["title"]
        negative_title = sentiment_groups["Negative"][0]["title"]
        insights.append(
            f"Example contrast: '{positive_title}' is classified as positive, while "
            f"'{negative_title}' is classified as negative."
        )

    return {
        "Sentiment Distribution": sentiment_counts,
        "Dominant Sentiment": dominant_sentiment,
        "Insights": insights,
    }


def generate_tts(text, filename="final_sentiment.mp3"):
    """
    Generate Hindi speech when translation is available.
    If Google translation is rate-limited or unavailable, generate English speech.
    Returns the language code ('hi' or 'en'), or None if audio generation fails.
    """
    if not text or not text.strip():
        return None

    speech_text = text
    language = "hi"

    try:
        speech_text = GoogleTranslator(source="auto", target="hi").translate(text)
        if not speech_text:
            raise ValueError("Translator returned empty text.")
    except Exception as exc:
        # Translation is an optional enhancement; do not let it break the app.
        print(f"Hindi translation unavailable; using English audio. Details: {exc}")
        speech_text = text
        language = "en"

    try:
        gTTS(text=speech_text, lang=language).save(filename)
        return language
    except Exception as exc:
        print(f"Text-to-speech generation failed: {exc}")
        return None
