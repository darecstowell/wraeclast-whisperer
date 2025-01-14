import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.helpers.scrape import fetch_sitemap_links, get_robots_txt, is_url_allowed
from app.tools.base import AssistantTool


class FetchSitemapParams(BaseModel):
    sitemap_url: str = pydantic.Field(..., description="")


class FetchSitemap(AssistantTool):
    name: str = "web_fetch_sitemap"
    friendly_name: str = "Website Links Finder"
    description: str = render.render_template("fetch_sitemap_description.jinja2")
    parameters = FetchSitemapParams

    def run(self, **kwargs) -> str:
        input_url = kwargs.get("sitemap_url", "")
        result = {}

        robots_txt = get_robots_txt(input_url)
        if not is_url_allowed(input_url, robots_txt):
            raise ValueError(f"Scraping is disallowed by {input_url}")

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
