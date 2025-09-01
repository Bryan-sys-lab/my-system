"""TikTok collector helpers.

yt_dlp is an optional dependency. Importing it at module import time can
cause the whole test suite to fail when `yt_dlp` isn't installed. We guard
the import and expose a runtime function that raises a clear error if the
consumer tries to call it without yt_dlp available.
"""

try:
    import yt_dlp  # type: ignore
except Exception:  # pragma: no cover - depends on test environment
    yt_dlp = None


def user_posts(username: str, max_items: int = 20):
    """Return flattened TikTok posts for a username using yt_dlp.

    Raises:
        RuntimeError: if `yt_dlp` is not installed in the environment.
    """
    if yt_dlp is None:
        raise RuntimeError(
            "yt_dlp is not available. Install yt_dlp to use the TikTok collector"
        )

    url = f"https://www.tiktok.com/@{username}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "playlistend": max_items,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    # Flatten entries
    entries = info.get("entries", [])
    out = []
    for e in entries[:max_items]:
        out.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "url": e.get("url") or e.get("webpage_url"),
                "uploader": e.get("uploader"),
                "timestamp": e.get("timestamp"),
            }
        )
    return out
