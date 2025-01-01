from urllib.parse import urlparse
from xml.etree import ElementTree

import requests


def get_robots_txt(url: str) -> str:
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Fetching robots.txt from: {base_url}")
    try:
        response = requests.get(base_url, timeout=5)
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


def get_sitemap_links(robots_txt: str) -> list:
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
        response = requests.get(sitemap_url, timeout=5)
        if response.ok:
            tree = ElementTree.fromstring(response.content)
            return [elem.text for elem in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    except requests.RequestException:
        pass
    return []


# Allowed URL
allowed_url = "https://maxroll.gg/poe2/build-guides/lightning-arrow-deadeye"
robots_txt = get_robots_txt(allowed_url)
print(f"Is Build Guide URL allowed: {is_url_allowed(allowed_url, robots_txt)}")

# Crawl Delay
print("Crawl delay for Maxroll:", get_crawl_delay(robots_txt))
print()

# Disallowed URL
disallowed_url = "https://maxroll.gg/d4/planner/8niw00kp"
print(f"Is D4 Planner URL allowed: {is_url_allowed(disallowed_url, robots_txt)}")
print()

# Unreachable Robots.txt
fextralife_url = "https://fextralife.com/path-of-exile-2-monk-starter-guide-how-to-build-a-monk/"
unable_to_load_robots_txt = get_robots_txt(fextralife_url)
print(f"Is Fextralife URL allowed: {is_url_allowed(fextralife_url, unable_to_load_robots_txt)}")
print()

# Site Map Links
sitemaps = get_sitemap_links(robots_txt)
all_links = []
for mobalytics_sitemap in sitemaps:
    all_links.extend(fetch_sitemap_links(mobalytics_sitemap))

print("All links from Maxroll sitemap:", all_links)
print()

print("All links from Maxroll Poe2 sitemap:")
poe2_sitemap = "https://maxroll.gg/poe2/sitemap.xml"
print(fetch_sitemap_links(poe2_sitemap))
print()

# Mobalytics
mobalytics_url = "https://mobalytics.gg/poe-2"
mobalytics_robots = get_robots_txt(mobalytics_url)
print(f"Is Mobalytics URL allowed: {is_url_allowed(mobalytics_url, mobalytics_robots)}")

# Crawl Delay
print("Crawl delay for Mobalytics:", get_crawl_delay(mobalytics_robots))
print()

# Sitemap Links
mobalytics_sitemaps = get_sitemap_links(mobalytics_robots)
print("Mobalytics sitemap link:", mobalytics_sitemaps)
print()

# Site Map Links
mobalytics_sitemaps = get_sitemap_links(mobalytics_robots)
all_links = []
for mobalytics_sitemap in mobalytics_sitemaps:
    all_links.extend(fetch_sitemap_links(mobalytics_sitemap))

print("All links from Mobalytics sitemap:", all_links)
print()

# TODO: use beautifulsoup to scrape a webpage
