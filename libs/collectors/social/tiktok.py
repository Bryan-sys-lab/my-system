import yt_dlp

def user_posts(username: str, max_items: int = 20):
    url = f"https://www.tiktok.com/@{username}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "playlistend": max_items
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    # Flatten entries
    entries = info.get("entries", [])
    out = []
    for e in entries[:max_items]:
        out.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "url": e.get("url") or e.get("webpage_url"),
            "uploader": e.get("uploader"),
            "timestamp": e.get("timestamp"),
        })
    return out
