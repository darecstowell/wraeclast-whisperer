import asyncio

from wraeclast_whisperer.assistant import AssistantManager, ThreadManager
from wraeclast_whisperer.helpers import render_template
from wraeclast_whisperer.panel import start_panel_app
from wraeclast_whisperer.settings import MODEL, NAME
from wraeclast_whisperer.tools import get_tools


def main():
    instructions = render_template("agent_instructions.jinja2")
    tools = get_tools()
    assistant_manager = AssistantManager(
        name=NAME,
        model=MODEL,
        instructions=instructions,
        tools=tools,
    )
    assistant = asyncio.run(assistant_manager.setup_assistant())
    thread_manager = ThreadManager(assistant=assistant)
    start_panel_app(thread_manager)


if __name__ == "__main__":
    main()
