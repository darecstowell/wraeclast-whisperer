import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.tools.base import AssistantTool

from .base import poe2wiki


class WikiPageParams(BaseModel):
    page_name: str = pydantic.Field(..., description="")


class WikiPage(AssistantTool):
    name: str = "wiki_page"
    friendly_name: str = "PoE2 Wiki Load Page"
    description: str = render.render_template("wiki_page_description.jinja2")
    parameters = WikiPageParams

    def run(self, **kwargs):
        page_name = kwargs.get("page_name", "")
        if not page_name:
            raise ValueError("page_name is required")
        page = poe2wiki.page(page_name)
        # TODO render as markdown using template instead
        result_lines = [
            "== Title ==",
            page.title,
            "== Summary ==",
            page.summary,
            page.content,
            "== Links ==",
            str(page.links),
        ]
        return "\n".join(result_lines)
