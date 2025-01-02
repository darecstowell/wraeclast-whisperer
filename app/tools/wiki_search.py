from app.helpers import render
from pydantic import BaseModel

from .base import AssistantTool, poe2wiki


class WikiSearchParams(BaseModel):
    query: str


class WikiSearch(AssistantTool):
    name: str = "wiki_search"
    friendly_name: str = "PoE2 Wiki Search"
    description: str = render.render_template("wiki_search_description.jinja2")
    parameters = WikiSearchParams

    def run(self, **kwargs):
        search_term = kwargs.get("query", "")
        if not search_term:
            raise ValueError("Query parameter is required")
        return poe2wiki.search(query=search_term, results=5, suggestion=True)
