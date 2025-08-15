import requests
from xml.etree import ElementTree as ET

def fetch_channel(channel_id: str, max_items: int = 25):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    items = []
    for entry in root.findall("atom:entry", ns)[:max_items]:
        title = entry.findtext("atom:title", default="", namespaces=ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.attrib.get("href") if link_el is not None else ""
        published = entry.findtext("atom:published", default="", namespaces=ns)
        items.append({"title": title, "link": link, "published": published})
    return items
