# app.py
import streamlit as st
import requests

#API_BASE_URL = "https://phill2001-news-fetcher.hf.space"
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("News Analysis & Summarization")
    
    # Fetch RSS Links
    company = st.sidebar.text_input("Enter company name", "Tesla")
    if st.sidebar.button("Fetch News Links"):
        response = requests.post(f"{API_BASE_URL}/fetch-links", json={"company": company})
        if response.status_code == 200:
            data = response.json()
            st.sidebar.subheader("Fetched News Links:")
            for link in data["links"]:
                st.sidebar.write(f"[{link['title']}]({link['url']})")
            st.session_state.rss_links = [link["url"] for link in data["links"]]
        else:
            st.sidebar.error(f"Error: {response.json()['detail']}")
    
    # Manual Link Input
    st.subheader("Manual Link Input")
    manual_links = [st.text_input(f"Enter Link {i+1}", "") for i in range(10)]
    manual_links = [link for link in manual_links if link.strip()]
    
    if len(manual_links) < 2:
        st.warning("At least 2 links are required.")
    
    if st.button("Analyze News"):
        with st.spinner("Analyzing news..."):
            response = requests.post(f"{API_BASE_URL}/analyze-news", json={"links": manual_links})
            if response.status_code == 200:
                data = response.json()
                st.subheader("Summary")
                st.write(data["summary"])
                if "audio" in data:
                    try:
                        audio_bytes = bytes.fromhex(data["audio"])
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("Audio should be playing now!")  # Debugging
                    except Exception as e:
                        st.error(f"Failed to play audio: {e}")  # Debugging

                
                st.subheader("Analysis Results")
                for i, article in enumerate(data["articles"], 1):
                    st.write(f"**Article {i}: {article['title']}**")
                    st.write(f"**Topic:** {article['topic']}")
                    st.text_area(f"Article {i} Content", article["content"], height=300, key=f"article_{i}_content")
                    st.write(f"Sentiment: {article['sentiment']}")
                    st.write("---")
                
                st.subheader("Extraction Method Counts")
                st.write(f"Articles extracted with BeautifulSoup: {data['extraction_counts']['beautifulsoup']}")
                st.write(f"Articles extracted with Newspaper3k: {data['extraction_counts']['newspaper3k']}")
            else:
                st.error(f"Error: {response.json()['detail']}")

if __name__ == "__main__":
    main()
