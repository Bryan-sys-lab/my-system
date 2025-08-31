import os, requests

def tor_session():
    # Requires a running Tor SOCKS proxy (e.g., on localhost:9050) configured externally
    proxy = os.getenv("TOR_SOCKS_PROXY", "socks5h://localhost:9050")
    s = requests.Session()
    s.proxies = {"http": proxy, "https": proxy}
    s.headers.update({"User-Agent": "b-search/1.0 (tor)"})
    # Small sanity check : s.get("http://httpbin.org/ip")
    return s
