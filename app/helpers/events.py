import json

import chainlit as cl
from literalai.helper import utc_now
from openai import AsyncAssistantEventHandler, AsyncOpenAI
from openai.types.beta.threads.runs import RunStep


class EventHandler(AsyncAssistantEventHandler):
    def __init__(self, assistant_name: str, async_openai_client: AsyncOpenAI) -> None:
        super().__init__()
        self.current_message: cl.Message = None
        self.current_step: cl.Step = None
        self.current_tool_call = None
        self.assistant_name = assistant_name
        self.async_openai_client = async_openai_client

        # Track processed tool call IDs to avoid double-calls
        self.processed_calls = set()
        self.processed_snapshots = set()

    async def on_run_step_created(self, run_step: RunStep) -> None:
        cl.user_session.set("run_step", run_step)

    async def on_text_created(self, text) -> None:
        self.current_message = await cl.Message(author=self.assistant_name, content="").send()

    async def on_text_delta(self, delta, snapshot):
        if delta.value:
            await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        await self.current_message.update()
        # TODO: render stuff?
        # if text.annotations:
        #     for annotation in text.annotations:
        #         if annotation.type == "file_path":
        #             response = await self.async_openai_client.files.with_raw_response.content(
        #                 annotation.file_path.file_id
        #             )
        #             file_name = annotation.text.split("/")[-1]
        #             try:
        #                 fig = plotly.io.from_json(response.content)
        #                 element = cl.Plotly(name=file_name, figure=fig)
        #                 await cl.Message(content="", elements=[element]).send()
        #             except Exception:
        #                 element = cl.File(content=response.content, name=file_name)
        #                 await cl.Message(content="", elements=[element]).send()
        #             Hack to fix links
        #             if annotation.text in self.current_message.content and element.chainlit_key:
        #                 self.current_message.content = self.current_message.content.replace(
        #                     annotation.text, f"/project/file/{element.chainlit_key}?session_id={cl.context.session.id}"
        #                 )
        #                 await self.current_message.update()

    async def on_tool_call_created(self, tool_call):
        from app.tools import fetch_sitemap, load_page_content, wiki_page, wiki_search

        print(f"Tool Call: {tool_call.id}")

        # Skip if we've already processed this call ID
        if tool_call.id in self.processed_calls:
            return

        self.processed_calls.add(tool_call.id)

        wiki_search_instance = wiki_search.WikiSearch()
        wiki_page_instance = wiki_page.WikiPage()
        fetch_sitemap_instance = fetch_sitemap.FetchSitemap()
        load_page_content_instance = load_page_content.LoadPageContent()
        self.current_tool_call = tool_call.id
        if hasattr(tool_call, "function"):
            if tool_call.function.name == wiki_search_instance.name:
                friendly_name = wiki_search.WikiSearch().friendly_name
            elif tool_call.function.name == wiki_page_instance.name:
                friendly_name = wiki_page.WikiPage().friendly_name
            elif tool_call.function.name == fetch_sitemap_instance.name:
                friendly_name = fetch_sitemap.FetchSitemap().friendly_name
            elif tool_call.function.name == load_page_content_instance.name:
                friendly_name = load_page_content.LoadPageContent().friendly_name
            self.current_step = cl.Step(name=friendly_name, type="tool", parent_id=cl.context.current_run.id)
        else:
            self.current_step = cl.Step(name=tool_call.type, type="tool", parent_id=cl.context.current_run.id)
        self.current_step.start = utc_now()
        await self.current_step.send()

    async def on_tool_call_delta(self, delta, snapshot):
        # Avoid reprocessing the same snapshot
        if snapshot.id in self.processed_snapshots:
            return
        self.processed_snapshots.add(snapshot.id)

        if snapshot.id != self.current_tool_call:
            self.current_tool_call = snapshot.id
            self.current_step = cl.Step(name=delta.type, type="tool", parent_id=cl.context.current_run.id)
            self.current_step.start = utc_now()
            if snapshot.type == "code_interpreter":
                self.current_step.show_input = "python"
            if snapshot.type == "function":
                self.current_step.name = snapshot.function.name
                self.current_step.language = "json"
            await self.current_step.update()

        if delta.type == "function":
            pass

        if delta.type == "code_interpreter":
            if delta.code_interpreter.outputs:
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.current_step.output += output.logs
                        self.current_step.language = "markdown"
                        self.current_step.end = utc_now()
                        await self.current_step.update()
                    elif output.type == "image":
                        self.current_step.language = "json"
                        self.current_step.output = output.image.model_dump_json()
            else:
                if delta.code_interpreter.input:
                    await self.current_step.stream_token(delta.code_interpreter.input, is_input=True)

    async def on_event(self, event) -> None:
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            await self.handle_requires_action(event.data, run_id)
        if event.event == "error":
            print(event.data.message)
            return cl.ErrorMessage(content=str(event.data.message)).send()

    async def on_exception(self, exception: Exception) -> None:
        print(exception)
        return cl.ErrorMessage(content=str(exception)).send()

    async def on_tool_call_done(self, tool_call):
        self.current_step.end = utc_now()
        await self.current_step.update()

    async def handle_requires_action(self, data, run_id):
        from app.tools import fetch_sitemap, load_page_content, wiki_page, wiki_search

        wiki_search_instance = wiki_search.WikiSearch()
        wiki_page_instance = wiki_page.WikiPage()
        fetch_sitemap_instance = fetch_sitemap.FetchSitemap()
        load_page_content_instance = load_page_content.LoadPageContent()
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if hasattr(tool, "function"):
                args = tool.function.arguments
                if isinstance(args, str):
                    args = json.loads(args or "{}")
                try:
                    print(f"Running tool: {tool.function.name} with args: {args}")
                    if tool.function.name == wiki_search_instance.name:
                        function_response = wiki_search_instance.run(**args)
                    elif tool.function.name == wiki_page_instance.name:
                        # self.current_step.name = f"Wiki Page: {args.get('page_name')}"
                        function_response = wiki_page_instance.run(**args)
                    elif tool.function.name == fetch_sitemap_instance.name:
                        # self.current_step.name = f"Fetched Sitemap for: {args.get('sitemap_url')}"
                        function_response = fetch_sitemap_instance.run(**args)
                    elif tool.function.name == load_page_content_instance.name:
                        # self.current_step.name = f"Load Page Content for: {args.get('url')}"
                        function_response = await load_page_content_instance.run(**args)
                    self.current_step.show_input = "json"
                    self.current_step.input = args
                    self.current_step.output = function_response
                    self.current_step.language = "markdown"
                    tool_outputs.append({"tool_call_id": tool.id, "output": str(function_response)})
                    # print(f"Output: {function_response}")
                except Exception as e:
                    function_response = str(e)
                    await cl.ErrorMessage(content=str(e)).send()
                    print(f"Error: {str(e)}")
                    self.current_step.is_error = True
                    tool_outputs.append({"tool_call_id": tool.id, "output": f"Error: {str(e)}"})

        # Submit all tool_outputs at the same time
        await self.submit_tool_outputs(tool_outputs, run_id)

    async def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        async with self.async_openai_client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(
                assistant_name=self.assistant_name,
                async_openai_client=self.async_openai_client,
            ),
        ) as stream:
            await stream.until_done()

    async def on_image_file_done(self, image_file):
        image_id = image_file.file_id
        response = await self.async_openai_client.files.with_raw_response.content(image_id)
        image_element = cl.Image(name=image_id, content=response.content, display="inline", size="large")
        if not self.current_message.elements:
            self.current_message.elements = []
        self.current_message.elements.append(image_element)
        await self.current_message.update()
