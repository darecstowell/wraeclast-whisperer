import asyncio

import openai
import panel as pn

pn.extension()

# Initialize OpenAI API client
client = openai.AsyncOpenAI()


# Create the assistant
async def create_assistant():
    return await client.beta.assistants.create(
        name="PanelExample",
        instructions="You are a helpful assistant named PanelExample.",
        model="gpt-4o-2024-11-20",
    )


def setup_assistant():
    global assistant
    assistant = asyncio.run(create_assistant())


pn.state.execute(setup_assistant)


async def assistant_callback(message: str):
    # Create a new thread
    thread = await client.beta.threads.create()
    # Add the user's message to the thread
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )
    # Run the assistant on the thread
    await client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    # Retrieve the assistant's response
    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)
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

# Serve the Panel app
pn.serve(
    template,
    port=5007,
    websocket_origin=["localhost:5007", "0.0.0.0:5007"],
    show=True,
)
