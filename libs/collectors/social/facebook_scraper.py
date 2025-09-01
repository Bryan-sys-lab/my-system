import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def scrape_facebook_page(page_id: str, limit: int = 25):
    """
    Alternative Facebook scraper using web interface
    Note: Facebook heavily blocks scraping, this is for fallback purposes only
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    try:
        # Try the public page URL
        page_url = f"https://www.facebook.com/{page_id}"
        r = requests.get(page_url, headers=headers, timeout=15)

        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        posts = []

        # Look for post content (Facebook changes their HTML structure frequently)
        # This is a basic implementation that may need updates
        post_elements = soup.select("[data-ad-preview='message']")[:limit]

        for post_elem in post_elements:
            try:
                message = post_elem.get_text().strip()
                if message:
                    posts.append({
                        "message": message,
                        "url": page_url,
                        "platform": "facebook",
                        "source": "web_scraper",
                        "page_id": page_id
                    })
            except Exception:
                continue

        # If no posts found with primary selector, try alternative approaches
        if not posts:
            # Look for any text content that might be posts
            content_divs = soup.select("div[data-pagelet]")[:limit]
            for div in content_divs:
                text = div.get_text().strip()
                if len(text) > 50:  # Only include substantial text
                    posts.append({
                        "message": text[:1000],  # Limit text length
                        "url": page_url,
                        "platform": "facebook",
                        "source": "web_scraper_fallback",
                        "page_id": page_id
                    })

        return posts[:limit]

    except Exception as e:
        print(f"Facebook scraping failed: {e}")
        return []