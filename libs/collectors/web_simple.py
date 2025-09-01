import mimetypes
import json
try:
    from langdetect import detect as detect_lang
except ImportError:
    detect_lang = None
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
except ImportError:
    PlaintextParser = Tokenizer = LsaSummarizer = None
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None
import asyncio
import httpx
from typing import Union, List
import time, re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import logging

def fetch_url(
    url: str,
    timeout: int = 20,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 2,
    backoff: float = 1.5,
    extract_tags: Optional[List[str]] = None,
    extract_links: bool = False,
    return_html: bool = False,
    cookies: Optional[Dict[str, str]] = None,
    session: Optional[requests.Session] = None,
    extract_tables: bool = False,
    extract_images: bool = False,
    custom_selectors: Optional[List[str]] = None,
    detect_language: bool = False,
    summarize: bool = False,
    content_type_detection: bool = True,
    use_js: bool = False,
    rate_limit: Optional[float] = None,
    proxy: Optional[str] = None,
    error_hook: Optional[callable] = None,
    extract_structured: bool = False,
    retry_status: Optional[list] = None,
    method: str = "GET",
    data: Optional[dict] = None,
    json_payload: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Fetch a URL and extract main content, with error handling, retries, and extra metadata.
    Args:
        url: URL to fetch
        timeout: request timeout
        headers: optional HTTP headers
        retries: number of retries on failure
        backoff: backoff multiplier between retries
        extract_tags: list of tags to extract text from (default: ["p","li","h1","h2","h3"])
        extract_links: if True, return all links found on the page
        return_html: if True, include raw HTML in the result
    Returns:
        dict with title, text, status, url, fetched_at, meta_description, canonical_url, error (if any), links (if requested), html (if requested)
    """
    if headers is None:
        headers = {"User-Agent": "b-search/1.0 (+https://example.local)"}
    if extract_tags is None:
        extract_tags = ["p","li","h1","h2","h3"]
    attempt = 0
    last_exc = None
    last_request_time = getattr(fetch_url, '_last_request_time', 0)
    import time as _time
    while attempt <= retries:
        if rate_limit:
            now = _time.time()
            wait = rate_limit - (now - last_request_time)
            if wait > 0:
                _time.sleep(wait)
        try:
            req = session if session else requests
            request_args = dict(headers=headers, timeout=timeout, cookies=cookies)
            if proxy:
                request_args['proxies'] = {"http": proxy, "https": proxy}
            if method.upper() == "POST":
                r = req.post(url, data=data, json=json_payload, **request_args)
            elif method.upper() == "PUT":
                r = req.put(url, data=data, json=json_payload, **request_args)
            else:
                r = req.get(url, **request_args)
            if retry_status and r.status_code in retry_status:
                raise requests.HTTPError(f"Retryable status: {r.status_code}")
            r.raise_for_status()
            content_type = r.headers.get('Content-Type', '')
            if content_type_detection and ('pdf' in content_type or url.lower().endswith('.pdf')):
                return {"content_type": "pdf", "url": url, "status": r.status_code, "fetched_at": time.time()}
            if content_type_detection and ('image' in content_type or url.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.svg'))):
                return {"content_type": "image", "url": url, "status": r.status_code, "fetched_at": time.time()}
            # JS rendering fallback
            html = None
            if use_js and sync_playwright:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, timeout=timeout*1000)
                    _time.sleep(2)  # let JS load
                    html = page.content()
                    browser.close()
            if not html:
                encoding = r.encoding if r.encoding else r.apparent_encoding
                html = r.content.decode(encoding, errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            title = (soup.title.text.strip() if soup.title else "")
            text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(extract_tags))
            text = re.sub(r"\s+", " ", text)[:20000]
            # Language detection
            lang = None
            if detect_language and detect_lang:
                try:
                    lang = detect_lang(text)
                except Exception:
                    lang = None
            # Summarization
            summary = None
            if summarize and PlaintextParser and Tokenizer and LsaSummarizer:
                try:
                    parser = PlaintextParser.from_string(text, Tokenizer(lang or "en"))
                    summarizer = LsaSummarizer()
                    summary = " ".join(str(sentence) for sentence in summarizer(parser.document, 3))
                except Exception:
                    summary = None
            meta = soup.find("meta", attrs={"name": "description"})
            from bs4.element import Tag
            if isinstance(meta, Tag):
                content = meta.get("content")
                if isinstance(content, list):
                    content = content[0] if content else ""
                if isinstance(content, str):
                    meta_desc = content.strip()
            canonical = ""
            link = soup.find("link", rel="canonical")
            if isinstance(link, Tag):
                href = link.get("href")
                if isinstance(href, list):
                    href = href[0] if href else ""
                if isinstance(href, str):
                    canonical = href.strip()
            links = []
            if extract_links:
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    if isinstance(href, str):
                        links.append(href)
            tables = []
            if extract_tables:
                for table in soup.find_all("table"):
                    rows = []
                    for tr in table.find_all("tr"):
                        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                        if cells:
                            rows.append(cells)
                    if rows:
                        tables.append(rows)
            images = []
            if extract_images:
                for img in soup.find_all("img"):
                    src = img.get("src")
                    if isinstance(src, str):
                        images.append(src)
            custom = {}
            if custom_selectors:
                for sel in custom_selectors:
                    custom[sel] = [el.get_text(" ", strip=True) for el in soup.select(sel)]
            # Structured data extraction
            structured = {}
            if extract_structured:
                # JSON-LD
                for tag in soup.find_all("script", type="application/ld+json"):
                    try:
                        structured.setdefault("jsonld", []).append(json.loads(tag.string))
                    except Exception:
                        pass
                # OpenGraph
                og = {}
                for tag in soup.find_all("meta"):
                    if tag.get("property", "").startswith("og:"):
                        og[tag.get("property")] = tag.get("content", "")
                if og:
                    structured["opengraph"] = og
                # Twitter cards
                tw = {}
                for tag in soup.find_all("meta"):
                    if tag.get("name", "").startswith("twitter:"):
                        tw[tag.get("name")] = tag.get("content", "")
                if tw:
                    structured["twitter"] = tw
            result = {
                "title": title,
                "text": text,
                "status": r.status_code,
                "url": url,
                "fetched_at": time.time(),
                "meta_description": meta_desc,
                "canonical_url": canonical,
            }
            if extract_links:
                result["links"] = links
            if return_html:
                result["html"] = html
            if extract_tables:
                result["tables"] = tables
            if extract_images:
                result["images"] = images
            if custom_selectors:
                result["custom"] = custom
            if detect_language:
                result["language"] = lang
            if summarize:
                result["summary"] = summary
            if extract_structured:
                result["structured"] = structured
            fetch_url._last_request_time = _time.time()
            return result
        except requests.Timeout as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"Timeout fetching {url}: {e}")
            _time.sleep(backoff * (attempt + 1))
            attempt += 1
        except requests.ConnectionError as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"Connection error fetching {url}: {e}")
            _time.sleep(backoff * (attempt + 1))
            attempt += 1
        except Exception as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"fetch_url error for {url}: {e}")
            _time.sleep(backoff * (attempt + 1))
            attempt += 1
    return {
        "title": "",
        "text": "",
        "status": None,
        "url": url,
        "fetched_at": time.time(),
        "meta_description": "",
        "canonical_url": "",
        "error": str(last_exc) if last_exc else "Unknown error"
    }

# Async version
async def fetch_url_async(
    url: str,
    timeout: int = 20,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 2,
    backoff: float = 1.5,
    extract_tags: Optional[List[str]] = None,
    extract_links: bool = False,
    return_html: bool = False,
    cookies: Optional[Dict[str, str]] = None,
    session: Optional[httpx.AsyncClient] = None,
    extract_tables: bool = False,
    extract_images: bool = False,
    custom_selectors: Optional[List[str]] = None,
    detect_language: bool = False,
    summarize: bool = False,
    content_type_detection: bool = True,
    use_js: bool = False,
    rate_limit: Optional[float] = None,
    proxy: Optional[str] = None,
    error_hook: Optional[callable] = None,
    extract_structured: bool = False,
    retry_status: Optional[list] = None,
    method: str = "GET",
    data: Optional[dict] = None,
    json_payload: Optional[dict] = None
) -> Dict[str, Any]:
    if headers is None:
        headers = {"User-Agent": "b-search/1.0 (+https://example.local)"}
    if extract_tags is None:
        extract_tags = ["p","li","h1","h2","h3"]
    attempt = 0
    last_exc = None
    last_request_time = getattr(fetch_url_async, '_last_request_time', 0)
    import time as _time
    while attempt <= retries:
        if rate_limit:
            now = _time.time()
            wait = rate_limit - (now - last_request_time)
            if wait > 0:
                await asyncio.sleep(wait)
        try:
            req = session if session else httpx.AsyncClient()
            request_args = dict(headers=headers, timeout=timeout, cookies=cookies)
            if proxy:
                request_args['proxies'] = proxy
            if method.upper() == "POST":
                resp = await req.post(url, data=data, json=json_payload, **request_args)
            elif method.upper() == "PUT":
                resp = await req.put(url, data=data, json=json_payload, **request_args)
            else:
                resp = await req.get(url, **request_args)
            if retry_status and resp.status_code in retry_status:
                raise httpx.HTTPStatusError(f"Retryable status: {resp.status_code}", request=None, response=resp)
            resp.raise_for_status()
            content_type = resp.headers.get('Content-Type', '')
            if content_type_detection and ('pdf' in content_type or url.lower().endswith('.pdf')):
                return {"content_type": "pdf", "url": url, "status": resp.status_code, "fetched_at": _time.time()}
            if content_type_detection and ('image' in content_type or url.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.svg'))):
                return {"content_type": "image", "url": url, "status": resp.status_code, "fetched_at": _time.time()}
            html = None
            if use_js and sync_playwright:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=timeout*1000)
                    await asyncio.sleep(2)
                    html = await page.content()
                    await browser.close()
            if not html:
                encoding = resp.encoding if resp.encoding else resp.apparent_encoding
                html = resp.content.decode(encoding, errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            title = (soup.title.text.strip() if soup.title else "")
            text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(extract_tags))
            text = re.sub(r"\s+", " ", text)[:20000]
            lang = None
            if detect_language and detect_lang:
                try:
                    lang = detect_lang(text)
                except Exception:
                    lang = None
            summary = None
            if summarize and PlaintextParser and Tokenizer and LsaSummarizer:
                try:
                    parser = PlaintextParser.from_string(text, Tokenizer(lang or "en"))
                    summarizer = LsaSummarizer()
                    summary = " ".join(str(sentence) for sentence in summarizer(parser.document, 3))
                except Exception:
                    summary = None
            meta_desc = ""
            meta = soup.find("meta", attrs={"name": "description"})
            from bs4.element import Tag
            if isinstance(meta, Tag):
                content = meta.get("content")
                if isinstance(content, list):
                    content = content[0] if content else ""
                if isinstance(content, str):
                    meta_desc = content.strip()
            canonical = ""
            link = soup.find("link", rel="canonical")
            if isinstance(link, Tag):
                href = link.get("href")
                if isinstance(href, list):
                    href = href[0] if href else ""
                if isinstance(href, str):
                    canonical = href.strip()
            links = []
            if extract_links:
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    if isinstance(href, str):
                        links.append(href)
            tables = []
            if extract_tables:
                for table in soup.find_all("table"):
                    rows = []
                    for tr in table.find_all("tr"):
                        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                        if cells:
                            rows.append(cells)
                    if rows:
                        tables.append(rows)
            images = []
            if extract_images:
                for img in soup.find_all("img"):
                    src = img.get("src")
                    if isinstance(src, str):
                        images.append(src)
            custom = {}
            if custom_selectors:
                for sel in custom_selectors:
                    custom[sel] = [el.get_text(" ", strip=True) for el in soup.select(sel)]
            structured = {}
            if extract_structured:
                for tag in soup.find_all("script", type="application/ld+json"):
                    try:
                        structured.setdefault("jsonld", []).append(json.loads(tag.string))
                    except Exception:
                        pass
                og = {}
                for tag in soup.find_all("meta"):
                    if tag.get("property", "").startswith("og:"):
                        og[tag.get("property")] = tag.get("content", "")
                if og:
                    structured["opengraph"] = og
                tw = {}
                for tag in soup.find_all("meta"):
                    if tag.get("name", "").startswith("twitter:"):
                        tw[tag.get("name")] = tag.get("content", "")
                if tw:
                    structured["twitter"] = tw
            result = {
                "title": title,
                "text": text,
                "status": resp.status_code,
                "url": url,
                "fetched_at": _time.time(),
                "meta_description": meta_desc,
                "canonical_url": canonical,
            }
            if extract_links:
                result["links"] = links
            if return_html:
                result["html"] = html
            if extract_tables:
                result["tables"] = tables
            if extract_images:
                result["images"] = images
            if custom_selectors:
                result["custom"] = custom
            if detect_language:
                result["language"] = lang
            if summarize:
                result["summary"] = summary
            if extract_structured:
                result["structured"] = structured
            fetch_url_async._last_request_time = _time.time()
            return result
        except httpx.TimeoutException as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"Timeout fetching {url}: {e}")
            await asyncio.sleep(backoff * (attempt + 1))
            attempt += 1
        except httpx.RequestError as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"Connection error fetching {url}: {e}")
            await asyncio.sleep(backoff * (attempt + 1))
            attempt += 1
        except Exception as e:
            last_exc = e
            if error_hook:
                error_hook(e, url)
            logging.warning(f"fetch_url_async error for {url}: {e}")
            await asyncio.sleep(backoff * (attempt + 1))
            attempt += 1
    return {
        "title": "",
        "text": "",
        "status": None,
        "url": url,
        "fetched_at": _time.time(),
        "meta_description": "",
        "canonical_url": "",
        "error": str(last_exc) if last_exc else "Unknown error"
    }
