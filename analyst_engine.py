import urllib.parse
import feedparser
import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load local TML Analytics .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def fetch_google_news_rss(ticker: str) -> list:
    """
    Fetch the latest 3-5 news headlines from Google News RSS.
    """
    query = urllib.parse.quote(f'"{ticker}" stock news')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:4]: # Get top 4
            title = entry.title
            
            # Clean up the date string
            pub_date = "Recent"
            try:
                from dateutil import parser
                if hasattr(entry, 'published'):
                    dt = parser.parse(entry.published)
                    pub_date = dt.strftime("%b %d")
            except:
                pass
            
            news_items.append(f"- **{title}** <span style='color:#777; font-size: 11px;'>({pub_date})</span>")
        
        if not news_items:
            # Fallback broader search
            query = urllib.parse.quote(f"{ticker} stock")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                news_items.append(f"- {entry.title}")
                
        return news_items
    except Exception as e:
        print(f"News fetch error for {ticker}: {e}")
        return ["No recent news available."]

def generate_ibd_brief(ticker: str, tech_data: dict, news_items: list) -> str:
    """
    Call gpt-oss-120b:free via OpenRouter to act as an IBD analyst.
    """
    if not OPENROUTER_API_KEY:
        return "❌ Error: OPENROUTER_API_KEY not found in environment."

    news_text = "\n".join(news_items)
    
    # Construct context packet
    context = f"""
    TICKER: {ticker}
    CURRENT PRICE: {tech_data.get('close', 'N/A')}
    DISTANCE FROM 52W HIGH: {tech_data.get('dist_from_high', 'N/A')}%
    
    TECHNICAL STATE:
    - Minervini Trend Template Passed: {tech_data.get('minervini_passed', False)} (Score: {tech_data.get('minervini_count', 0)}/8)
    - VCP Pattern Detected: {tech_data.get('vcp_detected', False)}
    - VCP Forming: {tech_data.get('vcp_forming', False)}
    - Volume Dry-up Detected: {tech_data.get('vol_dryup', False)}
    - Overall Buy-Readiness Label: {tech_data.get('label', 'Not Ready')}
    
    RECENT NEWS HEADLINES:
    {news_text}
    """

    prompt = f"""
    You are an elite stock market analyst writing for Investor's Business Daily (IBD).
    I am providing you with the exact technical and fundamental data for the True Market Leader stock '{ticker}'.
    
    {context}
    
    Write a concise, punchy 3-bullet brief analyzing this stock.
    Focus strictly on the technical setup (VCP, distance from high, volume dryup) and how the recent news provides a fundamental catalyst. 
    Use strong, authoritative momentum-trading language (e.g., 'tightening action', 'constructive base', 'institutional accumulation').
    Do not use introductory or concluding filler. Just return the markdown bullets.
    """

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ LLM Error: {response.text}"
            
    except Exception as e:
        return f"❌ LLM Exception: {e}"
