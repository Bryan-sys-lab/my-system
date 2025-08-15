from pathlib import Path
import hashlib

def scan_dir(path: str):
    p = Path(path)
    results = []
    for f in p.rglob("*"):
        if f.is_file():
            h = hashlib.md5(f.read_bytes()).hexdigest()
            results.append({"path": str(f), "size": f.stat().st_size, "md5": h})
    return results
