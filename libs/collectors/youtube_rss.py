import contextlib
import requests
import httpx
import asyncio
from xml.etree import ElementTree as ET
from typing import Optional, Dict, Any, List, Union

def fetch_channel(
    channel_id: str,
    max_items: int = 25,
    session: Optional[requests.Session] = None,
    headers: Optional[Dict[str, str]] = None,
    proxy: Optional[str] = None,
    timeout: int = 20,
    extract_fields: Optional[List[str]] = None,
    return_raw: bool = False,
    return_tree: bool = False
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Fetch YouTube channel RSS feed and parse entries.
    Args:
        channel_id: YouTube channel ID
        max_items: max number of items to return
        session: optional requests.Session
        headers: optional HTTP headers
        proxy: optional proxy URL
        timeout: request timeout
        extract_fields: extra fields to extract (e.g., ["id", "media:group", "yt:videoId"])
        return_raw: if True, return raw XML string
        return_tree: if True, return parsed ElementTree
    Returns:
        List of dicts (videos) or dict with raw/tree if requested
    """
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = session if session else requests
    try:
        get_kwargs = {}
        if headers:
            get_kwargs['headers'] = headers
        if proxy:
            get_kwargs['proxies'] = {"http": proxy, "https": proxy}
        # Pass only valid kwargs
        r = req.get(url, timeout=timeout,
                   headers=headers if headers else None,
                   proxies={"http": proxy, "https": proxy} if proxy else None)
        r.raise_for_status()
        xml = r.text
        root = ET.fromstring(xml)
        if return_raw:
            return {"raw": xml}
        if return_tree:
            return {"tree": root}
        ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "media": "http://search.yahoo.com/mrss/"}
        items = []
        for entry in root.findall("atom:entry", ns)[:max_items]:
            link = ""
            link_el = entry.find("atom:link", ns)
            if link_el is not None and hasattr(link_el, 'attrib'):
                link = link_el.attrib.get("href", "")
            item = {
                "title": entry.findtext("atom:title", default="", namespaces=ns),
                "link": link,
                "published": entry.findtext("atom:published", default="", namespaces=ns),
                "id": entry.findtext("atom:id", default="", namespaces=ns),
                "yt_video_id": entry.findtext("yt:videoId", default="", namespaces=ns),
            }
            # Optionally extract more fields
            if extract_fields:
                for field in extract_fields:
                    val = entry.findtext(field, default="", namespaces=ns)
                    if not val:
                        el = entry.find(field, ns)
                        if el is not None:
                            val = el.text or ""
                    item[field] = val
            # Extract thumbnails if present
            thumbnails = []
            for thumb in entry.findall("media:group/media:thumbnail", ns):
                turl = thumb.attrib.get("url")
                if turl:
                    thumbnails.append(turl)
            if thumbnails:
                item["thumbnails"] = thumbnails
            items.append(item)
        return items
    except Exception as e:
        return {"error": str(e)}

# Async version
async def fetch_channel_async(
    channel_id: str,
    max_items: int = 25,
    client: Optional[httpx.AsyncClient] = None,
    headers: Optional[Dict[str, str]] = None,
    proxy: Optional[str] = None,
    timeout: int = 20,
    extract_fields: Optional[List[str]] = None,
    return_raw: bool = False,
    return_tree: bool = False
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = client if client else httpx.AsyncClient()
    try:
        cm = req if client else contextlib.nullcontext(req)
        async with cm:
            r = await req.get(url, timeout=timeout,
                             headers=headers if headers else None,
                             proxies=proxy if proxy else None)
            r.raise_for_status()
            xml = r.text
            root = ET.fromstring(xml)
            if return_raw:
                return {"raw": xml}
            if return_tree:
                return {"tree": root}
            ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "media": "http://search.yahoo.com/mrss/"}
            items = []
            for entry in root.findall("atom:entry", ns)[:max_items]:
                link = ""
                link_el = entry.find("atom:link", ns)
                if link_el is not None and hasattr(link_el, 'attrib'):
                    link = link_el.attrib.get("href", "")
                item = {
                    "title": entry.findtext("atom:title", default="", namespaces=ns),
                    "link": link,
                    "published": entry.findtext("atom:published", default="", namespaces=ns),
                    "id": entry.findtext("atom:id", default="", namespaces=ns),
                    "yt_video_id": entry.findtext("yt:videoId", default="", namespaces=ns),
                }
                if extract_fields:
                    for field in extract_fields:
                        val = entry.findtext(field, default="", namespaces=ns)
                        if not val:
                            el = entry.find(field, ns)
                            if el is not None:
                                val = el.text or ""
                        item[field] = val
                thumbnails = []
                for thumb in entry.findall("media:group/media:thumbnail", ns):
                    turl = thumb.attrib.get("url")
                    if turl:
                        thumbnails.append(turl)
                if thumbnails:
                    item["thumbnails"] = thumbnails
                items.append(item)
            return items
    except Exception as e:
        return {"error": str(e)}
