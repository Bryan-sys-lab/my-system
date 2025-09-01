import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_instagram_profile(username: str, limit: int = 25):
    """
    Alternative Instagram scraper using web interface
    Note: Instagram heavily blocks scraping, this is for fallback purposes only
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    try:
        profile_url = f"https://www.instagram.com/{username}/"
        r = requests.get(profile_url, headers=headers, timeout=15)

        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        posts = []

        # Look for JSON data in script tags (Instagram embeds post data)
        scripts = soup.find_all("script", type="application/json")

        for script in scripts:
            try:
                data = json.loads(script.string)
                if "require" in data:
                    continue

                # Navigate through Instagram's JSON structure
                if "entry_data" in data:
                    entry_data = data["entry_data"]
                    if "ProfilePage" in entry_data:
                        profile_data = entry_data["ProfilePage"][0]["graphql"]["user"]
                        media = profile_data["edge_owner_to_timeline_media"]["edges"]

                        for edge in media[:limit]:
                            node = edge["node"]
                            caption = ""
                            if node["edge_media_to_caption"]["edges"]:
                                caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"]

                            posts.append({
                                "caption": caption,
                                "url": f"https://www.instagram.com/p/{node['shortcode']}/",
                                "platform": "instagram",
                                "source": "web_scraper",
                                "username": username,
                                "likes": node["edge_liked_by"]["count"],
                                "comments": node["edge_media_to_comment"]["count"]
                            })

            except (json.JSONDecodeError, KeyError, TypeError):
                continue

        # Fallback: Extract from HTML if JSON parsing fails
        if not posts:
            # Look for post links in the HTML
            post_links = soup.select("article a[href*='/p/']")[:limit]
            for link in post_links:
                href = link.get("href")
                if href:
                    posts.append({
                        "caption": "Content extracted from web scraping",
                        "url": f"https://www.instagram.com{href}",
                        "platform": "instagram",
                        "source": "web_scraper_fallback",
                        "username": username
                    })

        return posts[:limit]

    except Exception as e:
        print(f"Instagram scraping failed: {e}")
        return []