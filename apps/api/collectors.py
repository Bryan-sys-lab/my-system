"""
Collection service for handling data collection operations
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from libs.collectors.web_simple import fetch_url
from libs.collectors.rss import fetch_rss
from libs.enrichment.nlp import extract_entities
from libs.crypto.btc import address_txs
from libs.collectors.rss_multi import fetch_many as rss_fetch_many
from libs.collectors.reddit import fetch_subreddit_json
from libs.collectors.youtube_rss import fetch_channel as youtube_fetch_channel
from libs.collectors.wayback import latest_snapshot
from libs.common.fallback import run_with_fallbacks
from libs.collectors.social.nitter_search import nitter_search
from libs.collectors.reddit_old import old_reddit_top
from libs.collectors.wayback_fetch import fetch_wayback_text

from .database import DatabaseManager
from .exceptions import CollectorError
from .config import DEFAULT_NITTER_INSTANCE

logger = logging.getLogger("apps.api.collectors")


class CollectionService:
    """Service for handling various data collection operations"""

    @staticmethod
    def collect_web_content(url: str, project_id: str) -> Dict[str, Any]:
        """
        Collect content from a web URL.

        Args:
            url: URL to collect from
            project_id: Project ID to associate with collected data

        Returns:
            Collection result with saved item ID and metadata
        """
        try:
            # Fetch web content
            data = fetch_url(url)

            # Extract entities from content
            entities = extract_entities(data["text"][:10000])

            # Prepare item data
            item_data = {
                "project_id": project_id,
                "content": data["text"],
                "meta": {
                    "title": data["title"],
                    "url": url,
                    "entities": entities,
                    "source": "web_scraper",
                    "collected_at": datetime.now(timezone.utc).isoformat()
                }
            }

            return {
                "item_data": item_data,
                "entities": entities,
                "source": "web_scraper"
            }

        except Exception as e:
            logger.error(f"Web collection failed for URL {url}: {str(e)}")
            raise CollectorError("web_scraper", f"Failed to collect from {url}: {str(e)}")

    @staticmethod
    def collect_rss_pack(pack_path: str, project_id: str) -> Dict[str, Any]:
        """
        Collect RSS feeds from a pack configuration.

        Args:
            pack_path: Path to RSS pack YAML file
            project_id: Project ID to associate with collected data

        Returns:
            Collection result with saved items
        """
        try:
            import yaml

            # Load RSS pack configuration
            with open(pack_path, "r") as f:
                cfg = yaml.safe_load(f)

            feeds = [s["url"] for s in cfg.get("sources", []) if s.get("type") == "rss"]

            # Fetch RSS data
            data = rss_fetch_many(feeds, per_feed_limit=20)

            # Prepare items data
            items_data = []
            for item in data:
                items_data.append({
                    "project_id": project_id,
                    "content": item.get("summary", ""),
                    "meta": {
                        **item,
                        "source": "rss_pack",
                        "pack_path": pack_path,
                        "collected_at": datetime.now(timezone.utc).isoformat()
                    }
                })

            return {
                "items_data": items_data,
                "count": len(items_data),
                "source": "rss_pack"
            }

        except Exception as e:
            logger.error(f"RSS pack collection failed for {pack_path}: {str(e)}")
            raise CollectorError("rss_pack", f"Failed to collect RSS pack {pack_path}: {str(e)}")

    @staticmethod
    def collect_reddit_subreddit(subreddit: str, project_id: str) -> Dict[str, Any]:
        """
        Collect posts from a Reddit subreddit.

        Args:
            subreddit: Subreddit name to collect from
            project_id: Project ID to associate with collected data

        Returns:
            Collection result with saved items
        """
        try:
            def _json():
                return fetch_subreddit_json(subreddit)

            def _old():
                return old_reddit_top(subreddit)

            def _wayback():
                snap = latest_snapshot(f"https://www.reddit.com/r/{subreddit}/")
                if not snap:
                    return []
                doc = fetch_wayback_text(snap["url"])
                return [{"title": doc["text"][:1000], "wayback_url": doc["url"]}]

            # Try multiple sources with fallbacks
            result = run_with_fallbacks([
                ("reddit_json", _json),
                ("old_reddit", _old),
                ("wayback", _wayback)
            ])

            data = result["data"]

            # Prepare items data
            items_data = []
            for item in data:
                content = item.get("title", "")
                meta = {
                    "source": result["source"],
                    "platform": "reddit",
                    "subreddit": subreddit,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    **item
                }

                items_data.append({
                    "project_id": project_id,
                    "content": content,
                    "meta": meta
                })

            return {
                "items_data": items_data,
                "count": len(items_data),
                "source": result["source"],
                "errors": result.get("errors", [])
            }

        except Exception as e:
            logger.error(f"Reddit collection failed for r/{subreddit}: {str(e)}")
            raise CollectorError("reddit", f"Failed to collect from r/{subreddit}: {str(e)}")

    @staticmethod
    def collect_youtube_channel(channel_id: str, project_id: str) -> Dict[str, Any]:
        """
        Collect videos from a YouTube channel.

        Args:
            channel_id: YouTube channel ID
            project_id: Project ID to associate with collected data

        Returns:
            Collection result with saved items
        """
        try:
            data = youtube_fetch_channel(channel_id)

            # Prepare items data
            items_data = []
            for item in data:
                items_data.append({
                    "project_id": project_id,
                    "content": item.get("title", ""),
                    "meta": {
                        **item,
                        "platform": "youtube",
                        "channel_id": channel_id,
                        "collected_at": datetime.now(timezone.utc).isoformat()
                    }
                })

            return {
                "items_data": items_data,
                "count": len(items_data),
                "source": "youtube_api"
            }

        except Exception as e:
            logger.error(f"YouTube collection failed for channel {channel_id}: {str(e)}")
            raise CollectorError("youtube", f"Failed to collect from YouTube channel {channel_id}: {str(e)}")

    @staticmethod
    def collect_crypto_btc(address: str) -> Dict[str, Any]:
        """
        Collect Bitcoin transaction data for an address.

        Args:
            address: Bitcoin address to query

        Returns:
            Transaction data
        """
        try:
            txs = address_txs(address)
            return {
                "count": len(txs),
                "transactions": txs[:10],  # Limit to first 10
                "address": address
            }

        except Exception as e:
            logger.error(f"BTC collection failed for address {address}: {str(e)}")
            raise CollectorError("bitcoin", f"Failed to collect BTC data for {address}: {str(e)}")

    @staticmethod
    def collect_wayback_snapshot(url: str, project_id: str) -> Dict[str, Any]:
        """
        Collect Wayback Machine snapshot for a URL.

        Args:
            url: URL to find snapshot for
            project_id: Project ID to associate with collected data

        Returns:
            Snapshot data
        """
        try:
            snap = latest_snapshot(url)
            if not snap:
                return {"snapshot": None}

            # Prepare item data
            item_data = {
                "project_id": project_id,
                "content": snap["url"],
                "meta": {
                    **snap,
                    "source": "wayback_machine",
                    "original_url": url,
                    "collected_at": datetime.now(timezone.utc).isoformat()
                }
            }

            return {
                "item_data": item_data,
                "snapshot": snap,
                "source": "wayback_machine"
            }

        except Exception as e:
            logger.error(f"Wayback collection failed for URL {url}: {str(e)}")
            raise CollectorError("wayback", f"Failed to collect Wayback snapshot for {url}: {str(e)}")

    @staticmethod
    def collect_twitter_search(query: str, project_id: str, max_results: int = 25) -> Dict[str, Any]:
        """
        Collect tweets from Twitter search.

        Args:
            query: Search query
            project_id: Project ID to associate with collected data
            max_results: Maximum number of results to return

        Returns:
            Collection result with saved items
        """
        try:
            from libs.collectors.social.twitter_v2 import search_recent as twitter_search_recent

            data = twitter_search_recent(query, max_results=max_results)

            # Prepare items data
            items_data = []
            for item in data:
                items_data.append({
                    "project_id": project_id,
                    "content": item.get("text", ""),
                    "meta": {
                        **item,
                        "platform": "twitter",
                        "query": query,
                        "collected_at": datetime.now(timezone.utc).isoformat()
                    }
                })

            return {
                "items_data": items_data,
                "count": len(items_data),
                "source": "twitter_v2"
            }

        except Exception as e:
            logger.error(f"Twitter search failed for query '{query}': {str(e)}")
            raise CollectorError("twitter", f"Failed to search Twitter for '{query}': {str(e)}")

    @staticmethod
    def collect_twitter_auto(query: str, project_id: str, max_results: int = 25) -> Dict[str, Any]:
        """
        Collect tweets with automatic fallback methods.

        Args:
            query: Search query
            project_id: Project ID to associate with collected data
            max_results: Maximum number of results to return

        Returns:
            Collection result with saved items
        """
        try:
            from libs.collectors.social.twitter_v2 import search_recent as twitter_search_recent

            def _main():
                return twitter_search_recent(query, max_results=max_results)

            def _nitter():
                return nitter_search(DEFAULT_NITTER_INSTANCE, query, limit=max_results)

            def _wayback():
                snap = latest_snapshot(f"https://x.com/search?q={query}")
                if not snap:
                    return []
                doc = fetch_wayback_text(snap["url"])
                return [{"text": doc["text"][:1000], "wayback_url": doc["url"]}]

            # Try multiple sources with fallbacks
            result = run_with_fallbacks([
                ("twitter_v2", _main),
                ("nitter", _nitter),
                ("wayback", _wayback)
            ])

            data = result["data"]

            # Prepare items data
            items_data = []
            for item in data:
                content = item.get("text") or item.get("title") or ""
                items_data.append({
                    "project_id": project_id,
                    "content": content,
                    "meta": {
                        "source": result["source"],
                        "platform": "twitter",
                        "query": query,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                        **item
                    }
                })

            return {
                "items_data": items_data,
                "count": len(items_data),
                "source": result["source"],
                "errors": result.get("errors", [])
            }

        except Exception as e:
            logger.error(f"Twitter auto collection failed for query '{query}': {str(e)}")
            raise CollectorError("twitter", f"Failed to auto-collect Twitter data for '{query}': {str(e)}")