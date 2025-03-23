**News Summarization and Text-to-Speech Application
**
This project is a web-based application that extracts news articles related to a given company, performs sentiment analysis, conducts comparative sentiment analysis across articles, and generates a Hindi text-to-speech (TTS) output. The application uses a Streamlit frontend and a FastAPI backend, deployed on Hugging Face Spaces.


Objective

Develop a tool that:
Extracts key details from at least 10 news articles.
Analyzes sentiment (positive, negative, neutral).
Provides comparative insights on news coverage.
Converts summaries to Hindi audio.
Offers a user-friendly interface and API-driven communication.

news-summarization-app/
├── app.py          # Streamlit frontend
├── api.py          # FastAPI backend
├── utils.py        # Utility functions for extraction, analysis, and TTS
├── requirements.txt # Dependencies
├── README.md       # Documentation (this file)



Deployment
Hugging Face Spaces Link: https://huggingface.co/spaces/Phill2001/News_fetcher
GitHub Repository: https://github.com/<your-username>/news-summarization-app (Update with actual link)
Run the Backend (FastAPI):
python api.py
Run the Frontend (Streamlit)
streamlit run app.py


Model Details
News Extraction
Library: BeautifulSoup4 (primary), newspaper3k (fallback)
Method: Scrapes non-JS weblinks from Google News RSS feed. BeautifulSoup targets <article> or specific <div> classes/IDs; newspaper3k extracts content if BS fails.
Output: Title, topic (keywords or fallback), and content.
Sentiment Analysis
Library: nltk with VADER (Valence Aware Dictionary and sEntiment Reasoner)
Method: Analyzes article content polarity scores (compound score: >0.05 = Positive, <-0.05 = Negative, else Neutral).
Output: Sentiment label per article.
Summarization & Comparative Analysis
Library: groq API with llama3-8b-8192 model
Method: Combines article content, splits into 8000-character chunks if needed, summarizes each chunk, and generates a final summary with comparative sentiment insights across all articles.
Output: Structured summary with per-article summaries, sentiments, and overall insights.
Text-to-Speech
Library: gtts (Google Text-to-Speech), google_trans_new (translation)
Method: Translates summary to Hindi, converts to MP3 audio.
Output: Playable Hindi audio file.


API Development
Backend (api.py)
Framework: FastAPI
Endpoints:
GET /health: Checks API status.
Response: {"status": "API is running"}
POST /fetch-links: Fetches RSS links for a company.
Request: {"Input": "Tesla"}
Response: {"Input": "Tesla", "links": [{"title": "...", "url": "..."}, ...]}
POST /analyze-news: Analyzes provided links.
Request: {"links": ["url1", "url2", ...]}
Response: {"summary": "...", "articles": [...], "extraction_counts": {...}, "audio": "..."}


Assumptions & Limitations

Assumptions
Google News RSS provides at least 10 scrapeable articles.
Articles are in English; translation to Hindi is accurate.
Non-JS weblinks are accessible via BeautifulSoup or newspaper3k.
Groq API has sufficient capacity for summarization.

Limitations
Scraping: Some articles may require JavaScript, which isn’t supported.
Translation: may fail for long texts or rate limits.
TTS: Audio generation is basic; no intonation control.
API Rate Limits: Groq and Google services may throttle requests.
Usage Instructions
Local Usage
Start the FastAPI backend: python api.py.
Run the Streamlit frontend: streamlit run app.py.
Enter a company name in the sidebar to fetch links.
Copy-paste at least 2 links into the manual input fields.
Click "Analyze News" to see summaries, sentiments, and hear Hindi audio.


