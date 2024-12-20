import hashlib
import json
import os

import jinja2
import openai


def render_template(template_name: str = "instructions.jinja") -> str:
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the templates directory
    templates_dir = os.path.join(script_dir, "..", "templates")
    # Load and render the instructions template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    instructions = template.render()
    return instructions


class AssistantManager:
    def __init__(self, name, model, instructions, tools=None):
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.client = openai.AsyncOpenAI()
        self.assistant = None

    async def get_or_create_assistant(self):
        # List available assistants
        assistants = await self.client.beta.assistants.list()

        # Serialize the desired assistant data including tools
        desired_assistant_data = {
            "name": self.name,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools,
        }
        desired_serialized = json.dumps(desired_assistant_data, sort_keys=True).encode()
        desired_hash = hashlib.sha256(desired_serialized).hexdigest()

        for assistant in assistants.data:
            # Serialize existing assistant data including tools
            existing_assistant_data = {
                "name": assistant.name,
                "model": assistant.model,
                "instructions": assistant.instructions,
                "tools": [
                    {
                        "type": tool.type,
                        "function": {
                            "name": tool.function.name,
                            "description": tool.function.description,
                            "parameters": tool.function.parameters,
                        },
                    }
                    for tool in assistant.tools
                ],
            }
            existing_serialized = json.dumps(existing_assistant_data, sort_keys=True).encode()
            existing_hash = hashlib.sha256(existing_serialized).hexdigest()

            if existing_hash == desired_hash:
                self.assistant = assistant
                return self.assistant

        # Create a new assistant if none match
        self.assistant = await self.client.beta.assistants.create(
            name=self.name,
            model=self.model,
            instructions=self.instructions,
            tools=self.tools,
        )
        return self.assistant

    async def setup_assistant(self):
        return await self.get_or_create_assistant()
