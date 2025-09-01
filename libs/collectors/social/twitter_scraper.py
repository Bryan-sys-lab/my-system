import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def scrape_twitter_search(query: str, max_results: int = 20):
    """
    Alternative Twitter scraper using web interface
    Note: Twitter heavily blocks scraping, this is for fallback purposes only
    """
    # Use a realistic User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        # Search URL (this may not work due to Twitter's anti-scraping measures)
        search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&f=live"
        r = requests.get(search_url, headers=headers, timeout=15)

        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        tweets = []
        # Look for tweet articles (this selector may need updating as Twitter changes their HTML)
        for article in soup.select("article[data-testid='tweet']")[:max_results]:
            try:
                # Extract tweet text
                text_elem = article.select_one("[data-testid='tweetText']")
                text = text_elem.get_text() if text_elem else ""

                # Extract username and tweet ID for URL construction
                link_elem = article.select_one("a[href*='/status/']")
                if link_elem:
                    href = link_elem['href']
                    tweet_url = f"https://twitter.com{href}"
                else:
                    tweet_url = ""

                if text:
                    tweets.append({
                        "text": text,
                        "url": tweet_url,
                        "platform": "twitter",
                        "source": "web_scraper"
                    })

            except Exception:
                continue

        return tweets

    except Exception as e:
        print(f"Twitter scraping failed: {e}")
        return []