import pydantic
from pydantic import BaseModel

from app.helpers import render

from .base import AssistantTool, poe2wiki


class WikiSearchParams(BaseModel):
    query: str = pydantic.Field(..., description="")


class WikiSearch(AssistantTool):
    name: str = "wiki_search"
    friendly_name: str = "Wiki Search"
    description: str = render.render_template("wiki_search_description.jinja2")
    parameters = WikiSearchParams

    def run(self, **kwargs) -> str:
        search_term = kwargs.get("query", "")
        if not search_term:
            raise ValueError("Query parameter is required")
        results, suggestion = poe2wiki.search(query=search_term, results=5, suggestion=True)
        context = {
            "search_term": search_term,
            "results": results,
            "suggestion": suggestion,
        }
        return render.render_template("wiki_search_results.jinja2", context=context)
