import os
import re

from dotenv import load_dotenv
from helpers import _render
from openai import OpenAI

load_dotenv()

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = _render.render_template("agent_instructions.jinja2")
tools = [{"type": "code_interpreter"}, {"type": "file_search"}]  # TODO create tools abc
# TODO: is this needed?
file = openai_client.files.create(file=open("../data/all-wiki-pages-12-20-2024.txt", "rb"), purpose="assistants")
assistant = openai_client.beta.assistants.create(
    model="gpt-4o",  # TODO pydantic base settings
    name="Wraeclast Whisperer",
    instructions=instructions,
    temperature=0.1,
    tools=tools,
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)

# Add the assistant id to the .env file
# Overwrite the OPENAI_ASSISTANT_ID in the .env file if it already exists
with open(".env", "a") as f:
    env_path = ".env"
    with open(env_path, "r") as file:
        content = file.read()
    pattern = r"^OPENAI_ASSISTANT_ID\s*=.*$"
    replacement = f'OPENAI_ASSISTANT_ID = "{assistant.id}"'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count == 0:
        new_content += f"\n{replacement}\n"
    with open(env_path, "w") as file:
        file.write(new_content)

print(f"Assistant created with id: {assistant.id} and saved to .env file")
