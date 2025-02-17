# file path: tests\conftest.py

import os
import logging
import pytest
import threading
import time
import configparser
from typing import Generator
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright, BrowserContext, Page, ElementHandle
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch
from llm_utils import LLMUtils


logger = logging.getLogger(__name__)

class ServerThread(threading.Thread):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def run(self):
        print("Starting server...")
        self.server.serve_forever()

    def shutdown(self):
        print("Shutting down server...")
        self.server.shutdown()

@pytest.fixture(scope="session")
def config():
    config = configparser.ConfigParser()
    config.read('pytest.ini')
    return config

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
    yield

@pytest.fixture(scope="session")
def web_server() -> Generator[None, None, None]:
    site_dir = os.path.join(os.getcwd(), 'tests/')
    handler = SimpleHTTPRequestHandler
    handler.directory = site_dir
    httpd = TCPServer(("localhost", 8000), handler)
    server_thread = ServerThread(httpd)
    logger.info("Starting web server...")
    server_thread.start()
    time.sleep(3)  # Give the server time to start
    logger.info("Web server started.")
    yield
    logger.info("Shutting down web server...")
    server_thread.shutdown()
    server_thread.join()
    logger.info("Web server shut down.")

@pytest.fixture(scope="session")
def playwright_instance(web_server) -> Generator:
    logger.info("Starting Playwright instance...")
    instance = sync_playwright().start()
    yield instance
    logger.info("Stopping Playwright instance...")
    instance.stop()
    logger.info("Playwright instance stopped.")

@pytest.fixture(scope="session")
def playwright_browser(playwright_instance) -> Generator[BrowserContext, None, None]:
    try:
        logger.info("Launching persistent Playwright browser context...")
        browser_context = playwright_instance.webkit.launch(headless=False)
        logger.info("Persistent browser context launched successfully.")
        yield browser_context
        logger.info("Closing persistent browser context...")
        browser_context.close()
        logger.info("Persistent browser context closed.")
    except Exception as e:
        logger.error(f"Failed to launch persistent browser context: {e}")
        raise

@pytest.fixture(scope="function")
def form_page(playwright_browser: BrowserContext) -> Generator[Page, None, None]:
    page = playwright_browser.new_page()
    logger.info("Navigating to test page...")
    page.goto("http://127.0.0.1:8000/tests/index.html")
    logger.info("Test page loaded successfully.")
    yield page
    page.close()

@pytest.fixture
def mock_llm():
    return MagicMock(spec=LLMUtils)

@pytest.fixture
def form_filling(mock_llm):
    return FormFilling(llm=mock_llm, resume_content=MOCK_RESUME_CONTENT)

@pytest.fixture
def form_filling_with_path(mock_llm):
    return FormFilling(llm=mock_llm, resume_path=MOCK_RESUME_PATH)

@pytest.fixture
def mock_element():
    element = MagicMock(spec=ElementHandle)
    element.get_attribute.side_effect = lambda attr: {
        "name": "test_field",
        "id": "test_id",
        "aria-label": "Test Label"
    }.get(attr)
    element.evaluate.return_value = "text"
    return element
