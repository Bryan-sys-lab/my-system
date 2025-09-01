try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.chrome.options import Options  # type: ignore

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
            driver.implicitly_wait(wait_ms / 1000.0)
            html = driver.page_source
            return {"url": url, "html": html}
        finally:
            driver.quit()
except Exception:
    # Selenium isn't available in lightweight test environments. Provide a
    # fallback stub so importing the module doesn't fail; callers will get a
    # clear runtime error if they try to use rendering.
    def render_url(url: str, wait_ms: int = 1500):
        raise RuntimeError("selenium is not installed or not available in this environment")
