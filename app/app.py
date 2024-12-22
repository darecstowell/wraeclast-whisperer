import os
from pathlib import Path
from typing import List

import chainlit as cl
from chainlit.config import config
from chainlit.element import Element
from helpers.events import EventHandler
from openai import AsyncOpenAI, OpenAI
from openai.types.beta.threads.runs import RunStep

async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

assistant = sync_openai_client.beta.assistants.retrieve(os.environ.get("OPENAI_ASSISTANT_ID"))

config.ui.name = assistant.name


@cl.step(type="tool")
async def speech_to_text(audio_file):
    response = await async_openai_client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    return response.text


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
    return [
        cl.Starter(
            label="Run Tesla stock analysis",
            message="Make a data analysis on the tesla-stock-price.csv file I previously uploaded.",
            icon="/public/write.svg",
        ),
        cl.Starter(
            label="Run a data analysis on my CSV",
            message="Make a data analysis on the next CSV file I will upload.",
            icon="/public/write.svg",
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
