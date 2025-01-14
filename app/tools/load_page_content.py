import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.helpers.scrape import get_readable_content, get_robots_txt, is_url_allowed
from app.tools.base import AssistantTool


class LoadPageContentParams(BaseModel):
    url: str = pydantic.Field(..., description="")


class LoadPageContent(AssistantTool):
    name: str = "web_load_page_content"
    friendly_name: str = "Webpage Loader"
    description: str = render.render_template("load_page_content_description.jinja2")
    parameters = LoadPageContentParams

    async def run(self, **kwargs):
        page_url = kwargs.get("url", "")
        if not page_url:
            raise ValueError("url parameter is required")
        robots_txt = get_robots_txt(page_url)
        if not is_url_allowed(page_url, robots_txt):
            raise ValueError(f"Scraping is disallowed by {page_url}")
        result = await get_readable_content(page_url)
        if not result:
            raise ValueError(f"No content found at {page_url}\n Please verify the URL and try again.")
        print(result)
        return result
