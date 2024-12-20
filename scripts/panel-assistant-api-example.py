"""
Panel Assistant API Example Script

This script integrates OpenAI's assistant with a Panel-based web interface, allowing users to interact
with a custom assistant through a chat interface. It demonstrates creating or retrieving an assistant,
defining custom tools, and handling asynchronous API interactions.
"""

import asyncio
import hashlib
import json

import openai
import panel as pn

client = openai.AsyncOpenAI()


def create_thread():
    """
    Create a new thread.
    """
    # !Avoid global variables in production code
    global thread
    thread = asyncio.run(client.beta.threads.create())


async def create_assistant(name: str, model: str, instructions: str, tools: list = []):
    """
    Create a new assistant or retrieve an existing one with the same data.
    """

    # List available assistants
    assistants = await client.beta.assistants.list()

    # Serialize the desired assistant data including tools
    desired_assistant_data = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "tools": tools,
    }
    desired_serialized = json.dumps(desired_assistant_data, sort_keys=True).encode()
    desired_hash = hashlib.sha256(desired_serialized).hexdigest()

    for assistant in assistants.data:
        # Serialize existing assistant data including tools as dictionaries
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
            return assistant

    # If assistant does not exist, create a new one with tools
    new_assistant = await client.beta.assistants.create(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )
    return new_assistant


def setup_assistant():
    """
    Setup the assistant with the desired data and tools for this example.
    """
    # !Avoid global variables in production code
    global assistant
    assistant = asyncio.run(
        create_assistant(
            name="PanelExample",
            model="gpt-4o-mini",
            instructions="You are an example assistant.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "hello_world",
                        "description": "Returns a greeting message.",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_temperature",
                        "description": "Returns the current temperature.",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
            ],
        )
    )


async def hello_world():
    """
    Returns a greeting message.
    """

    print("Called hello_world")
    return "hello world"


async def get_current_temperature():
    """
    Returns the current temperature
    """

    print("Called get_current_temperature")
    return "The current temperature is 72°F."


async def assistant_callback(message: str):
    """
    Callback function to interact with the assistant.
    """

    try:
        # Add the user's message to the thread
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )

        # Create and poll the run
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Define the list to store tool outputs
        tool_outputs = []

        # Check if required_action is present
        if run.status == "requires_action" and run.required_action and run.required_action.submit_tool_outputs:
            # Loop through each tool in the required action section
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "hello_world":
                    tool_outputs.append({"tool_call_id": tool.id, "output": await hello_world()})
                elif tool.function.name == "get_current_temperature":
                    tool_outputs.append({"tool_call_id": tool.id, "output": await get_current_temperature()})

            # Submit all tool outputs at once after collecting them in a list
            if tool_outputs:
                try:
                    run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )
                    print("Tool outputs submitted successfully.")
                except Exception as e:
                    print("Failed to submit tool outputs:", e)
                    return "Failed to process your request."
            else:
                print("No tool outputs to submit.")
                return "No actions required."

        if run.status == "completed":
            print(run.status)
            # Retrieve the assistant's response
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            # print(messages)
            # Find the assistant's message
            assistant_message = None
            for msg in messages.data:
                if msg.role == "assistant":
                    assistant_message = msg.content[0]
                    break
            # Extract the text content from the TextContentBlock object
            if isinstance(assistant_message, openai.types.beta.threads.message_content.TextContentBlock):
                assistant_message = assistant_message.text.value
            return assistant_message
        else:
            print(run.status)
            return "The assistant is still processing your request."

    except AttributeError as e:
        print(f"AttributeError encountered: {e}")
        return "An error occurred while processing the assistant's response."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred."


if __name__ == "__main__":
    # Set up the chat interface and serve the panel app
    pn.extension()
    pn.state.execute(setup_assistant)
    pn.state.execute(create_thread)
    chat_interface = pn.chat.ChatInterface(
        callback=assistant_callback,
        callback_user="PanelExample",
        help_text="Send a message to interact with the PanelExample assistant!",
    )
    template = pn.template.FastListTemplate(
        title="OpenAI Assistant - PanelExample",
        header_background="#212121",
        main=[chat_interface],
    )
    template.servable()
    pn.serve(
        template,
        port=5007,
        host="0.0.0.0",
        websocket_origin=["localhost:5007", "127.0.0.1:5007"],
        show=True,
    )
