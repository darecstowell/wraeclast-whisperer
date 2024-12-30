from mediawiki import MediaWiki
from pydantic import BaseModel

from .base import AssistantTool

poe2wiki = MediaWiki(
    url="https://www.poe2wiki.net/api.php",
    user_agent="wraeclast-whisperer/0.0.1 (https://github.com/darecstowell) python-pymediawiki/0.7.4",
)


class Poe2WikiToolParams(BaseModel):
    query: str


class Poe2WikiTool(AssistantTool):
    name: str = "wiki_search"
    friendly_name: str = "PoE2 Wiki Search"
    description: str = "Searches the PoE2 wiki"
    parameters = Poe2WikiToolParams

    def run(self, **kwargs):
        search_term = kwargs.get("query", "")
        if not search_term:
            raise ValueError("Query parameter is required")
        return poe2wiki.search(search_term)
