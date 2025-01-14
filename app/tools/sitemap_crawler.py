import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.helpers.scrape import fetch_sitemap_links, get_robots_txt, get_sitemap_links_from_robots_txt, is_url_allowed
from app.tools.base import AssistantTool


class SitemapCrawlerParams(BaseModel):
    get_base_sitemap: bool = pydantic.Field(
        ...,
        description="if True, the tool with fetch the base sitemap for the given URL.",
    )
    sitemap_url: str = pydantic.Field(..., description="")


# TODO: respect crawl delay
class SitemapCrawler(AssistantTool):
    name: str = "web_sitemap_crawler"
    friendly_name: str = "Website Links Finder"
    description: str = render.render_template("sitemap_crawler_description.jinja2")
    parameters = SitemapCrawlerParams

    def run(self, **kwargs) -> str:
        input_url = kwargs.get("sitemap_url", "")
        get_base_sitemap = kwargs.get("get_base_sitemap", False)
        result = {}

        robots_txt = get_robots_txt(input_url)
        if not is_url_allowed(input_url, robots_txt):
            raise ValueError(f"Scraping is disallowed by {input_url}")

        if get_base_sitemap:
            sitemaps = get_sitemap_links_from_robots_txt(robots_txt)
            for sm in sitemaps:
                links = fetch_sitemap_links(sm)
                result[sm] = links
        else:
            if "sitemap.xml" not in input_url:
                raise ValueError("URL does not appear to be a sitemap. Please try again.")
            links = fetch_sitemap_links(input_url)
            result[input_url] = links

        markdown = ""
        for sitemap, links in result.items():
            markdown += f"## Sitemap Links for: {sitemap}\n"
            for link in links:
                markdown += f"- {link}\n"
            markdown += "\n"
        return markdown
