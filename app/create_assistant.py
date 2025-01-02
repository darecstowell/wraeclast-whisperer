import os
import re

from dotenv import load_dotenv
from helpers import render
from openai import OpenAI
from tools import wiki_page, wiki_search


def _update_env_file(assistant_id: str) -> None:
    """
    Update the .env file with the assistant id
    """
    env_path = ".env"
    with open(env_path, "r") as file:
        content = file.read()
    pattern = r"^OPENAI_ASSISTANT_ID\s*=.*$"
    replacement = f'OPENAI_ASSISTANT_ID = "{assistant_id}"'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count == 0:
        new_content += f"\n{replacement}\n"
    with open(env_path, "w") as file:
        file.write(new_content)


load_dotenv()

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = render.render_template("agent_instructions.jinja2")
tools = [
    {"type": "code_interpreter"},
    {"type": "file_search"},
    {"type": "function", "function": wiki_search.WikiSearch().function_schema},
    {"type": "function", "function": wiki_page.WikiPage().function_schema},
]
# TODO: is file_search needed?
# TODO: magic string
file = openai_client.files.create(file=open("../data/all-wiki-pages-12-20-2024.txt", "rb"), purpose="assistants")
assistant = openai_client.beta.assistants.create(
    model="gpt-4o",  # TODO pydantic base settings
    name="Wraeclast Whisperer",
    instructions=instructions,
    temperature=0.1,
    tools=tools,
)

_update_env_file(assistant.id)

print(f"Assistant created with id: {assistant.id} and saved to .env file")
