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

    if st.button("Generate Hindi audio for insights"):
        with st.spinner("Translating insights and generating Hindi audio..."):
            try:
                final_insights = " ".join(sentiment_summary["Insights"])
                st.session_state["news_summarizer_audio"] = generate_tts(final_insights)
                st.session_state["news_summarizer_audio_error"] = None
            except RuntimeError as exc:
                st.session_state["news_summarizer_audio"] = None
                st.session_state["news_summarizer_audio_error"] = str(exc)

    if st.session_state.get("news_summarizer_audio_error"):
        st.error(st.session_state["news_summarizer_audio_error"])

    if st.session_state.get("news_summarizer_audio"):
        st.audio(st.session_state["news_summarizer_audio"], format="audio/mp3")
        st.success("Hindi audio is ready. Press play to listen.")
