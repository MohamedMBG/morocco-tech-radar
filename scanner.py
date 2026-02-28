import requests
import json
import os

# Secrets from GitHub
SERPER_API_KEY = os.getenv("SERPER_API_KEY") 
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# High-Authority Queries for Big Events
QUERIES = [
    'site:gitexafrica.com "2026"',
    '"GITEX Africa" 2026 Marrakech dates',
    '"Summit" OR "Forum" technology Morocco 2026',
    '"Salon International" informatique Maroc 2026',
    'site:medias24.com "Digital" OR "Startup" Morocco',
    '"PFE" software engineering (Rabat OR Casablanca) 2026'
]

def search_internet(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "tbs": "qdr:w"}) # Search last 7 days
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except: return []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    seen_links = []
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            seen_links = json.load(f)

    # NOISE FILTER: Skips webinars and casual social media
    EXCLUDE = ["webinar", "zoom", "online only", "facebook", "youtube", "instagram", "iftar"]
    # SIGNAL FILTER: Prioritizes big events
    PRIORITY = ["summit", "forum", "gitex", "pfe", "investment", "conference", "salon"]

    new_results = []
    for query in QUERIES:
        for item in search_internet(query):
            title = item.get('title').lower()
            snippet = item.get('snippet', '').lower()
            link = item.get('link')

            is_noisy = any(word in title or word in snippet for word in EXCLUDE)
            is_big = any(word in title or word in snippet for word in PRIORITY)

            if link not in seen_links and not is_noisy and is_big:
                new_results.append(f"🏛️ *MAJOR EVENT:* {item.get('title')}\n🔗 {link}")
                seen_links.append(link)

    if new_results:
        send_telegram("🚀 *High-Authority Tech Scan (Morocco 2026):*\n\n" + "\n\n".join(new_results))
    
    with open("history.json", "w") as f:
        json.dump(seen_links[-300:], f)
