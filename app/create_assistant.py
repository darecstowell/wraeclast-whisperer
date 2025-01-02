import os
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI

# Ensure the app directory is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.helpers import render
from app.tools import fetch_sitemap, load_page_content, wiki_page, wiki_search

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def _update_env_file(assistant_id: str) -> None:
    """
    Update the .env file with the assistant id
    """
    env_path = dotenv_path
    with open(env_path, "r") as file:
        content = file.read()
    pattern = r"^OPENAI_ASSISTANT_ID\s*=.*$"
    replacement = f'OPENAI_ASSISTANT_ID = "{assistant_id}"'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count == 0:
        new_content += f"\n{replacement}\n"
    with open(env_path, "w") as file:
        file.write(new_content)


openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = render.render_template("agent_instructions.jinja2")
tools = [
    {"type": "code_interpreter"},
    {"type": "file_search"},
    {"type": "function", "function": wiki_search.WikiSearch().function_schema},
    {"type": "function", "function": wiki_page.WikiPage().function_schema},
    {"type": "function", "function": fetch_sitemap.FetchSitemap().function_schema},
    {"type": "function", "function": load_page_content.LoadPageContent().function_schema},
]
# TODO: is file_search needed?
# TODO: magic string
# file = openai_client.files.create(file=open("../data/all-wiki-pages-12-20-2024.txt", "rb"), purpose="assistants")
assistant = openai_client.beta.assistants.create(
    model="gpt-4o",  # TODO pydantic base settings
    name="Wraeclast Whisperer",
    instructions=instructions,
    temperature=0.1,
    tools=tools,
)

_update_env_file(assistant.id)

print(f"Assistant created with id: {assistant.id} and saved to .env file")
