# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import utils
import os

app = FastAPI()

class CompanyRequest(BaseModel):
    company: str

class LinksRequest(BaseModel):
    links: List[str]

@app.get("/health")
async def health_check():
    return {"status": "API is running"}

@app.post("/fetch-links")
async def fetch_links(request: CompanyRequest):
    try:
        links = utils.fetch_rss_links(request.company)
        return {"company": request.company, "links": [{"title": title, "url": url} for title, url in links]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching links: {str(e)}")


@app.post("/analyze-news")
async def analyze_news(request: LinksRequest):
    if len(request.links) < 2:
        raise HTTPException(status_code=400, detail="At least 2 links are required.")
    
    articles = []
    bs_count = [0]
    np_count = [0]
    
    for link in request.links:
        title, topic, content = utils.scrape_article(link, bs_count, np_count)
        sentiment = utils.analyze_sentiment(content)
        articles.append({"url": link, "title": title, "topic": topic, "content": content, "sentiment": sentiment})
    
    summary_text = utils.generate_summary(articles)
    summary_audio = utils.generate_tts(summary_text)
    
    response = {
        "summary": summary_text,
        "articles": articles,
        "extraction_counts": {"beautifulsoup": bs_count[0], "newspaper3k": np_count[0]}
    }
    
    if summary_audio and os.path.exists(summary_audio):
        with open(summary_audio, "rb") as f:
            response["audio"] = f.read().hex()  # Keep as hex for now

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
