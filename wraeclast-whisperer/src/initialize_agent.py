import asyncio

from helpers import AssistantManager, render_template
from tools import get_tools


# TODO: move this to scripts?
async def main():
    # Define assistant parameters
    name = "Wraeclast Whisperer"
    model = "gpt-4o-mini"
    instructions = render_template("agent_instructions.jinja2")
    tools = get_tools()

    # Instantiate the AssistantManager
    assistant_manager = AssistantManager(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
    )

    # Setup the assistant
    assistant = await assistant_manager.setup_assistant()

    # TODO: add thread manager

    # TODO: load panel app


if __name__ == "__main__":
    asyncio.run(main())
