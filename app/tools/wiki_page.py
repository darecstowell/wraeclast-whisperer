import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.tools.base import AssistantTool

from .base import poe2wiki


class WikiPageParams(BaseModel):
    page_name: str = pydantic.Field(..., description="")


class WikiPage(AssistantTool):
    name: str = "wiki_load_page"
    friendly_name: str = "Wiki Page Loader"
    description: str = render.render_template("wiki_page_description.jinja2")
    parameters = WikiPageParams

    def run(self, **kwargs) -> str:
        page_name = kwargs.get("page_name", "")
        if not page_name:
            raise ValueError("page_name is required")
        # TODO: render template instead
        page = poe2wiki.page(page_name)
        markdown = f"{page.content}\n\n"
        # This is a bit much for now
        # markdown += "## Wiki Page Links \n\n"
        # for link in page.links:
        #     markdown += f"- {link}\n"
        return markdown
