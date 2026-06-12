from __future__ import annotations
from typing import Callable, Any
from playwright.async_api import async_playwright


async def crawl_with_playwright(url: str, wait_selector: str, extract_fn: Callable[[str], Any], timeout: int = 30000) -> Any:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_selector(wait_selector, timeout=timeout)
        html = await page.content()
        await browser.close()
    return extract_fn(html)
