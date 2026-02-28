import requests
import json
import os

# Configuration from GitHub Secrets
SERPER_API_KEY = os.getenv("SERPER_API_KEY") 
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Targeted Search Queries for Morocco
QUERIES = [
    'site:eventbrite.com "tech" Morocco (Rabat OR Casablanca OR Tanger)',
    'site:meetup.com "developer" Morocco (Rabat OR Casablanca OR Tanger)',
    '"conference informatique" Maroc 2026',
    '"PFE" software engineering (Rabat OR Casablanca) 2026',
    '"STABLEX" mention' # Tracking mentions of your new company!
]

def search_internet(query):
    url = "https://google.serper.dev/search"
    # tbs: "qdr:d" looks for results from the LAST 24 HOURS
    payload = json.dumps({"q": query, "tbs": "qdr:d"}) 
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except:
        return []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    seen_links = []
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            seen_links = json.load(f)

    new_results = []
    for query in QUERIES:
        for item in search_internet(query):
            link = item.get('link')
            if link not in seen_links:
                new_results.append(f"🌟 *{item.get('title')}*\n🔗 {link}")
                seen_links.append(link)

    if new_results:
        send_telegram("🔍 *Daily Tech & Opportunity Scan:*\n\n" + "\n\n".join(new_results))
    
    # Save history to avoid duplicate notifications
    with open("history.json", "w") as f:
        json.dump(seen_links[-300:], f)
