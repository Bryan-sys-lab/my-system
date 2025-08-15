from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_browser():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)

def render_url(url: str, wait_ms: int = 1500):
    driver = get_browser()
    try:
        driver.get(url)
        driver.implicitly_wait(wait_ms/1000.0)
        html = driver.page_source
        return {"url": url, "html": html}
    finally:
        driver.quit()
