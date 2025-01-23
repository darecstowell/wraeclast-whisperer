import hashlib
import json
from typing import Any

import openai


def _serialize_tools(tools: list) -> list[dict[str, Any]]:
    """
    Convert tool objects (or dicts) to a standardized dict format.
    """
    serialized_tools: list[dict[str, Any]] = []

    for tool in tools:
        # Handle when tool is a dict
        if isinstance(tool, dict):
            tool_type = tool.get("type")
            if tool_type == "function":
                fn = tool.get("function", {})
                serialized_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": fn.get("name"),
                            "description": fn.get("description"),
                            "parameters": fn.get("parameters"),
                            "strict": fn.get("strict"),
                        },
                    }
                )
            else:
                serialized_tools.append({"type": tool_type})
        else:
            # Handle when tool is an object with a .type attribute
            if tool.type == "code_interpreter":
                serialized_tools.append({"type": "code_interpreter"})
            elif tool.type == "file_search":
                serialized_tools.append({"type": "file_search"})
            elif tool.type == "function":
                serialized_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.function.name,
                            "description": tool.function.description,
                            "parameters": tool.function.parameters,
                            "strict": tool.function.strict,
                        },
                    }
                )
            else:
                serialized_tools.append({"type": tool.type})

    return serialized_tools


def _calculate_assistant_data_hash(name: str, model: str, instructions: str, tools: list):
    """
    Calculate a hash of the assistant data to uniquely identify it.
    """
    data = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "tools": _serialize_tools(tools),
    }
    serialized = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def get_or_create_assistant(sync_client: openai.OpenAI, name: str, model: str, instructions: str, tools: list):
    """
    Get an existing assistant with the same data or create a new one if no match
    """
    desired_hash = _calculate_assistant_data_hash(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )
    # List available assistants
    assistants = sync_client.beta.assistants.list(limit=10)
    for assistant in assistants.data:
        existing_hash = _calculate_assistant_data_hash(
            name=assistant.name,
            model=assistant.model,
            instructions=assistant.instructions,
            tools=assistant.tools,
        )
        # Return existing assistant if hashes match
        if existing_hash == desired_hash:
            print(f"Found existing assistant: {name} {assistant.id}")
            return assistant

    print(f"Creating new assistant: {name}")
    # Create new assistant only if no match was found
    return sync_client.beta.assistants.create(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )
