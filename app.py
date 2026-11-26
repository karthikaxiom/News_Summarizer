import streamlit as st
from utils import (
    analyze_sentiment,
    compare_sentiments,
    generate_tts,
    get_news_articles,
)

st.set_page_config(page_title="News Summarizer", page_icon="📰", layout="wide")
st.title("News Summarization and Sentiment Analysis")
st.write("Enter a company name to fetch recent news and compare its sentiment.")

company_name = st.text_input("Enter a company name:", placeholder="e.g. Apple")

if company_name.strip():
    try:
        news = get_news_articles(company_name.strip())
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if not news:
        st.warning("No news articles were found. Try another company name.")
        st.stop()

    st.subheader(f"News Articles about {company_name}")
    for i, article in enumerate(news, 1):
        sentiment = analyze_sentiment(article["summary"])
        st.markdown(f"**{i}. {article['title']}**")
        st.write(f"Sentiment: {sentiment}")
        st.write(article["summary"])
        if article["url"]:
            st.markdown(f"[Read Full Article]({article['url']})")
        st.divider()

    sentiment_summary = compare_sentiments(news, company_name.strip())

    st.subheader(f"Comparative Sentiment Analysis for {company_name}")
    st.write(f"Sentiment Distribution: {sentiment_summary['Sentiment Distribution']}")
    st.write(f"Dominant Sentiment: {sentiment_summary['Dominant Sentiment']}")

    st.markdown("### Key Insights")
    for insight in sentiment_summary["Insights"]:
        st.write(f"- {insight}")

    if st.button("Play audio for Insights"):
        final_sentiment = " ".join(sentiment_summary["Insights"])
        with st.spinner("Generating audio..."):
            audio_language = generate_tts(final_sentiment, "final_sentiment.mp3")

        if audio_language:
            st.audio("final_sentiment.mp3", format="audio/mp3")
            if audio_language == "hi":
                st.success("Hindi audio generated successfully!")
            else:
                st.warning(
                    "Hindi translation is temporarily unavailable. "
                    "English audio has been generated instead."
                )
        else:
            st.error("Audio generation failed. Please try again.")
