import streamlit as st
from utils import get_news_articles, analyze_sentiment, compare_sentiments, generate_tts

# Original News Summarizer interface
st.title("News Summarization and Sentiment Analysis")
st.write("Enter a company name to get the latest news and sentiment analysis.")

company_name = st.text_input("Enter a company name:")

if company_name:
    st.subheader(f"News Articles about {company_name}:")
    try:
        news = get_news_articles(company_name)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if news:
        for i, article in enumerate(news, 1):
            sentiment = analyze_sentiment(article["summary"])
            st.write(f"{i}. **{article['title']}**")
            st.write(f"   Sentiment: {sentiment}")
            st.write(f"   {article['summary']}")
            if article.get("url"):
                st.write(f"   [Read Full Article]({article['url']})")
            st.markdown("---")

        sentiment_summary = compare_sentiments(news, company_name)

        st.subheader(f"Comparative Sentiment Analysis for {company_name}")
        st.write(f"Sentiment Distribution: {sentiment_summary['Sentiment Distribution']}")
        st.write(f"Dominant Sentiment: {sentiment_summary['Dominant Sentiment']}")

        st.write("### Key Insights:")
        for insight in sentiment_summary["Insights"]:
            st.write(f"- {insight}")

        if st.button("Play audio for Insights"):
            final_sentiment = " ".join(sentiment_summary["Insights"])
            try:
                with st.spinner("Generating Hindi audio..."):
                    audio_bytes = generate_tts(final_sentiment)
                st.audio(audio_bytes, format="audio/mp3")
                st.success("Hindi audio generated successfully!")
            except RuntimeError as exc:
                st.error(str(exc))
    else:
        st.error("No news articles found.")
