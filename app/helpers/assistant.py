import openai


def _serialize_tools(tools):
    """
    Serialize a list of tools into a format that can be used to create an assistant.
    """
    # Todo: this is not working
    serialized = []
    for tool in tools:
        print(tool)
        serialized_tool = {
            "type": tool["type"],
            "name": tool["name"] if "name" in tool else None,
            "instructions": tool["instructions"] if "instructions" in tool else None,
        }
        serialized.append(serialized_tool)
    return serialized


def create_assistant(sync_client: openai.OpenAI, name: str, model: str, instructions: str, tools: list):
    # # List available assistants
    # assistants = sync_client.beta.assistants.list(limit=10)

    # # Serialize the desired assistant data
    # desired_assistant_data = {
    #     "name": name,
    #     "model": model,
    #     "instructions": instructions,
    #     "tools": _serialize_tools(tools),
    # }
    # desired_serialized = json.dumps(desired_assistant_data, sort_keys=True).encode()
    # desired_hash = hashlib.sha256(desired_serialized).hexdigest()

    # for assistant in assistants.data:
    #     # Serialize existing assistant data
    #     existing_assistant_data = {
    #         "name": assistant.name,
    #         "model": assistant.model,
    #         "instructions": assistant.instructions,
    #         "tools": _serialize_tools(assistant.tools),
    #     }
    #     existing_serialized = json.dumps(existing_assistant_data, sort_keys=True).encode()
    #     existing_hash = hashlib.sha256(existing_serialized).hexdigest()

    #     # Return existing assistant if hashes match
    #     if existing_hash == desired_hash:
    #         print(f"Found existing assistant: {name}")
    #         return assistant

    print(f"Creating new assistant: {name}")
    # Create new assistant only if no match was found
    return sync_client.beta.assistants.create(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )
