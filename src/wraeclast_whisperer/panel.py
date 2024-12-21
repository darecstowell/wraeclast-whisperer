import panel as pn

from wraeclast_whisperer.assistant import ThreadManager
from wraeclast_whisperer.settings import CALLBACK_USER, TEMPLATE_TITLE


def start_panel_app(thread_manager: ThreadManager):
    pn.extension()

    async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        return await thread_manager.conversation_callback(contents)

    chat = pn.chat.ChatInterface(
        callback=callback,
        callback_user=CALLBACK_USER,
    )
    template = pn.template.FastListTemplate(
        title=TEMPLATE_TITLE,
        main=[chat],
    )
    # pn.serve(
    #     template,
    #     port=PORT,
    #     host=HOST,
    #     websocket_origin=WEBSOCKET_ORIGINS,
    #     show=SHOW_PANEL,
    # )

    pn.serve(
        template,
        port=5007,
        host="0.0.0.0",
        websocket_origin=["localhost:5007", "127.0.0.1:5007"],
        show=True,
    )
