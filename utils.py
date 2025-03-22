# utils.py
import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gtts import gTTS
from googletrans import Translator
import urllib.parse
from groq import Groq
import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def fetch_rss_links(Input):
    encoded_query = urllib.parse.quote(Input)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}"
    feed = feedparser.parse(rss_url)
    links = [(entry.title, entry.link) for entry in feed.entries[:20]]
    return links

def scrape_article(url, bs_count, np_count):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        content = (soup.find('article') or
                   soup.find('div', class_=['main-content', 'article-body', 'story-body', 'entry-content', 'post-content', 'article-content', 'story-content']) or
                   soup.find(id=['article-body', 'story']))
        title = soup.find('title').get_text(strip=True) if soup.find('title') else "No Title Found"
        topic = soup.find('meta', attrs={'name': 'keywords'})
        topic = topic['content'] if topic else "No Topic Found"
        
        if content:
            for tag in content.find_all(['script', 'style', 'aside', 'nav', 'form', 'footer', 'header', 'noscript']):
                tag.decompose()
            extracted_text = " ".join(p.get_text().strip() for p in content.find_all('p') if p.get_text().strip())
            if len(extracted_text.split()) > 50:
                bs_count[0] += 1
                return title, topic, extracted_text
        
        article = Article(url)
        article.download()
        article.parse()
        np_count[0] += 1
        return article.title, "Extracted via Newspaper3k", article.text if article.text else "Content extraction failed."
    except Exception as e:
        return "Failed to fetch title", "Failed to fetch topic", f"Failed to fetch content: {e}"

def analyze_sentiment(text):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    return "Positive" if scores["compound"] > 0.05 else "Negative" if scores["compound"] < -0.05 else "Neutral"

# def generate_summary(articles):
#     full_text = "\n\n".join([article['content'] for article in articles])
#     max_chars = 4000
#     if len(full_text) > max_chars:
#         full_text = full_text[:max_chars]
#     prompt = f"Summarize the following news articles and conduct a comparative sentiment analysis to derive insights on how the company's news coverage varies:\n{full_text}"
#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[{"role": "system", "content": "You are a news summarizer and analyst."},
#                   {"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content
def generate_summary(articles):
    # Combine all article content
    full_text = "\n\n---\n\n".join([f"Article {i+1}: {article['content']}" for i, article in enumerate(articles)])
    max_chars_per_chunk = 8000  # Adjust based on model token limit
    
    # Split into chunks if necessary
    if len(full_text) > max_chars_per_chunk:
        chunks = [full_text[i:i + max_chars_per_chunk] for i in range(0, len(full_text), max_chars_per_chunk)]
        summaries = []
        
        for chunk in chunks:
            prompt = (
                "Summarize the following news article content and analyze its sentiment:\n\n"
                f"{chunk}"
            )
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a news summarizer and analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            summaries.append(response.choices[0].message.content)
        
        # Combine chunk summaries and generate overall insights
        combined_prompt = (
            "Combine the following partial summaries into a cohesive overall summary and provide comparative sentiment analysis "
            "insights across all articles:\n\n" + "\n\n".join(summaries)
        )
        final_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a news summarizer and analyst."},
                {"role": "user", "content": combined_prompt}
            ]
        )
        return final_response.choices[0].message.content
    
    # Single call if within limit
    else:
        prompt = (
            "You are a news summarizer and analyst. Summarize the following news articles and conduct a comparative sentiment analysis "
            "to derive insights on how the company's news coverage varies across ALL provided articles. "
            "For each article, provide a brief summary and its sentiment implication. Then, give an overall summary and comparative insights:\n\n"
            f"{full_text}"
        )
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a news summarizer and analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    

def generate_tts(text):
    if not text or text.strip() == "No content available for summarization.":
        return None
    try:
        translator = Translator()
        hindi_text = translator.translate(text, dest="hi").text
        if not hindi_text:
            return None
        tts = gTTS(hindi_text, lang="hi")
        audio_file = "summary_output.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
