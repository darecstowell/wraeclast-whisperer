from mediawiki import MediaWiki

from app.tools.base import AssistantTool

poe2wiki = MediaWiki(
    url="https://www.poe2wiki.net/api.php",
    user_agent="wraeclast-whisperer/0.0.1 (https://github.com/darecstowell) python-pymediawiki/0.7.4",
)


class Poe2WikiTool(AssistantTool):
    name: str = "poe2_wiki_tool"
    description: str = "Searches the PoE2 wiki"
    strict: bool = True
    # todo pydatnic schema
    parameters: dict = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "A search term for the wiki"}},
        "required": ["query"],
        "additionalProperties": False,
    }

    def run(self, **kwargs):
        search_term = kwargs.get("query", "")
        return poe2wiki.search(search_term)
