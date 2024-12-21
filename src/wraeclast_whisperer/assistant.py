import hashlib
import json

import openai

from wraeclast_whisperer.tools import get_current_temperature, hello_world

_client_instance = None


def get_client() -> openai.AsyncOpenAI:
    global _client_instance
    if _client_instance is None:
        _client_instance = openai.AsyncOpenAI()
    return _client_instance


class AssistantManager:
    name: str
    model: openai.types.ChatModel
    instructions: str
    tools: list[dict]
    assistant: openai.types.beta.Assistant  # type: ignore

    def __init__(self, name: str, model: openai.types.ChatModel, instructions: str, tools=None) -> None:
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.assistant: openai.types.beta.Assistant  # type: ignore

    # TODO: remove type ignore, define openai types aliases
    async def get_or_create_assistant(self) -> openai.types.beta.Assistant:  # type: ignore
        client = get_client()
        # List available assistants
        assistants = await client.beta.assistants.list()

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
        self.assistant = await client.beta.assistants.create(
            name=self.name,
            model=self.model,
            instructions=self.instructions,
            tools=self.tools,
        )
        return self.assistant

    async def setup_assistant(self):
        return await self.get_or_create_assistant()


class ThreadManager:
    def __init__(self, assistant: openai.types.beta.Assistant = None) -> None:
        self.assistant = assistant
        self.thread: openai.types.beta.Thread | None = None

    async def create_thread(self) -> openai.types.beta.Thread:
        client = get_client()
        self.thread = await client.beta.threads.create()
        return self.thread

    async def _submit_message_and_run(self, message: str) -> openai.types.beta.threads.Run:
        client = get_client()
        # Add the user's message to the thread
        await client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message,
        )

        # Create and poll the run
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        return run

    async def _handle_required_action(self, run: openai.types.beta.threads.Run) -> openai.types.beta.threads.Run:
        client = get_client()
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
                        thread_id=self.thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                    )
                    print("Tool outputs submitted successfully.")
                except Exception as e:
                    print("Failed to submit tool outputs:", e)
                    return "Failed to process your request."
            else:
                print("No tool outputs to submit.")
                return "No actions required."
        return run

    async def _fetch_final_response(self, run: openai.types.beta.threads.Run) -> str:
        client = get_client()
        if run.status == "completed":
            print(run.status)
            # Retrieve the assistant's response
            messages = await client.beta.threads.messages.list(thread_id=self.thread.id)
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

    async def conversation_callback(self, message: str) -> str:
        try:
            if not self.thread:
                await self.create_thread()
            run = await self._submit_message_and_run(message)
            run = await self._handle_required_action(run)
            return await self._fetch_final_response(run)
        except AttributeError as e:
            print(f"AttributeError encountered: {e}")
            return "An error occurred while processing the assistant's response."
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "An unexpected error occurred."
