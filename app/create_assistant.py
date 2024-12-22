import os

from dotenv import load_dotenv
from helpers import _render
from openai import OpenAI

load_dotenv()

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = _render.render_template("agent_instructions.jinja2")
tools = [{"type": "code_interpreter"}, {"type": "file_search"}]
file = openai_client.files.create(file=open("../data/all-wiki-pages-12-20-2024.txt", "rb"), purpose="assistants")
assistant = openai_client.beta.assistants.create(
    model="gpt-4o",
    name="Wraeclast Whisperer",
    instructions=instructions,
    temperature=0.1,
    tools=tools,
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)

# Add the assistant id to the .env file
with open(".env", "a") as f:
    f.write(f'OPENAI_ASSISTANT_ID = "{assistant.id}"\n')
print(f"Assistant created with id: {assistant.id} and saved to .env file")
