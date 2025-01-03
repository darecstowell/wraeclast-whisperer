import os
import random
from pathlib import Path
from typing import List

import chainlit as cl
from chainlit.config import config
from chainlit.element import Element
from openai import AsyncOpenAI, OpenAI
from openai.types.beta.threads.runs import RunStep

from app.helpers.assistant import create_assistant
from app.helpers.events import EventHandler
from app.helpers.render import render_template
from app.tools import fetch_sitemap, load_page_content, wiki_page, wiki_search

async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

assistant = create_assistant(
    sync_client=sync_openai_client,
    name="Wraeclast Whisperer",
    model="gpt-4o-2024-11-20",
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
            ]
            else [{"type": "code_interpreter"}],
        }
        for file_id, file in zip(file_ids, files)
    ]


@cl.set_starters
async def set_starters():
    general_questions = [
        "How many trial parts do you have to get through to get the level 60 ascendancy points?",
        "What is the best way to farm currency?",
        "What is the fastest way to level up?",
        "What is the best way to get maps?",
        "What is the best way to get currency?",
        "What is the best way to get exalted orbs?",
        "What is the best way to get chaos orbs?",
        "What is the best way to get alchemy orbs?",
    ]

    return [
        # TODO: have the message pick at random from a list of questions
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
    ]


@cl.on_chat_start
async def start_chat():
    # Create a Thread
    thread = await async_openai_client.beta.threads.create()
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", thread.id)


@cl.on_stop
async def stop_chat():
    current_run_step: RunStep = cl.user_session.get("run_step")
    if current_run_step:
        await async_openai_client.beta.threads.runs.cancel(
            thread_id=current_run_step.thread_id, run_id=current_run_step.run_id
        )


@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    attachments = await process_files(message.elements)

    # Add a Message to the Thread
    oai_message = await async_openai_client.beta.threads.messages.create(
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
