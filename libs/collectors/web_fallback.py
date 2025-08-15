
import time
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent":"b-search/1.0 (+prod)"}

def fetch_static(url: str, timeout: int = 20) -> Optional[Dict]:
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","li","h1","h2","h3"]))[:20000]
    return {"url": url, "text": text}

def fetch_selenium(url: str, wait_css: str = None, timeout: int = 20) -> Optional[Dict]:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    opts = Options()
    opts.add_argument("--headless=new"); opts.add_argument("--no-sandbox"); opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        if wait_css:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_css)))
        time.sleep(1.0)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","li","h1","h2","h3"]))[:20000]
        return {"url": url, "text": text}
    finally:
        driver.quit()

def fetch_with_fallback(url: str, wait_css: str = None, timeout: int = 20):
    try:
        return {"source": "requests", "data": fetch_static(url, timeout)}
    except Exception:
        try:
            return {"source": "selenium", "data": fetch_selenium(url, wait_css, timeout)}
        except Exception as e:
            raise RuntimeError(f"Both static and selenium failed: {e}")
