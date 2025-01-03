import hashlib
import json


def _serialize_tools(tools):
    serialized = []
    for tool in tools:
        # If it's already a dict, just use it
        if isinstance(tool, dict):
            serialized.append(tool)
        else:
            # Otherwise, convert it into a simple dict/string
            serialized.append({"type": str(tool.__class__.__name__)})
    return serialized


def create_assistant(client, name: str, model: str, instructions: str, tools: list):
    # List available assistants
    assistants = client.beta.assistants.list()

    serialized_tools = _serialize_tools(tools)

    # Serialize the desired assistant data
    desired_assistant_data = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "tools": serialized_tools,
    }
    desired_serialized = json.dumps(desired_assistant_data, sort_keys=True).encode()
    desired_hash = hashlib.sha256(desired_serialized).hexdigest()

    for assistant in assistants.data:
        # Serialize existing assistant data
        existing_assistant_data = {
            "name": assistant.name,
            "model": assistant.model,
            "instructions": assistant.instructions,
            "tools": _serialize_tools(assistant.tools),
        }
        existing_serialized = json.dumps(existing_assistant_data, sort_keys=True).encode()
        existing_hash = hashlib.sha256(existing_serialized).hexdigest()

        if existing_hash == desired_hash:
            return assistant

    # If assistant does not exist, create a new one
    new_assistant = client.beta.assistants.create(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )
    return new_assistant
