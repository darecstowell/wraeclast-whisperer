from playwright.sync_api import sync_playwright


def get_readable_content(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # Remove unwanted elements
        page.evaluate("""
            for (const tag of document.querySelectorAll('script, style, nav, header, footer, ads')) {
                tag.remove();
            }
        """)
        # Try to find the main content
        article_selector = "article, main, .content"
        main_content = page.query_selector(article_selector)
        if not main_content:
            browser.close()
            return ""
        content = page.evaluate("(main_content) => main_content.innerText", main_content)
        browser.close()
        return content
