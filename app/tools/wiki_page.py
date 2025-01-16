import pydantic
from pydantic import BaseModel

from app.helpers import render
from app.tools.base import AssistantTool

from .base import poe2wiki

def condense_wiki_text(wiki_content: str) -> str:
    """
    Parse and condense wiki content output into paragraphs separated by newlines
    """
    # Split content into paragraphs
    paragraphs = []
    current_para = []
    for line in wiki_content.split('\n'):
        line = line.strip()
        # Skip empty lines and wiki markup
        # 
        if not line or line.startswith('=='):
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
            continue
        current_para.append(line)
    # Add final paragraph if exists
    if current_para:
        paragraphs.append(' '.join(current_para))
    return '\n'.join(paragraphs)


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
        page = poe2wiki.page(page_name)
        return condense_wiki_text(page.content)
