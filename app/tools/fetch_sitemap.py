import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.helpers.scrape import fetch_sitemap_links, get_robots_txt, get_sitemap_links_from_robots_txt, is_url_allowed
from app.tools.base import AssistantTool


class FetchSitemapParams(BaseModel):
    use_robots_txt: bool = pydantic.Field(
        ...,
        description="If true, the tool will use the robots.txt file to find the root sitemap. If false, the tool will use the URL parameter to fetch a sitemap directly.",
    )
    sitemap_url: str = pydantic.Field(..., description="")


# TODO: respect crawl delay
class FetchSitemap(AssistantTool):
    name: str = "fetch_sitemap"
    friendly_name: str = "Sitemap Fetcher"
    description: str = render.render_template("fetch_sitemap_description.jinja2")
    parameters = FetchSitemapParams

    def run(self, **kwargs) -> dict:
        input_url = kwargs.get("sitemap_url", "")
        use_robots_txt = kwargs.get("use_robots_txt", False)
        result = {}

        robots_txt = get_robots_txt(input_url)
        if not is_url_allowed(input_url, robots_txt):
            raise ValueError(f"Scraping is disallowed by {input_url}")

        if use_robots_txt:
            sitemaps = get_sitemap_links_from_robots_txt(robots_txt)
            for sm in sitemaps:
                links = fetch_sitemap_links(sm)
                result[sm] = links
        else:
            if "sitemap.xml" not in input_url:
                raise ValueError("URL does not appear to be a sitemap")
            links = fetch_sitemap_links(input_url)
            result[input_url] = links
        return result
