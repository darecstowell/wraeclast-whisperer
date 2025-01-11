import asyncio
import logging
import random
from pathlib import Path
from typing import List

import bcrypt
import chainlit as cl
from chainlit.config import config
from chainlit.data.chainlit_data_layer import ChainlitDataLayer
from chainlit.element import Element
from openai import AsyncOpenAI, OpenAI
from openai.types.beta.threads.runs import RunStep

from app.helpers.assistant import create_assistant
from app.helpers.events import EventHandler
from app.helpers.render import render_template
from app.settings import DATABASE_URL, OPENAI_API_KEY, OPENAI_MODEL
from app.tools import fetch_sitemap, load_page_content, wiki_page, wiki_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
sync_openai_client = OpenAI(api_key=OPENAI_API_KEY)

assistant = create_assistant(
    sync_client=sync_openai_client,
    name="Wraeclast Whisperer",
    model=OPENAI_MODEL,
    instructions=render_template("agent_instructions.jinja2"),
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"},
        {"type": "function", "function": wiki_search.WikiSearch().function_schema},
        {"type": "function", "function": wiki_page.WikiPage().function_schema},
        {"type": "function", "function": fetch_sitemap.FetchSitemap().function_schema},
        {"type": "function", "function": load_page_content.LoadPageContent().function_schema},
    ],
)
config.ui.name = assistant.name or "Wraeclast Whisperer"


async def upload_files(files: List[Element]):
    file_ids = []
    for file in files:
        uploaded_file = await async_openai_client.files.create(file=Path(file.path), purpose="assistants")
        file_ids.append(uploaded_file.id)
    return file_ids


async def process_files(files: List[Element]):
    # TODO: Process images i.e. screenshots of items
    # Upload files if any and get file_ids
    file_ids = []
    if len(files) > 0:
        file_ids = await upload_files(files)

    return [
        {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}, {"type": "file_search"}]
            if file.mime
            in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/markdown",
                "application/pdf",
                "text/plain",
                "text/html",
            ]
            else [{"type": "code_interpreter"}],
        }
        for file_id, file in zip(file_ids, files)
    ]


def generate_starters() -> List[cl.Starter]:
    """
    Generate a list of starters for the user to choose from
    """
    general_questions = [
        "How do I get more spirit?",
        "How many trial parts do you have to get through to get the level 60 ascendancy points?",
        "What is the best way to farm currency?",
        "What is the fastest way to level up?",
        "What is the best way to get exalted orbs?",
        "What is the best way to get chaos orbs?",
        "What is the best way to get alchemy orbs?",
    ]

    endgame_questions = [
        "What's a Citadel?",
    ]

    return [
        cl.Starter(
            label="Ask a general Path of Exile 2 question",
            message=general_questions[random.randint(0, len(general_questions) - 1)],
            icon="/public/write.svg",
        ),
        cl.Starter(
            label="What is the best build for a new player?",
            message="What is the best build for a new player?",
            icon="/public/learn.svg",
        ),
        cl.Starter(
            label="Ask an endgame question",
            message=endgame_questions[random.randint(0, len(endgame_questions) - 1)],
            icon="/public/idea.svg",
        ),
    ]


@cl.set_starters
def starters():
    return generate_starters()


@cl.on_stop
async def stop_chat():
    current_run_step: RunStep = cl.user_session.get("run_step")
    if current_run_step:
        await async_openai_client.beta.threads.runs.cancel(
            thread_id=current_run_step.thread_id, run_id=current_run_step.run_id
        )


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    logger.info(f"Authenticating user: {username}")
    # TODO: probably don't need to re-initalize the data layer every time
    user = asyncio.run(ChainlitDataLayer(DATABASE_URL).get_user(username))
    if not user:
        logger.warning("Authentication failed: user not found")
        return None

    # Compare hashed password
    if bcrypt.checkpw(password.encode("utf-8"), user.metadata["password"].encode("utf-8")):
        logger.info("Authentication successful")
        return cl.User(identifier=username, metadata=user.metadata)
    else:
        logger.warning("Authentication failed: incorrect password")
        return None


@cl.on_message
async def main(message: cl.Message):
    # get or create a thread
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        thread = await async_openai_client.beta.threads.create()
        cl.user_session.set("thread_id", thread.id)
        thread_id = thread.id

    # Process files
    attachments = await process_files(message.elements)

    # Add a Message to the Thread
    await async_openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.content,
        attachments=attachments,
    )

    # Create and Stream a Run
    async with async_openai_client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        event_handler=EventHandler(assistant_name=assistant.name, async_openai_client=async_openai_client),
    ) as stream:
        await stream.until_done()
