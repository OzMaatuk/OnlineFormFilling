# driver.py

from playwright.sync_api import sync_playwright
from playwright.sync_api import BrowserContext

def initialize_driver(headless: bool = True, user_data_dir: str = "") -> BrowserContext:
    playwright = sync_playwright().start()
    browser = playwright.webkit.launch_persistent_context(
                # user_data_dir=user_data_dir,
                headless=headless)
    return browser
