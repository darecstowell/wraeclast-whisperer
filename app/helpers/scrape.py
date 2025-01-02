from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
from playwright.async_api import async_playwright

# TODO: get from settings
_user_agent = "wraeclast-whisperer/0.0.1 (https://github.com/darecstowell) python-pymediawiki/0.7.4"


def get_robots_txt(url: str) -> str:
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Fetching robots.txt from: {base_url}")
    try:
        response = requests.get(base_url, headers={"User-Agent": _user_agent}, timeout=5)
        if response.ok:
            return response.text
    except requests.RequestException:
        pass
    return ""


def is_url_allowed(url: str, robots_txt: str) -> bool:
    """
    Check if the given URL is allowed for user-agent '*'
    based on the provided robots.txt content.
    If no robots.txt exists, disallow all URLs by returning False.
    """
    if not robots_txt.strip():
        return False

    parsed_url = urlparse(url)
    path = parsed_url.path
    lines = robots_txt.splitlines()

    user_agent_line_found = False
    disallowed_paths: list[str] = []

    for line in lines:
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            user_agent_line_found = agent == "*"
            disallowed_paths = [] if user_agent_line_found else disallowed_paths
        elif user_agent_line_found and line.lower().startswith("disallow:"):
            dp = line.split(":", 1)[1].strip()
            disallowed_paths.append(dp)

    for dp in disallowed_paths:
        if dp.endswith("*"):
            dp = dp[:-1]
            if dp and path.startswith(dp):
                return False
            elif not dp:  # "Disallow: *" means disallow all
                return False
        else:
            if path.startswith(dp):
                return False
    return True


def get_crawl_delay(robots_txt: str, user_agent: str = "*") -> float:
    """
    Extract the crawl delay (if any) for the given user agent.
    If not under that agent, fall back to any top-level crawl delay.
    Returns 0.0 if none is specified.
    """
    lines = robots_txt.splitlines()
    general_delay = 0.0
    current_agent_found = False

    for line in lines:
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agent_found = agent == user_agent
        elif line.lower().startswith("crawl-delay:"):
            val = line.split(":", 1)[1].strip()
            try:
                delay = float(val)
            except ValueError:
                delay = 0.0

            if current_agent_found:
                return delay
            else:
                # Take note of this as a fallback
                general_delay = delay

    return general_delay


def get_sitemap_links_from_robots_txt(robots_txt: str) -> list:
    """
    Extract all sitemap URLs from the robots.txt content.
    """
    sitemaps = []
    lines = robots_txt.splitlines()
    for line in lines:
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            sitemap_url = line.split(":", 1)[1].strip()
            sitemaps.append(sitemap_url)
    return sitemaps


def fetch_sitemap_links(sitemap_url: str) -> list:
    """
    Fetch and parse the sitemap XML to extract all URLs.
    """
    try:
        response = requests.get(sitemap_url, headers={"User-Agent": _user_agent}, timeout=5)
        if response.ok:
            tree = ElementTree.fromstring(response.content)
            return [elem.text for elem in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    except requests.RequestException:
        pass
    return []


async def get_readable_content(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        # Remove unwanted elements
        await page.evaluate("""
            for (const tag of document.querySelectorAll('script, style, nav, header, footer, ads')) {
                tag.remove();
            }
        """)
        # Try to find the main content
        article_selector = "article, main, .content"
        main_content = await page.query_selector(article_selector)
        if not main_content:
            await browser.close()
            return ""
        content = await page.evaluate("(main_content) => main_content.innerText", main_content)
        await browser.close()
        print(f"Content : {content}")
        return content
